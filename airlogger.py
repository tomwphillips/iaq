import argparse
import datetime
import sqlite3
import time


def create_table(db):
    cursor = db.cursor()
    cursor.execute("""
        create table readings (
            'datetimestamp' datetime,
            'pm1_ug_per_m3' real,
            'pm25_ug_per_m3' real,
            'pm10_ug_per_m3' real
        )
    """)

def read_sensor(sensor):
    pm_sizes = [1.0, 2.5, 10.0]
    reading = sensor.read()
    return datetime.datetime.now(), {pm_size: reading.pm_ug_per_m3(pm_size) for pm_size in pm_sizes}

def record_reading(db, reading):
    datetimestamp, pm_ug_per_m3 = reading
    cursor = db.cursor()
    cursor.execute("insert into readings values  (?, ?, ?, ?)", (datetimestamp, *pm_ug_per_m3.values()))

def parse_args(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("database")
    parser.add_argument("-p", "--period", type=int, help="Period between measurements (seconds)", default=60)
    parser.add_argument("-d", "--device", default="/dev/ttyAMA0", help="Serial port to PMS5003")
    parser.add_argument("-b", "--baud-rate", default=9600, type=int, help="Baud rate")
    parser.add_argument("-e", "--pin-enable", default=22, type=int, help="GPIO pin connected to PMS5003 enable pin")
    parser.add_argument("-r", "--pin-reset", default=27, type=int, help="GPIO pin connected to PMS5003 reset pin")
    return parser.parse_args(args)


def main(args=None):
    import pms5003  # import here because running tests off-RPi imports RPi before it's mocked

    args = parse_args(args)
    sensor = pms5003.PMS5003(args.device, args.baud_rate, args.pin_enable, args.pin_reset)
    db = sqlite3.connection(args.database)

    try:
        while True:
            reading = read_sensor(sensor)
            record_reading(db, reading)
            time.sleep(args.period)
    finally:
        db.close()    


if __name__ == "__main__":
    main()