import requests
import melcloud_interface


def fetch_control()
    # Select Quick Code according to Spot-hinta API documentation at
    # https://spot-hinta.fi/pikakoodit/
    quick_code = 125

    # Define the URL
    url = 'https://api.spot-hinta.fi/QuickCode/{}'.format(quick_code)

    try:
        # Fetch control from the URL
        response = requests.get(url, timeout=10)

        # Check if the request was successful
        state = response.status_code == 200
        print('Setting heatpump state to {}'.format(state))
    except Exception as err:
        print(err)
        print('Fetching Spot-hinta API control failed. Deactivating heatpump')
        state = False

    return state
