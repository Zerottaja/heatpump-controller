'''This module calls Estonian national grid Elering's LIVE API
and fetches Nord Pool Spot electricity prices.'''
from os import path
import configparser
import json
from datetime import datetime
from zoneinfo import ZoneInfo
from datetime import timedelta
import requests
import light_logging


_dir_path = path.dirname(path.abspath(__file__))
_conf = configparser.ConfigParser()
_conf.read(path.join(_dir_path, '..', 'config.ini'))


def fetch_nps_price_data(fetch_today_also):
    '''Make API call, save Nord Pool Spot data to a JSON file.'''
    ct_local = datetime.now(ZoneInfo(_conf['NordPool']['timezone']))
    if fetch_today_also:
        no_of_requests = 2
    else:
        no_of_requests = 1
    for i in range(no_of_requests):
        # Define the request URL, Elering API requires UTC time
        request_date_local = ct_local + timedelta(days=1-i)
        start_time_local = datetime(year=request_date_local.year, \
                                    month=request_date_local.month, \
                                    day=request_date_local.day, hour=0, minute=0)
        end_time_local = datetime(year=request_date_local.year, \
                                  month=request_date_local.month, \
                                  day=request_date_local.day, hour=23, minute=30)
        start_time_utc = start_time_local - request_date_local.utcoffset()
        end_time_utc = end_time_local - request_date_local.utcoffset()
        start_param = start_time_utc.strftime('%Y-%m-%dT%H:%M:%S.000Z')
        start_param = start_param.replace(':', '%3A')
        end_param = end_time_utc.strftime('%Y-%m-%dT%H:%M:%S.000Z')
        end_param = end_param.replace(':', '%3A')
        url = f'https://dashboard.elering.ee/api/nps/price?start={start_param}&end={end_param}'
        # Fetch the JSON data from the URL
        response = requests.get(url, timeout=10)

        # Check if the request was successful
        if response.status_code == 200:
            raw_data = json.loads(response.content)
            data_list = raw_data['data'][_conf['NordPool']['pricearea']]
            clean_data = {'data': data_list}
            # Define the local file name to save the JSON data
            filename = path.join(_dir_path, '..', 'nps-data', \
                       'nps_price_data_'+request_date_local.strftime('%Y-%m-%d')+'.json')

            # Save the content to a local file
            with open(filename, 'w', encoding="utf-8") as file:
                file.write(json.dumps(clean_data))

            light_logging.log(f"NPS data successfully saved as {filename}")
        else:
            light_logging.log(f"Failed to fetch JSON data. Status code: {response.status_code}")


if __name__ == '__main__':
    fetch_nps_price_data(True)
