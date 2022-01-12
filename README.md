# rpi-iaq

Indoor air quality measurement on Raspberry Pi:

* PM1.0, PM2.5 and PM10.0 concentrations
* CO2 concentration
* Temperature
* Relative humidity

This began as quick project over the Christmas break, so it's rough around the edges.

## Sensors

* [PMS5003 particulate matter sensor](https://shop.pimoroni.com/products/pms5003-particulate-matter-sensor-with-cable)
* [SCD-40 CO2, temperature and humidity sensor](https://shop.pimoroni.com/products/adafruit-scd-40-true-co2-temperature-and-humidity-sensor-stemma-qt-qwiic)

Follow the instructions to hook them up to the GPIO pins.

## Install and deploy

I'm running Raspbian 10 on a Raspberry Pi (1) Model B. `pip` is slow, but works.

You need to [install Adafruit Blinka](https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/installing-circuitpython-on-raspberry-pi):

```
sudo pip3 install --upgrade adafruit-python-shell
wget https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/raspi-blinka.py
sudo python3 raspi-blinka.py
```

Eventually the Pi will restart and you can check I2C is enabled:

```
$ ls /dev/i2c*
/dev/i2c-1  /dev/i2c-2
```

Install this package:

```
pip3 install --upgrade git+https://github.com/tomwphillips/iaq.git
```

Set up the SQLite database table and record your first measurements:

```
python3 -m iaq.logger --create-table ~/iaq.db
```

If you only have one of the sensors, you can disable the missing one using `--disable-pms` or `--disable-scd`.

I added it to my cron jobs (`crontab -e`) to run every minute:

```
* * * * * python3 -m iaq.logger ~/iaq.db
```

## Viewing the data

### Quick checks

I SSH into the Pi and get the readings by querying the SQLite database.
There's a view called `summary` which shows the 30 minute average PM1.0, PM2.5 and PM10.0 concentration.

```
$ sqlite3 -header -column pms5003.db 'select * from summary'
timestamp                   PM1.0_30min_avg  PM2.5_30min_avg  PM10.0_30min_avg
--------------------------  ---------------  ---------------  ----------------
2022-01-01 14:02:05.613893  4.0              6.0              6.0
```

### Plotting

I use `scp` to copy the SQLite database to my computer and then plot it using matplotlib:

```
python -m iaq.viewer pms5003.db
```
