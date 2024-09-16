'''Main module of the heatpump controller. Calls configured source to control heatpump.'''
from os import path
import sys
import configparser
import spot_hinta_api_interface
import melcloud_interface
import heating_controller

_dir_path = path.dirname(path.abspath(__file__))
_conf = configparser.ConfigParser()
_conf.read(path.join(_dir_path, '..', 'config.ini'))


def main():
    '''Select control source according to config and call MELCloud interface.'''
    match _conf['Heating']['controlsource']:
        case 'spot-hinta':
            heatpump_request = spot_hinta_api_interface.fetch_control()
        case 'internal':
            heatpump_request = heating_controller.calculate_control()
    melcloud_interface.set_heatpump_state(heatpump_request)


if __name__ == "__main__":
    sys.exit(main())
