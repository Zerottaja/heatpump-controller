import json
import configparser
from datetime import datetime, timezone


conf = configparser.ConfigParser()
conf.read('config.ini')


def __sort_and_short(dict_list):
    dict_list.sort(key = lambda k: k['price'])
    dict_list = dict_list[0:int(conf['DEFAULT']['heatinghours'])]
    return dict_list


def __get_hour_list(dict_list):
    hour_list = []
    for d in dict_list:
        hour_list.append(d['timestamp'])
    return hour_list


def calculate_control():
    ct = datetime.now(timezone.utc)
    date_str = ct.strftime('%Y-%m-%d')
    hour_timestamp = int(datetime(ct.year, ct.month, ct.day, ct.hour, \
                         0, 0, 0, timezone.utc).timestamp())
    filename = './nps-data/nps_price_data_' + date_str + '.json'
    try:
        cheapest_hours = []
        with open(filename, mode='r') as file:
            raw_data = json.load(file)
            cheapest_hours = __sort_and_short(raw_data['data'])
        if hour_timestamp in (__get_hour_list(cheapest_hours)):
            return True
        else:
            return False
    except ValueError as err:
        print('Error while calculating heating control: {}'.format(err))


if __name__ == '__main__':
    print(calculate_control())
