
from __future__ import annotations
from datetime import timedelta
from homeassistant.components.sensor import SensorDeviceClass

DOMAIN = "orno_517"

CONF_UNIT_ID = "unit_id"
CONF_SCAN_INTERVAL = "scan_interval"

DEFAULT_HOST = "192.168.86.202"
DEFAULT_PORT = 4196
DEFAULT_UNIT_ID = 2
DEFAULT_SCAN_INTERVAL = 15

PLATFORMS = ["sensor"]
UPDATE_INTERVAL = timedelta(seconds=DEFAULT_SCAN_INTERVAL)

SENSOR_DEFS = [
    {"name": "Napięcie L1", "address": 14, "unit": "V", "device_class": SensorDeviceClass.VOLTAGE, "input_type": "input", "dtype": "float32", "precision": 1},
    {"name": "Napięcie L2", "address": 16, "unit": "V", "device_class": SensorDeviceClass.VOLTAGE, "input_type": "input", "dtype": "float32", "precision": 1},
    {"name": "Napięcie L3", "address": 18, "unit": "V", "device_class": SensorDeviceClass.VOLTAGE, "input_type": "input", "dtype": "float32", "precision": 1},

    {"name": "Częstotliwość", "address": 20, "unit": "Hz", "device_class": SensorDeviceClass.FREQUENCY, "input_type": "input", "dtype": "float32", "precision": 1},

    {"name": "Prąd L1", "address": 22, "unit": "A", "device_class": SensorDeviceClass.CURRENT, "input_type": "input", "dtype": "float32", "precision": 1},
    {"name": "Prąd L2", "address": 24, "unit": "A", "device_class": SensorDeviceClass.CURRENT, "input_type": "input", "dtype": "float32", "precision": 1},
    {"name": "Prąd L3", "address": 26, "unit": "A", "device_class": SensorDeviceClass.CURRENT, "input_type": "input", "dtype": "float32", "precision": 1},

    {"name": "Moc czynna", "address": 28, "unit": "kW", "device_class": SensorDeviceClass.POWER, "input_type": "input", "dtype": "float32", "precision": 1},
    {"name": "Moc czynna L1", "address": 30, "unit": "kW", "device_class": SensorDeviceClass.POWER, "input_type": "input", "dtype": "float32", "precision": 1},
    {"name": "Moc czynna L2", "address": 32, "unit": "kW", "device_class": SensorDeviceClass.POWER, "input_type": "input", "dtype": "float32", "precision": 1},
    {"name": "Moc czynna L3", "address": 34, "unit": "kW", "device_class": SensorDeviceClass.POWER, "input_type": "input", "dtype": "float32", "precision": 1},

    {"name": "Moc bierna", "address": 36, "unit": "kvar", "device_class": None, "input_type": "input", "dtype": "float32", "precision": 1},
    {"name": "Moc bierna L1", "address": 38, "unit": "kvar", "device_class": None, "input_type": "input", "dtype": "float32", "precision": 1},
    {"name": "Moc bierna L2", "address": 40, "unit": "kvar", "device_class": None, "input_type": "input", "dtype": "float32", "precision": 1},
    {"name": "Moc bierna L3", "address": 42, "unit": "kvar", "device_class": None, "input_type": "input", "dtype": "float32", "precision": 1},

    {"name": "Moc pozorna", "address": 44, "unit": "kVA", "device_class": None, "input_type": "input", "dtype": "float32", "precision": 1},
    {"name": "Moc pozorna L1", "address": 46, "unit": "kVA", "device_class": None, "input_type": "input", "dtype": "float32", "precision": 1},
    {"name": "Moc pozorna L2", "address": 48, "unit": "kVA", "device_class": None, "input_type": "input", "dtype": "float32", "precision": 1},
    {"name": "Moc pozorna L3", "address": 50, "unit": "kVA", "device_class": None, "input_type": "input", "dtype": "float32", "precision": 1},

    {"name": "Współczynnik mocy", "address": 52, "unit": "", "device_class": None, "input_type": "input", "dtype": "float32", "precision": 2},
    {"name": "Współczynnik mocy L1", "address": 54, "unit": "", "device_class": None, "input_type": "input", "dtype": "float32", "precision": 2},
    {"name": "Współczynnik mocy L2", "address": 56, "unit": "", "device_class": None, "input_type": "input", "dtype": "float32", "precision": 2},
    {"name": "Współczynnik mocy L3", "address": 58, "unit": "", "device_class": None, "input_type": "input", "dtype": "float32", "precision": 2},
]
