import sqlite3
import sys
from unittest.mock import Mock

from airlogger import read_sensor, record_reading, create_table

import pytest


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
    pm_ug_per_m3 = read_sensor(mock_sensor)
    mock_sensor.read.assert_called_once()
    assert pm_ug_per_m3[1.0] == MOCK_READING_VALUE
    assert pm_ug_per_m3[2.5] == MOCK_READING_VALUE
    assert pm_ug_per_m3[10.0] == MOCK_READING_VALUE


@pytest.fixture
def db():
    db = sqlite3.connect(":memory:")
    create_table(db)
    return db


def test_record_reading(db):
    reading = {1.0: 1.0, 2.5: 3.0, 10.0: 7.0}
    record_reading(db, reading)

    cursor = db.cursor()
    query = "select pm1_ug_per_m3, pm25_ug_per_m3, pm10_ug_per_m3 from readings"
    cursor.execute(query)
    assert cursor.fetchone() == tuple(reading.values())
    assert cursor.fetchone() is None
