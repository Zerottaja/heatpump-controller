'''Unit tests for the manual override behaviour in main.py.'''
import configparser
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

import main  # pylint: disable=wrong-import-position


class ManualOverrideTests(unittest.TestCase):
    '''Test that manual override short-circuits the controller with a log entry.'''

    def test_manual_override_exits_and_logs(self):
        '''An enabled override returns early and logs the reason.'''
        config = configparser.ConfigParser()
        config.read_string('[Heating]\nmanualoverride = True\n')

        with mock.patch.object(main, '_conf', config), \
             mock.patch.object(main.ll, 'log') as log:
            result = main.main()

        self.assertEqual(result, 0)
        log.assert_called_once()
        self.assertIn('Manual override', log.call_args.args[0])

    def test_override_detection_defaults_to_false(self):
        '''Configs without the new key are treated as override disabled.'''
        config = configparser.ConfigParser()
        config.read_string('[Heating]\ncontrolsource = internal\n')

        self.assertFalse(main.manual_override_enabled(config))

    def test_override_detection_accepts_common_true_values(self):
        '''ConfigParser boolean values are interpreted correctly.'''
        config = configparser.ConfigParser()
        config.read_string('[Heating]\nmanualoverride = yes\n')

        self.assertTrue(main.manual_override_enabled(config))


if __name__ == '__main__':
    unittest.main()
