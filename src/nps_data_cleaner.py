'''This module cleans up old NPS data files from their directory.'''
import os
import configparser
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import light_logging as ll


_dir_path = os.path.dirname(os.path.abspath(__file__))
_conf = configparser.ConfigParser()
_conf.read(os.path.join(_dir_path, '..', 'config.ini'))


def delete_files_except(directory, files_to_keep):
    '''Iterate through every file in given directory, delete it if it's old.'''
    if not os.path.exists(directory):
        ll.log(f"The directory '{directory}' does not exist.")
        return

    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)

        # skip directories, only delete files
        if os.path.isfile(file_path):
            if file_path not in files_to_keep:
                try:
                    os.remove(file_path)
                    print(f"Deleted file: {file_path}")
                except Exception as e:
                    ll.log(f"Error deleting file {file_path}: {e}")
            else:
                ll.log(f"Skipped file: {file_path}")
        else:
            ll.log(f"Skipped directory: {file_path}")


if __name__ == '__main__':
    today = datetime.now(ZoneInfo(_conf['NordPool']['timezone']))
    data_dir_path =  os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), \
                     '..', 'nps-data'))
    today_data = os.path.join(data_dir_path, 'nps_price_data_' \
               + today.strftime('%Y-%m-%d')+'.json')
    tomorrow_data = os.path.join(data_dir_path, 'nps_price_data_' \
               + (today+timedelta(days=1)).strftime('%Y-%m-%d')+'.json')
    files_to_keep = [today_data, tomorrow_data]

    delete_files_except(data_dir_path, files_to_keep)
