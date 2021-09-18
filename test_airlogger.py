import sys
from unittest.mock import Mock

from airlogger import read_sensor

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
