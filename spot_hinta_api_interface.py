'''This module calls an external Spot-hinta.fi API for heating control.
Using this control source is independant from NPS data fetching.'''
from os import path
import requests
import configparser
import melcloud_interface


_dir_path = path.dirname(path.abspath(__file__))
_conf = configparser.ConfigParser()
_conf.read(path.join(_dir_path, 'config.ini'))


def fetch_control():
    '''Call Spot-hinta.fi API and return heating control boolean.'''
    url = 'https://api.spot-hinta.fi/QuickCode/{}' \
          .format(_conf['SpotHinta']['quickcode'])

    try:
        # Fetch control from the URL
        response = requests.get(url, timeout=10)

        # Check if the request was successful
        state = response.status_code == 200
        print('Spot-hinta API recommends setting heating state to {}'.format(state))
    except Exception as err:
        print(err)
        print('Fetching Spot-hinta API control failed. Deactivating heatpump')
        state = False

    return state


if __name__ == '__main__':
    fetch_control()
