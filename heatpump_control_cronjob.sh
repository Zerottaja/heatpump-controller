#!/bin/sh
#!/home/pi/src/heatpump-controller/venv/bin/python3

# this cronjob should be configured in crontab to be run hourly:
#  1 *  *   *   *     /path/to/source/heatpump-controller/heatpump_control_cronjob.sh
python3 ./main.py
