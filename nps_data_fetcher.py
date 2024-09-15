from os import path
import configparser
import elering_api_interface
from datetime import datetime, timezone


dir_path = path.dirname(path.abspath(__file__))
conf = configparser.ConfigParser()
conf.read(path.join(dir_path, 'config.ini'))


def __fetch_data():
    # Check if today's data already exists or not
    date_str = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    filename = path.join(dir_path, 'nps-data', 'nps_price_data_' + date_str + '.json')
    fetch_today_also = not path.isfile(filename)

    # Choose data source according to configuration file
    data_api = conf['NordPool']['datasource']
    match data_api:
        case 'elering':
            elering_api_interface.fetch_nps_price_data(fetch_today_also)
        case _:
            print('Configured data source not available. Could not fetch NPS data.')


if __name__ == '__main__':
    __fetch_data()
