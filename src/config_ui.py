'''Small stdlib web server for editing non-credential config.ini values.'''
import argparse
import configparser
import json
import os
import stat
import sys
import tempfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

import light_logging as ll


ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / 'config.ini'
WEB_UI_DIR = Path(__file__).resolve().parent / 'web-ui'

ALLOWED_SECTIONS = {
    'Heating': [
        'ControlSource',
        'QuarterHourInterval',
        'HeatingHours',
        'ConsecutiveHours',
    ],
    'NordPool': [
        'DataSource',
        'PriceArea',
        'TimeZone',
    ],
    'Heatpump': [
        'TargetTemperature',
        'OperationMode',
        'FanSpeed',
        'VaneHorizontal',
        'VaneVertical',
    ],
    'SpotHinta': [
        'QuickCode',
    ],
}


def load_config(path):
    '''Read a config file and return its ConfigParser.'''
    config_path = Path(path)
    if not config_path.is_file():
        raise FileNotFoundError(
            f'Config file not found: {config_path}. '
            'Copy config.ini.example to config.ini first.'
        )
    config = configparser.ConfigParser()
    with open(config_path, mode='r', encoding='utf-8') as config_file:
        config.read_file(config_file)
    return config


def public_config(config):
    '''Return only the allowlisted settings, keyed by their config.ini names.'''
    result = {}
    for section, keys in ALLOWED_SECTIONS.items():
        if not config.has_section(section):
            continue
        values = {}
        for key in keys:
            option = key.lower()
            if config.has_option(section, option):
                values[key] = config.get(section, option, raw=True)
        result[section] = values
    return result


def apply_payload(path, payload):
    '''Merge allowlisted payload values into config and save it atomically.'''
    if not isinstance(payload, dict):
        raise ValueError('JSON payload must be an object.')

    config = load_config(path)
    incoming_sections = {}
    for section_name, values in payload.items():
        if isinstance(values, dict):
            incoming_sections[str(section_name).lower()] = values

    for section, keys in ALLOWED_SECTIONS.items():
        incoming = incoming_sections.get(section.lower())
        if incoming is None:
            continue
        incoming_keys = {str(key).lower(): value for key, value in incoming.items()}
        if not config.has_section(section):
            config.add_section(section)
        for key in keys:
            option = key.lower()
            if option in incoming_keys:
                config.set(section, option, str(incoming_keys[option]))

    _atomic_write(config, path)


def _atomic_write(config, path):
    '''Write config to a temporary file in the same directory, then replace.'''
    config_path = Path(path)
    original_mode = stat.S_IMODE(config_path.stat().st_mode)
    descriptor, temp_name = tempfile.mkstemp(
        prefix=f'.{config_path.name}.',
        suffix='.tmp',
        dir=config_path.parent,
    )
    try:
        with os.fdopen(descriptor, mode='w', encoding='utf-8') as temp_file:
            config.write(temp_file)
            temp_file.flush()
            os.fsync(temp_file.fileno())
        os.chmod(temp_name, original_mode)
        os.replace(temp_name, config_path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


class ConfigHandler(BaseHTTPRequestHandler):
    '''Serve static UI files and the config JSON API.'''

    # pylint: disable=invalid-name

    def _send_bytes(self, status, content_type, body):
        '''Send a complete response with the given body.'''
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, status, data):
        '''Send a JSON response.'''
        body = json.dumps(data).encode('utf-8')
        self._send_bytes(status, 'application/json; charset=utf-8', body)

    def _serve_file(self, filename, content_type):
        '''Serve one whitelisted file from the web-ui directory.'''
        file_path = WEB_UI_DIR / filename
        if not file_path.is_file():
            self._send_json(404, {'status': 'error', 'message': 'File not found.'})
            return
        self._send_bytes(200, content_type, file_path.read_bytes())

    def do_GET(self):
        '''Handle page, asset, and config read requests.'''
        route = urlparse(self.path).path
        if route in ('/', '/index.html'):
            self._serve_file('index.html', 'text/html; charset=utf-8')
        elif route == '/styles.css':
            self._serve_file('styles.css', 'text/css; charset=utf-8')
        elif route == '/app.js':
            self._serve_file('app.js', 'application/javascript; charset=utf-8')
        elif route == '/api/config':
            try:
                config = load_config(CONFIG_PATH)
            except (OSError, configparser.Error) as err:
                self._send_json(400, {'status': 'error', 'message': str(err)})
            else:
                self._send_json(200, public_config(config))
        else:
            self._send_json(404, {'status': 'error', 'message': 'Not found.'})

    def do_POST(self):
        '''Handle config save requests.'''
        if urlparse(self.path).path != '/api/config':
            self._send_json(404, {'status': 'error', 'message': 'Not found.'})
            return
        try:
            length = int(self.headers.get('Content-Length', 0))
            if length <= 0:
                raise ValueError('Empty request body.')
            payload = json.loads(self.rfile.read(length).decode('utf-8'))
            apply_payload(CONFIG_PATH, payload)
        except FileNotFoundError as err:
            self._send_json(400, {'status': 'error', 'message': str(err)})
        except (ValueError, configparser.Error, OSError) as err:
            self._send_json(400, {'status': 'error', 'message': str(err)})
        else:
            self._send_json(200, {'status': 'ok'})

    def log_message(self, fmt, *args):  # pylint: disable=arguments-differ
        '''Route HTTP request logs through the project logger.'''
        ll.log(fmt % args)


def parse_args(argv=None):
    '''Parse command line arguments.'''
    parser = argparse.ArgumentParser(description='Serve the heatpump config editor.')
    parser.add_argument('--host', default='127.0.0.1',
                        help='Address to bind to (default: 127.0.0.1).')
    parser.add_argument('--port', type=int, default=8000,
                        help='Port to listen on (default: 8000).')
    return parser.parse_args(argv)


def main(argv=None):
    '''Run the config web server until interrupted.'''
    args = parse_args(argv)
    if not CONFIG_PATH.is_file():
        ll.log(f'WARNING: {CONFIG_PATH} not found; copy config.ini.example to config.ini.')
    with ThreadingHTTPServer((args.host, args.port), ConfigHandler) as server:
        ll.log(f'Serving config UI at http://{args.host}:{args.port}/')
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            ll.log('Shutting down config UI.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
