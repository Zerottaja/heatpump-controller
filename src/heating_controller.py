'''This module features the internal control algorithm for heating.
NPS data is required to be available for calculating heating control.'''
from os import path
import json
import configparser
from zoneinfo import ZoneInfo
from datetime import datetime
import light_logging as ll


_dir_path = path.dirname(path.abspath(__file__))
_conf = configparser.ConfigParser()
_conf.read(path.join(_dir_path, '..', 'config.ini'))


def __sort_and_short(dict_list):
    '''Sort daily electricity hour pricing, return list of cheapest hours and their prices.'''
    dict_list.sort(key = lambda k: k['price'])
    dict_list = dict_list[0:int(_conf['Heating']['heatinghours'])]
    return dict_list


def __hour_span_price(dict_list, start_hour):
    '''Calculate price sum of consecutive hours and arbitrary start point, return price'''
    price = 0
    for hour in range(start_hour, start_hour + int(_conf['Heating']['heatinghours'])):
        price += dict_list[hour]['price']
    return price


def __short_consecutive(dict_list):
    '''Loop over daily electricity pricing,
    return cheapest consecutive hours and their pricing'''
    cheapest_start = {'hour': 0, 'span_price': __hour_span_price(dict_list, 0)}
    loops = 24 - int(_conf['Heating']['heatinghours'])
    for start_hour in range(1, loops+1):
        span_price = __hour_span_price(dict_list, start_hour)
        if span_price < cheapest_start['span_price']:
            cheapest_start = {'hour': start_hour, 'span_price': span_price}
    return dict_list[cheapest_start['hour']:cheapest_start['hour'] \
           + int(_conf['Heating']['heatinghours'])]


def __get_hour_list(dict_list):
    '''Extract hours from dictionary list, return them as a list.'''
    hour_list = []
    hour_list_log = []
    for d in dict_list:
        hour_list.append(d['timestamp'])
        hour_list_log.append(datetime.fromtimestamp(d['timestamp'], \
                             ZoneInfo(_conf['NordPool']['timezone'])).strftime('%H'))
    ll.log(f'Selected hours: {str(hour_list_log)}')
    return hour_list


def calculate_control():
    '''Determine whether heating should be active right now, return boolean.'''
    ct = datetime.now(ZoneInfo(_conf['NordPool']['timezone']))
    date_str = ct.strftime('%Y-%m-%d')
    hour_timestamp = int(datetime(ct.year, ct.month, ct.day, ct.hour, \
                         0, 0, 0, ZoneInfo(_conf['NordPool']['timezone'])).timestamp())
    filename = path.join(_dir_path, '..', 'nps-data', 'nps_price_data_' + date_str + '.json')
    try:
        cheapest_hours = []
        with open(filename, mode='r', encoding="utf-8") as file:
            raw_data = json.load(file)
            if _conf.getboolean('Heating', 'consecutivehours'):
                cheapest_hours = __short_consecutive(raw_data['data'])
            else:
                cheapest_hours = __sort_and_short(raw_data['data'])
        return hour_timestamp in (__get_hour_list(cheapest_hours))
    except ValueError as err:
        ll.log(f'Error while calculating heating control: {err}')
        return False


if __name__ == '__main__':
    print(calculate_control())
