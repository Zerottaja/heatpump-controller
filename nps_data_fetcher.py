import os.path
import configparser
import elering_api_interface
from datetime import datetime, timezone


conf = configparser.ConfigParser()
conf.read('config.ini')


def __fetch_data():
    # Check if today's data already exists or not
    date_str = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    filename = './nps-data/nps_price_data_'+date_str+'.json'
    fetch_today_also = not os.path.isfile(filename)

    # Choose data source according to configuration file
    data_api = conf['NordPool']['datasource']
    match data_api:
        case 'elering':
            elering_api_interface.fetch_nps_price_data(fetch_today_also)
        case _:
            print('Configured data source not available. Could not fetch NPS data.')


if __name__ == '__main__':
    __fetch_data()
