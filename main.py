import sys
import configparser
import spot_hinta_api_interface
import melcloud_interface
import heating_controller

conf = configparser.ConfigParser()
conf.read('config.ini')


def main():
    match conf['Heating']['controlsource']:
        case 'spot-hinta':
            heatpump_request = spot_hinta_api_interface.fetch_control()
        case 'internal':
            heatpump_request = heating_controller.calculate_control()
    melcloud_interface.set_heatpump_state(heatpump_request)

    return

if __name__ == "__main__":
    sys.exit(main())
