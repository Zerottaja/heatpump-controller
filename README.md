# heatpump-controller
Home automation project meant to control Mitsubishi Electric heatpump according to Nordpool Spot electricity pricing.

## Setup
- I highly recommend installing a python virtual environment for running this project. After installation, please modify the shebangs in cronjob shell scripts `heatpump_control_cronjob.sh` and `nps_data_cronjob.sh` to match your virtual environments path.
- Add cronjob scripts to crontab (or your other favourite task scheduler) as detailed in each individual cronjob
- Install submodule `pymelcloud` according to it's instructions
- Configure `config.ini.example` to your liking and save it as `config.ini`

## Data sources
Configuration file `config.ini` allows the user to select which source API should be used for fetching Nord Pool Spot electricity prices. Currently only option is Estonian national grid's Elering LIVE API

## Control sources
Configuration file `config.ini` also allows the user to select which source should be used for determining automatic control for heating. Default option is to use the internal control algorithm but an external control source through spot-hinta.fi API is also available. 
