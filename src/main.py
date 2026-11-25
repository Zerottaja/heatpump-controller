'''Main module of the heatpump controller. Calls configured source to control heatpump.'''
from os import path
import sys
import configparser
import light_logging as ll


_dir_path = path.dirname(path.abspath(__file__))
_conf = configparser.ConfigParser()
_conf.read(path.join(_dir_path, '..', 'config.ini'))


def manual_override_enabled(config):
    '''Return True when manual override is enabled in the configuration.'''
    return config.getboolean('Heating', 'manualoverride', fallback=False)


def main():
    '''Select control source according to config and call MELCloud interface.'''
    if manual_override_enabled(_conf):
        ll.log('Manual override enabled. Exiting without changing heat pump state.')
        return 0

    # Imported only after the override check so an override does not load cloud libraries.
    import heating_controller  # pylint: disable=import-outside-toplevel
    import spot_hinta_api_interface  # pylint: disable=import-outside-toplevel
    import melcloud_interface  # pylint: disable=import-outside-toplevel

    match _conf['Heating']['controlsource']:
        case 'spot-hinta':
            heatpump_request = spot_hinta_api_interface.fetch_control()
        case 'internal':
            heatpump_request = heating_controller.calculate_control()
    melcloud_interface.set_heatpump_state(heatpump_request)
    return 0


if __name__ == "__main__":
    sys.exit(main())
