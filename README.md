# pms5003-logger

Raspberry Pi air pollution logger using [PMS5003](https://shop.pimoroni.com/products/pms5003-particulate-matter-sensor-with-cable).

## Install and deploy

I'm running Raspbian 10 on a Model B.

```
pip3 install --upgrade git+https://github.com/tomwphillips/pms5003-logger.git
```

Set up the SQLite database:

```
python3 -m pms5003logger --create-table ~/pms5003.db
```

Then I added it to my cron jobs (`crontab -e`) to run every minute:

```
* * * * * python3 -m pms5003logger ~/pms5003.db
```