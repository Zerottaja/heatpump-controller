'''This module features the internal control algorithm for heating.
NPS data is required to be available for calculating heating control.'''
from os import path
import json
import configparser
from datetime import datetime, timezone


_dir_path = path.dirname(path.abspath(__file__))
_conf = configparser.ConfigParser()
_conf.read(path.join(_dir_path, 'config.ini'))


def __sort_and_short(dict_list):
    '''Sort daily electricity hour pricing, return list of cheapest hours and their prices.'''
    dict_list.sort(key = lambda k: k['price'])
    dict_list = dict_list[0:int(_conf['Heating']['heatinghours'])]
    return dict_list


def __get_hour_list(dict_list):
    '''Extract hours from dictionary list, return them as a list.'''
    hour_list = []
    for d in dict_list:
        hour_list.append(d['timestamp'])
    return hour_list


def calculate_control():
    '''Determine whether heating should be active right now, return boolean.'''
    ct = datetime.now(timezone.utc)
    date_str = ct.strftime('%Y-%m-%d')
    hour_timestamp = int(datetime(ct.year, ct.month, ct.day, ct.hour, \
                         0, 0, 0, timezone.utc).timestamp())
    filename = path.join(_dir_path, 'nps-data', 'nps_price_data_' + date_str + '.json')
    try:
        cheapest_hours = []
        with open(filename, mode='r', encoding="utf-8") as file:
            raw_data = json.load(file)
            cheapest_hours = __sort_and_short(raw_data['data'])
        return hour_timestamp in (__get_hour_list(cheapest_hours))
    except ValueError as err:
        print(f'Error while calculating heating control: {err}')
        return False


if __name__ == '__main__':
    print(calculate_control())
