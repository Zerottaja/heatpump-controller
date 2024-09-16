'''This module simply wraps current time to console outputs that can
then be piped anywhere the user desires.'''
from datetime import datetime, timezone


def log(message):
    '''Add current local time to message, print it.'''
    print(datetime.now().strftime('%Y-%m-%d %H:%M:%S: ') + message)


if __name__ == '__main__':
    log('Hello, world! This is a sample log entry.')
