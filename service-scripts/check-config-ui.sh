#!/bin/sh
# Check the heatpump config UI service and restart it if it has stopped.
# Intended to be called once a day from the root crontab.

SERVICE_NAME=${SERVICE_NAME:-heatpump-config-ui}
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

if service "$SERVICE_NAME" status >/dev/null 2>&1; then
    echo "$TIMESTAMP: $SERVICE_NAME is running."
    exit 0
fi

echo "$TIMESTAMP: $SERVICE_NAME is not running; restarting."
if ! service "$SERVICE_NAME" restart; then
    echo "$TIMESTAMP: Failed to restart $SERVICE_NAME." >&2
    exit 1
fi

if service "$SERVICE_NAME" status >/dev/null 2>&1; then
    echo "$TIMESTAMP: $SERVICE_NAME restarted successfully."
    exit 0
fi

echo "$TIMESTAMP: $SERVICE_NAME did not come back after restart." >&2
exit 1
