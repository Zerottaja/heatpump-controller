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


def __sort_and_short(dict_list, quarter_interval):
    '''Sort daily electricity time pricing, return list of cheapest times and their prices.'''
    item_count = 0
    if quarter_interval:
        item_count = 4*int(_conf['Heating']['heatinghours'])
    else:
        item_count = int(_conf['Heating']['heatinghours'])
        for i in range(0, 24):
            dict_list[i]['price'] = (dict_list[i]['price'] + dict_list[i+1]['price'] + \
                                     dict_list[i+2]['price'] + dict_list[i+3]['price']) / 4
            for _ in range(0,3):
                dict_list.pop(i+1)
    dict_list.sort(key = lambda k: k['price'])
    dict_list = dict_list[0:item_count]
    return dict_list


def __time_span_price(dict_list, start_hour, start_quarter, hours, quarters):
    '''Calculate price sum of a continuous timespan at arbitrary start point, return price'''
    price = 0
    for quarter in range(4*start_hour + start_quarter, 4*start_hour + start_quarter + \
                         4*hours + quarters):
        price += dict_list[quarter]['price']
    return price


def __short_consecutive(dict_list):
    '''Loop over daily electricity pricing,
    return cheapest consecutive quarters and their pricing'''
    heating_hours = int(_conf['Heating']['heatinghours'])
    cheapest_start = {'quarter': 0, 'span_price': \
                      __time_span_price(dict_list, 0, 0, heating_hours, 0)}
    loops = 96 - 4*heating_hours
    for start_quarter in range(4, loops+1):
        start_hour = int((start_quarter - start_quarter % 4) / 4)
        quarter_of_start_hour = start_quarter % 4
        span_price = __time_span_price(dict_list, start_hour, \
                                       quarter_of_start_hour, heating_hours, 0)
        if span_price < cheapest_start['span_price']:
            cheapest_start = {'quarter': start_quarter, 'span_price': span_price}
    return dict_list[cheapest_start['quarter']:cheapest_start['quarter'] + 4*heating_hours]


def __get_times_list(dict_list):
    '''Extract times from dictionary list, return them as a list.'''
    time_list = []
    time_list_log = []
    for d in dict_list:
        time_list.append(d['timestamp'])
        time_list_log.append(datetime.fromtimestamp(d['timestamp'], \
                             ZoneInfo(_conf['NordPool']['timezone'])).strftime('%H:%M'))
    ll.log(f'Selected times: {str(time_list_log)}')
    return time_list


def calculate_control():
    '''Determine whether heating should be active right now, return boolean.'''
    ct = datetime.now(ZoneInfo(_conf['NordPool']['timezone']))
    date_str = ct.strftime('%Y-%m-%d')
    quarter_interval = _conf.getboolean('Heating', 'quarterhourinterval')
    if quarter_interval:
        current_quarter = ct.minute - (ct.minute % 15)
    else:
        current_quarter = 0
    current_timestamp = int(datetime(ct.year, ct.month, ct.day, ct.hour, \
                         current_quarter, 0, 0, \
                         ZoneInfo(_conf['NordPool']['timezone'])).timestamp())
    filename = path.join(_dir_path, '..', 'nps-data', 'nps_price_data_' + date_str + '.json')
    try:
        cheapest_times = []
        with open(filename, mode='r', encoding="utf-8") as file:
            raw_data = json.load(file)
            if _conf.getboolean('Heating', 'consecutivehours'):
                cheapest_times = __short_consecutive(raw_data['data'])
            else:
                cheapest_times = __sort_and_short(raw_data['data'], quarter_interval)
        return current_timestamp in (__get_times_list(cheapest_times))
    except ValueError as err:
        ll.log(f'Error while calculating heating control: {err}')
        return False


if __name__ == '__main__':
    print(calculate_control())
