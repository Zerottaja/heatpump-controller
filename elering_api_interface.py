import configparser
import requests
import json
from datetime import datetime
from datetime import timezone
from datetime import timedelta

conf = configparser.ConfigParser()
conf.read('config.ini')


def fetch_nps_price_data(fetch_today_also=False):
    if(fetch_today_also):
        no_of_requests = 2
    else:
        no_of_requests = 1
    for i in range(no_of_requests):
        # Define the request URL, all times in UTC
        request_date_str = (datetime.now(timezone.utc) + \
                            timedelta(days=1-i)).strftime('%Y-%m-%d')
        start_param = request_date_str+'T00%3A00%3A00.000Z'
        end_param = request_date_str+'T23%3A59%3A59.999Z'
        url = 'https://dashboard.elering.ee/api/nps/price?start={}&end={}'\
              .format(start_param, end_param)

        # Fetch the JSON data from the URL
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            raw_data = json.loads(response.content)
            data_list = raw_data['data'][conf['DEFAULT']['pricearea']]
            clean_data = {'data': data_list}
            # Define the local file name to save the JSON data
            filename = './nps-data/nps_price_data_'+request_date_str+'.json'

            # Save the content to a local file
            with open(filename, 'w') as file:
                file.write(json.dumps(clean_data))

            print(f"NPS data successfully saved as {filename}")
        else:
            print(f"Failed to fetch JSON data. Status code: {response.status_code}")

    return


if __name__ == '__main__':
    fetch_nps_price_data(True)
