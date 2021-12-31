import datetime
import sqlite3
import sys
from unittest.mock import Mock

import pytest

from pms5003logger import (
    Measurement,
    create_table,
    parse_args,
    read_sensor,
    write_measurement,
)


@pytest.fixture(scope="session", autouse=True)
def mock_rpi_packages():
    modules = ["RPi", "RPi.GPIO"]
    for module in modules:
        try:
            sys.modules[module]
        except KeyError:
            sys.modules[module] = Mock()


MOCK_READING_VALUE = 5.0


@pytest.fixture
def mock_sensor():
    reading = Mock(name="reading")
    reading.pm_ug_per_m3.return_value = MOCK_READING_VALUE

    sensor = Mock(name="sensor")
    sensor.read.return_value = reading
    return sensor


def test_read_sensor(mock_sensor):
    measurements = list(read_sensor(mock_sensor))
    mock_sensor.read.assert_called_once()
    assert all(measurement.value == MOCK_READING_VALUE for measurement in measurements)
    assert all(
        measurement.datetimestamp < datetime.datetime.now()
        for measurement in measurements
    )
    assert [measurement.name for measurement in measurements] == [
        "PM1.0",
        "PM2.5",
        "PM10.0",
    ]


@pytest.fixture
def db():
    db = sqlite3.connect(":memory:")
    create_table(db)
    return db


def test_write_measurement(db):
    measurement = Measurement(datetime.datetime.now(), "name", 1.0)
    write_measurement(db, measurement)

    cursor = db.cursor()
    query = "select datetimestamp, name, value from measurements"
    cursor.execute(query)
    assert cursor.fetchone() == (
        measurement.datetimestamp.isoformat(sep=" "),
        measurement.name,
        measurement.value,
    )
    assert cursor.fetchone() is None


def test_parse_args():
    args = parse_args(["database.db"])
    assert args.database == "database.db"
    assert args.device == "/dev/ttyAMA0"
    assert args.baud_rate == 9600
    assert args.pin_enable == 22
    assert args.pin_reset == 27