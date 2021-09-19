import argparse
import datetime


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

    return parser.parse_args(args)