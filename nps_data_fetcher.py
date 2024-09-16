'''This module calls a Nord Pool Spot price API,
source of which is selected by configuration.'''
from os import path
import configparser
from datetime import datetime, timezone
import elering_api_interface


_dir_path = path.dirname(path.abspath(__file__))
_conf = configparser.ConfigParser()
_conf.read(path.join(_dir_path, 'config.ini'))


def __fetch_data():
    '''Call selected API interface to fetch tomorrow's Spot prices.
    Fetch today's too if necessary.'''
    # Check if today's data already exists or not
    date_str = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    filename = path.join(_dir_path, 'nps-data', 'nps_price_data_' + date_str + '.json')
    fetch_today_also = not path.isfile(filename)

    # Choose data source according to configuration file
    data_api = _conf['NordPool']['datasource']
    match data_api:
        case 'elering':
            elering_api_interface.fetch_nps_price_data(fetch_today_also)
        case _:
            print('Configured data source not available. Could not fetch NPS data.')


if __name__ == '__main__':
    __fetch_data()
