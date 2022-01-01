import argparse
import datetime
import sqlite3
from typing import Iterator, NamedTuple


def create_table(db):
    cursor = db.cursor()
    cursor.execute(
        """
        create table measurements (
            'timestamp' timestamp,
            'name' text,
            'value' real
        )
    """
    )


class Measurement(NamedTuple):
    datetimestamp: datetime.datetime
    name: str
    value: float


def read_sensor(sensor) -> Iterator[Measurement]:
    pm_sizes = [1.0, 2.5, 10.0]
    readings = sensor.read()
    datetimestamp = datetime.datetime.now()
    for pm_size in pm_sizes:
        yield Measurement(datetimestamp, f"PM{pm_size}", readings.pm_ug_per_m3(pm_size))


def write_measurements(conn, measurements):
    with conn:
        cursor = conn.cursor()
        cursor.executemany(
            "insert into measurements(timestamp, name, value) values  (?, ?, ?)",
            measurements,
        )


def parse_args(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("database")
    parser.add_argument("--create-table", action="store_true")
    parser.add_argument(
        "-d", "--device", default="/dev/ttyAMA0", help="Serial port to PMS5003"
    )
    parser.add_argument("-b", "--baud-rate", default=9600, type=int, help="Baud rate")
    parser.add_argument(
        "-e",
        "--pin-enable",
        default=22,
        type=int,
        help="GPIO pin connected to PMS5003 enable pin",
    )
    parser.add_argument(
        "-r",
        "--pin-reset",
        default=27,
        type=int,
        help="GPIO pin connected to PMS5003 reset pin",
    )
    return parser.parse_args(args)


def main(args=None):
    import pms5003  # import here because running tests off-RPi imports RPi before it's mocked

    args = parse_args(args)
    sensor = pms5003.PMS5003(
        args.device, args.baud_rate, args.pin_enable, args.pin_reset
    )
    measurements = read_sensor(sensor)

    conn = sqlite3.connect(args.database)

    try:
        if args.create_table:
            create_table(conn)

        write_measurements(conn, measurements)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
