'''This module calls Estonian national grid Elering's LIVE API
and fetches Nord Pool Spot electricity prices.'''
from os import path
import configparser
import json
from datetime import datetime
from datetime import timezone
from datetime import timedelta
import requests


_dir_path = path.dirname(path.abspath(__file__))
_conf = configparser.ConfigParser()
_conf.read(path.join(_dir_path, 'config.ini'))


def fetch_nps_price_data(fetch_today_also=False):
    '''Make API call, save Nord Pool Spot data to a JSON file.'''
    if fetch_today_also:
        no_of_requests = 2
    else:
        no_of_requests = 1
    for i in range(no_of_requests):
        # Define the request URL, all times in UTC
        request_date_str = (datetime.now(timezone.utc) + \
                            timedelta(days=1-i)).strftime('%Y-%m-%d')
        start_param = request_date_str+'T00%3A00%3A00.000Z'
        end_param = request_date_str+'T23%3A59%3A59.999Z'
        url = f'https://dashboard.elering.ee/api/nps/price?start={start_param}&end={end_param}'

        # Fetch the JSON data from the URL
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            raw_data = json.loads(response.content)
            data_list = raw_data['data'][_conf['NordPool']['pricearea']]
            clean_data = {'data': data_list}
            # Define the local file name to save the JSON data
            filename = path.join(_dir_path, 'nps-data', 'nps_price_data_'+request_date_str+'.json')

            # Save the content to a local file
            with open(filename, 'w', encoding="utf-8") as file:
                file.write(json.dumps(clean_data))

            print(f"NPS data successfully saved as {filename}")
        else:
            print(f"Failed to fetch JSON data. Status code: {response.status_code}")


if __name__ == '__main__':
    fetch_nps_price_data(True)
