import datetime
import sqlite3
import sys
from unittest.mock import Mock, PropertyMock

import pytest

from iaq.logger import (
    Measurement,
    create_table,
    parse_args,
    read_pms_sensor,
    read_scd_sensor,
    write_measurements,
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
MOCK_TEMPERATURE_VALUE = 21.0
MOCK_RELATIVE_HUMIDITY_VALUE = 50.0
MOCK_CO2_VALUE = 500.0


@pytest.fixture
def mock_pms_sensor():
    reading = Mock(name="reading")
    reading.pm_ug_per_m3.return_value = MOCK_READING_VALUE

    sensor = Mock(name="sensor")
    sensor.read.return_value = reading
    return sensor


def test_read_pms_sensor(mock_pms_sensor):
    measurements = list(read_pms_sensor(mock_pms_sensor))
    mock_pms_sensor.read.assert_called_once()
    assert all(measurement.value == MOCK_READING_VALUE for measurement in measurements)
    assert all(
        measurement.timestamp < datetime.datetime.now() for measurement in measurements
    )
    assert [measurement.name for measurement in measurements] == [
        "PM1.0",
        "PM2.5",
        "PM10.0",
    ]


def mock_scd_sensor_factory(data_ready=[True]):
    sensor = Mock(name="sensor")
    type(sensor).data_ready = PropertyMock(name="data_ready", side_effect=data_ready)
    sensor.temperature = MOCK_TEMPERATURE_VALUE
    sensor.CO2 = MOCK_CO2_VALUE
    sensor.relative_humidity = MOCK_RELATIVE_HUMIDITY_VALUE
    return sensor


def test_read_scd_sensor():
    scd_sensor = mock_scd_sensor_factory()
    measurements = list(read_scd_sensor(scd_sensor))
    assert [(measurement.name, measurement.value) for measurement in measurements] == [
        ("temperature", MOCK_TEMPERATURE_VALUE),
        ("relative_humidity", MOCK_RELATIVE_HUMIDITY_VALUE),
        ("CO2", MOCK_CO2_VALUE),
    ]
    assert all(
        measurement.timestamp < datetime.datetime.now() for measurement in measurements
    )


def test_retry_read_scd_sensor_when_data_not_ready():
    scd_sensor = mock_scd_sensor_factory(data_ready=[False, False, False, False, True])
    measurements = list(read_scd_sensor(scd_sensor, polling_interval=0.01))
    assert [(measurement.name, measurement.value) for measurement in measurements] == [
        ("temperature", MOCK_TEMPERATURE_VALUE),
        ("relative_humidity", MOCK_RELATIVE_HUMIDITY_VALUE),
        ("CO2", MOCK_CO2_VALUE),
    ]
    assert all(
        measurement.timestamp < datetime.datetime.now() for measurement in measurements
    )


def test_read_scd_sensor_fails_after_max_tries():
    scd_sensor = mock_scd_sensor_factory(data_ready=[False] * 5)
    with pytest.raises(RuntimeError):
        list(read_scd_sensor(scd_sensor, polling_interval=0.01))


@pytest.fixture
def db_file(tmp_path):
    filename = tmp_path / "tests.db"
    conn = sqlite3.connect(filename)
    create_table(conn)
    conn.close()
    return filename


def test_write_measurements(db_file):
    conn = sqlite3.connect(db_file)
    measurement = Measurement(datetime.datetime.now(), "name", 1.0)
    write_measurements(conn, [measurement])
    conn.close()

    conn = sqlite3.connect(db_file, detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = conn.cursor()
    query = "select timestamp, name, value from measurements"
    cursor.execute(query)
    assert cursor.fetchmany() == [
        (
            measurement.timestamp,
            measurement.name,
            measurement.value,
        )
    ]


def test_parse_args_to_run():
    args = parse_args(["database.db"])
    assert args.database == "database.db"
    assert args.pms_enabled
    assert args.scd_enabled


def test_parse_args_disable_pm():
    args = parse_args(["database.db", "--disable-pms"])
    assert args.pms_enabled is False


def test_parse_args_disable_scd40():
    args = parse_args(["database.db", "--disable-scd"])
    assert args.scd_enabled is False


def test_parse_args_to_create_table():
    args = parse_args(["--create-table", "database.db"])
    assert args.create_table is True
    assert args.database == "database.db"
