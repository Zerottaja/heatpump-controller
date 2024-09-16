'''This module calls an external Spot-hinta.fi API for heating control.
Using this control source is independant from NPS data fetching.'''
from os import path
import configparser
import requests
import light_logging


_dir_path = path.dirname(path.abspath(__file__))
_conf = configparser.ConfigParser()
_conf.read(path.join(_dir_path, '..', 'config.ini'))


def fetch_control():
    '''Call Spot-hinta.fi API and return heating control boolean.'''
    url = f"https://api.spot-hinta.fi/QuickCode/{_conf['SpotHinta']['quickcode']}"

    try:
        # Fetch control from the URL
        response = requests.get(url, timeout=10)

        # Check if the request was successful
        state = response.status_code == 200
        light_logging.log(f'Spot-hinta API recommends setting heating state to {state}.')
    except ConnectionError as err:
        light_logging.log(err)
        light_logging.log('Fetching Spot-hinta API control failed. '
                          + 'Recommend setting heating state to False.')
        state = False

    return state


if __name__ == '__main__':
    fetch_control()
