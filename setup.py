from setuptools import setup

setup(
    name='pms5003-logger',
    version='0.1.0', 
    description='Raspberry Pi-based Logger for PMS5003 air pollution sensor',
    url='https://github.com/tomwphillips/pms5003-logger',
    py_modules=["pms5003logger"],
    python_requires='>=3.6, <4',
    install_requires=['pms5003==0.0.5']
)
