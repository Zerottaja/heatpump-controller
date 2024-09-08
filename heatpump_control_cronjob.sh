#!/bin/sh
#!/home/pi/src/heatpump-controller/venv/bin/python3

# this cronjob should be configured in crontask to be run hourly:
#  1 *  *   *   *     /path/to/source/heatpump-controller/heatpump_control_cronjob.sh
python3 /home/pi/src/heatpump-controller/main.py
