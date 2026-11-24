'''Unit tests for the config UI merge logic.'''
import os
import shutil
import stat
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

import config_ui  # pylint: disable=wrong-import-position


SAMPLE_CONFIG = '''[Heating]
ControlSource = internal
QuarterHourInterval = True
HeatingHours = 12
ConsecutiveHours = False

[NordPool]
DataSource = elering
PriceArea = fi
TimeZone = Europe/Helsinki

[Heatpump]
TargetTemperature = 23
OperationMode = heat
FanSpeed = 4
VaneHorizontal = swing
VaneVertical = swing

[SpotHinta]
QuickCode = 125

[Credentials]
MELCloudEmail = user@example.com
MELCloudPassword = secret
'''


class ConfigUiTests(unittest.TestCase):
    '''Test allowlisting and credential preservation when saving config.'''

    def setUp(self):
        '''Create a temporary config file for each test.'''
        temp_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, temp_dir)
        self.config_path = Path(temp_dir) / 'config.ini'
        self.config_path.write_text(SAMPLE_CONFIG, encoding='utf-8')

    def test_credentials_survive_payload(self):
        '''Injected credentials and unknown sections are ignored.'''
        payload = {
            'Heating': {'ControlSource': 'spot-hinta'},
            'Credentials': {'MELCloudEmail': 'attacker@example.com'},
            'Evil': {'Power': 'on'},
        }
        config_ui.apply_payload(self.config_path, payload)

        config = config_ui.load_config(self.config_path)
        self.assertEqual(config.get('Credentials', 'melcloudemail'), 'user@example.com')
        self.assertEqual(config.get('Credentials', 'melcloudpassword'), 'secret')
        self.assertFalse(config.has_section('Evil'))
        self.assertEqual(config.get('Heating', 'controlsource'), 'spot-hinta')

    def test_unknown_keys_are_ignored(self):
        '''Keys outside the allowlist do not appear in the saved file.'''
        config_ui.apply_payload(
            self.config_path,
            {'Heating': {'Bogus': 'value', 'HeatingHours': '8'}},
        )

        config = config_ui.load_config(self.config_path)
        self.assertFalse(config.has_option('Heating', 'bogus'))
        self.assertEqual(config.get('Heating', 'heatinghours'), '8')

    def test_public_config_omits_credentials(self):
        '''The read API never exposes the Credentials section.'''
        public = config_ui.public_config(config_ui.load_config(self.config_path))

        self.assertNotIn('Credentials', public)
        self.assertEqual(public['Heating']['ControlSource'], 'internal')
        self.assertEqual(public['SpotHinta']['QuickCode'], '125')

    def test_missing_config_raises_clear_error(self):
        '''A missing config file produces an actionable error message.'''
        missing = self.config_path.parent / 'missing.ini'

        with self.assertRaises(FileNotFoundError) as context:
            config_ui.apply_payload(missing, {'Heating': {'HeatingHours': '8'}})

        self.assertIn('config.ini.example', str(context.exception))

    def test_file_mode_is_preserved(self):
        '''Atomic replacement keeps the original file permissions.'''
        os.chmod(self.config_path, 0o600)

        config_ui.apply_payload(self.config_path, {'Heating': {'HeatingHours': '8'}})

        self.assertEqual(stat.S_IMODE(self.config_path.stat().st_mode), 0o600)


if __name__ == '__main__':
    unittest.main()
