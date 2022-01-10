from setuptools import setup

setup(
    name="iaq",
    description="Indoor air quality measurement using a Raspberry Pi and PMS5003 and SCD-40 sensors",
    url="https://github.com/tomwphillips/pms5003-logger",
    packages=["iaq"],
    install_requires=["pms5003==0.0.5", "adafruit-circuitpython-scd4x==1.2.1"],
    extras_require={
        "dev": ["black", "pytest", "isort", "flake8"],
        "viewer": ["pandas", "matplotlib"],
    },
)
