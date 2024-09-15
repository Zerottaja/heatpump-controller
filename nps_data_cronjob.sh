#!/bin/sh
#!/path/to/my/venv/bin/python3

# This cronjob should be configured in crontab to be run once a day
# after Nord Pool has published tomorrow's Spot price data:
#  0 18 *   *   *     /path/to/source/heatpump-controller/nps_data_cronjob.sh
python3 /path/to/my/nps_data_fetcher.py
