# heatpump-controller
[![Pylint](https://github.com/Zerottaja/heatpump-controller/actions/workflows/pylint.yml/badge.svg?branch=master)](https://github.com/Zerottaja/heatpump-controller/actions/workflows/pylint.yml)

Home automation project meant to control Mitsubishi Electric heatpump according to Nordpool Spot electricity pricing.

## Setup
- I highly recommend installing a python virtual environment for running this project.
- Install library requirements with `/path/to/my/venv/bin/pip3 install -r requirements.txt`
- Add tasks to crontab (or your other favourite task scheduler). Main script should run hourly just after hour change and NPS (Nord Pool Spot) data fetcher should run just once per day after the data has been published. Configure the paths according to your liking:
```
1 * * * * /path/to/my/venv/bin/python3 /path/to/my/heatpump-controller/src/main.py >> /path/to/my/logs/cron.log 2>&1
0 18 * * * /path/to/my/venv/bin/python3 /path/to/my/heatpump-controller/src/nps_data_fetcher.py >> /path/to/my/logs/cron.log 2>&1

```
- Install submodule `pymelcloud` according to it's instructions
- Configure `config.ini.example` to your liking and save it as `config.ini`

## Data sources
Configuration file `config.ini` allows the user to select which source API should be used for fetching Nord Pool Spot electricity prices. Currently only option is Estonian national grid's Elering LIVE API

## Control sources
Configuration file `config.ini` also allows the user to select which source should be used for determining automatic control for heating. Default option is to use the internal control algorithm but an external control source through spot-hinta.fi API is also available. 
