# heatpump-controller
[![Pylint](https://github.com/Zerottaja/heatpump-controller/actions/workflows/pylint.yml/badge.svg?branch=master)](https://github.com/Zerottaja/heatpump-controller/actions/workflows/pylint.yml)

Home automation project meant to control Mitsubishi Electric heatpump according to Nordpool Spot electricity pricing.
Supports quarter hour control interval or hourly interval.

## Setup
- I highly recommend installing a python virtual environment for running this project.
- Install library requirements with `/path/to/my/venv/bin/pip3 install -r requirements.txt`
- Add tasks to crontab (or your other favourite task scheduler). Main script should run hourly just after hour change and NPS (Nord Pool Spot) data fetcher should run just once per day after the data has been published. Configure the paths according to your liking:
```
0,15,30,45 * * * * /path/to/my/venv/bin/python3 /path/to/my/heatpump-controller/src/main.py >> /path/to/my/logs/cron.log 2>&1
0 18 * * * /path/to/my/venv/bin/python3 /path/to/my/heatpump-controller/src/nps_data_fetcher.py >> /path/to/my/logs/cron.log 2>&1
0 12 * * 1 /path/to/my/venv/bin/python3 /path/to/my/heatpump-controller/src/nps_data_cleaner.py >> /path/to/my/logs/cron.log 2>&1

```
- Install submodule `pymelcloud` according to it's instructions
- Configure `config.ini.example` to your liking and save it as `config.ini`

## Web config UI
A small browser UI is available for editing the non-credential settings in `config.ini`.

```bash
python3 src/config_ui.py
# open http://127.0.0.1:8000
```

By default the server binds only to localhost. Use `--host` and `--port` to change this:

```bash
python3 src/config_ui.py --host 0.0.0.0 --port 8000
```

Do not expose the UI to the local network until you have reviewed the network and security
setup. The intended follow-up is documented in `WEB_UI_PLAN.md`.

`config.ini` must already exist (copy `config.ini.example` during setup). Credentials are never
shown in the UI or included in its API responses, and they are preserved when settings are saved.
Fields with predefined options are shown as dropdowns; other fields remain free text. Cron jobs
read `config.ini` when each process starts, so saved changes apply on the next scheduled run.

The **Manual override** switch sets `[Heating] ManualOverride`. When it is true, `main.py` logs the
reason and exits before fetching prices, choosing heating hours, or contacting MELCloud, leaving the
heat pump state unchanged.

Run the tests with:

```bash
python3 -m unittest discover -s tests
```

### Running as a service
An init.d-style service script is provided in `service-scripts/`. Bookworm uses systemd, but SysV
scripts in `/etc/init.d/` are still supported through `service` and `systemctl`.

Install it as root:

```bash
sudo cp service-scripts/heatpump-config-ui /etc/init.d/heatpump-config-ui
sudo chmod 755 /etc/init.d/heatpump-config-ui
sudo update-rc.d heatpump-config-ui defaults
sudo service heatpump-config-ui start
```

By default it runs as user `pi`, listens on `127.0.0.1:8000`, and logs to
`/var/log/heatpump-config-ui.log`. To listen on the LAN, create `/etc/default/heatpump-config-ui`
with `HOST=0.0.0.0` (or the Pi's LAN address); see `service-scripts/README.md` for all options.

A health-check script can be run daily from the **root** crontab to restart the UI if it has
stopped:

```bash
sudo crontab -e
# add:
0 6 * * * /path/to/my/heatpump-controller/service-scripts/check-config-ui.sh >> /var/log/heatpump-config-ui-cron.log 2>&1
```

## Data sources
Configuration file `config.ini` allows the user to select which source API should be used for fetching Nord Pool Spot electricity prices. Currently only option is Estonian national grid's Elering LIVE API

## Control sources
Configuration file `config.ini` also allows the user to select which source should be used for determining automatic control for heating. Default option is to use the internal control algorithm but an external control source through spot-hinta.fi API is also available. 
