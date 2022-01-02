# pms5003-logger

Raspberry Pi air pollution logger using [PMS5003](https://shop.pimoroni.com/products/pms5003-particulate-matter-sensor-with-cable).
A quick project over the Christmas break, so rough around the edges!

## Install and deploy

I'm running Raspbian 10 on a Raspberry Pi (1) Model B. `pip` is slow, but works.

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

## Viewing the data

I SSH into the Pi and get the readings by querying the SQLite database.
There's a view called `summary` which shows the 30 minute average PM1.0, PM2.5 and PM10.0 concentration.

```
$ sqlite3 -header -column pms5003.db 'select * from summary'
timestamp                   PM1.0_30min_avg  PM2.5_30min_avg  PM10.0_30min_avg
--------------------------  ---------------  ---------------  ----------------
2022-01-01 14:02:05.613893  4.0              6.0              6.0
```

I tried building a Flask app to display a matplotlib graph, but had trouble installing numpy on my old Pi and not enough time to fix it.
