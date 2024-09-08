import sys
import spot_hinta_api_interface
import melcloud_interface

def main():
    heatpump_request = spot_hinta_api_interface.fetch_control()
    melcloud_interface.set_heatpump_state(heatpump_request)

    return

if __name__ == "__main__":
    sys.exit(main())
