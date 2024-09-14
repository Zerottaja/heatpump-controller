#!/bin/sh
#!/path/to/my/venv/bin/python3

# this cronjob should be configured in crontab to be run hourly one minute after hour change:
#  1 *  *   *   *     /path/to/source/heatpump-controller/heatpump_control_cronjob.sh
python3 ./main.py
