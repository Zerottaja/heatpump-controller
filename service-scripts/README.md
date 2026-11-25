# Service scripts

Helpers for running the config UI as a service on Raspberry Pi OS Bookworm.

- `heatpump-config-ui` — SysV `init.d` service script. Copy it to `/etc/init.d/heatpump-config-ui`.
- `check-config-ui.sh` — cron-friendly health check. It uses `service heatpump-config-ui status`
  and restarts the service if it is not running.

See the main `README.md` for installation commands and the crontab example.

## Configuration

The service reads optional overrides from `/etc/default/heatpump-config-ui`:

```sh
APP_DIR=/path/to/my/heatpump-controller
PYTHON=/usr/bin/python3
RUNAS=pi
HOST=127.0.0.1
PORT=8000
PIDFILE=/run/heatpump-config-ui.pid
LOGFILE=/var/log/heatpump-config-ui.log
```

`HOST` defaults to `127.0.0.1`. Set it to the Pi's LAN address or `0.0.0.0` before accessing the UI
from another device. Keep in mind that the UI has no authentication; see the main README.
