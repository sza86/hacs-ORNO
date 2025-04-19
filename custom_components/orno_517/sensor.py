
"""Platforma sensorów dla ORNO 517."""
import logging
import time
import asyncio
from homeassistant.components.sensor import SensorEntity
from pymodbus.client import ModbusTcpClient
from homeassistant.core import callback
from .const import DOMAIN, CONF_HOST, CONF_PORT, CONF_SLAVE, CONF_SCAN_INTERVAL, CONF_DEVICE_NAME

_LOGGER = logging.getLogger(__name__)

SENSORS = [
    {"name": "Meter ID", "address": 2, "data_type": "int16", "unit": None},
    {"name": "Napięcie L1", "address": 14, "data_type": "float32", "unit": "V", "device_class": "voltage"},
    {"name": "Napięcie L2", "address": 16, "data_type": "float32", "unit": "V", "device_class": "voltage"},
    {"name": "Napięcie L3", "address": 18, "data_type": "float32", "unit": "V", "device_class": "voltage"},
    {"name": "Częstotliwość", "address": 20, "data_type": "float32", "unit": "Hz", "device_class": "frequency"},
    {"name": "Prąd L1", "address": 22, "data_type": "float32", "unit": "A", "device_class": "current"},
    {"name": "Prąd L2", "address": 24, "data_type": "float32", "unit": "A", "device_class": "current"},
    {"name": "Prąd L3", "address": 26, "data_type": "float32", "unit": "A", "device_class": "current"},
    {"name": "Całkowita moc czynna", "address": 28, "data_type": "float32", "unit": "W", "device_class": "power"},
    {"name": "Moc czynna chwilowa L1", "address": 30, "data_type": "float32", "unit": "W", "device_class": "power"},
    {"name": "Moc czynna chwilowa L2", "address": 32, "data_type": "float32", "unit": "W", "device_class": "power"},
    {"name": "Moc czynna chwilowa L3", "address": 34, "data_type": "float32", "unit": "W", "device_class": "power"},
    {"name": "Całkowita energia bierna", "address": 36, "data_type": "float32", "unit": "kvarh", "device_class": "energy"},
    {"name": "Moc bierna chwilowa L1", "address": 38, "data_type": "float32", "unit": "var", "device_class": "reactive_power"},
    {"name": "Moc bierna chwilowa L2", "address": 40, "data_type": "float32", "unit": "var", "device_class": "reactive_power"},
    {"name": "Moc bierna chwilowa L3", "address": 42, "data_type": "float32", "unit": "var", "device_class": "reactive_power"},
    {"name": "Całkowita moc pozorna", "address": 44, "data_type": "float32", "unit": "VA", "device_class": "apparent_power"},
    {"name": "Moc pozorna chwilowa L1", "address": 46, "data_type": "float32", "unit": "VA", "device_class": "apparent_power"},
    {"name": "Moc pozorna chwilowa L2", "address": 48, "data_type": "float32", "unit": "VA", "device_class": "apparent_power"},
    {"name": "Moc pozorna chwilowa L3", "address": 50, "data_type": "float32", "unit": "VA", "device_class": "apparent_power"},
    {"name": "Współczynnik mocy", "address": 52, "data_type": "float32", "unit": None, "device_class": "power_factor"},
    {"name": "Współczynnik mocy L1", "address": 54, "data_type": "float32", "unit": None, "device_class": "power_factor"},
    {"name": "Współczynnik mocy L2", "address": 56, "data_type": "float32", "unit": None, "device_class": "power_factor"},
    {"name": "Współczynnik mocy L3", "address": 58, "data_type": "float32", "unit": None, "device_class": "power_factor"},
]

async def async_setup_entry(hass, entry, async_add_entities):
    """Konfiguracja sensorów dla ORNO 517."""
    try:
        config = hass.data[DOMAIN][entry.entry_id]
        _LOGGER.info("Rozpoczęcie konfiguracji Modbus: %s", config)

        client = ModbusTcpClient(host=config[CONF_HOST], port=config[CONF_PORT], timeout=10)
        scan_interval = entry.options.get(CONF_SCAN_INTERVAL, config.get(CONF_SCAN_INTERVAL, 10))
        device_name = config[CONF_DEVICE_NAME]
        entry_id = entry.entry_id

        sensors = [Orno517Sensor(sensor, device_name, entry_id, config[CONF_SLAVE]) for sensor in SENSORS]
        async_add_entities(sensors, update_before_add=False)
        _LOGGER.info("Dodano encje: %s", [sensor.name for sensor in sensors])

        updater = ModbusUpdater(client, config[CONF_SLAVE], sensors, scan_interval)
        hass.data[DOMAIN][f"{entry_id}_updater"] = updater
        hass.loop.create_task(updater.async_start_polling())

        @callback
        async def update_options():
            """Reaguj na zmiany opcji."""
            new_scan_interval = entry.options.get(CONF_SCAN_INTERVAL, scan_interval)
            _LOGGER.info("Nowy interwał odświeżania: %s sekund", new_scan_interval)
            await updater.async_update_scan_interval(new_scan_interval)

        entry.add_update_listener(update_options)

    except Exception as e:
        _LOGGER.error("Błąd konfiguracji sensorów: %s", e)
        raise

class ModbusUpdater:
    """Zarządzanie aktualizacjami rejestrów Modbus."""

    def __init__(self, client, slave, sensors, scan_interval):
        self.client = client
        self.slave = slave
        self.sensors = sensors
        self.scan_interval = scan_interval
        self._stop_event = asyncio.Event()

    async def async_start_polling(self):
        """Rozpocznij odpytywanie Modbus."""
        retry_count = 0
        max_retries = 3
        try:
            while not self._stop_event.is_set():
                start_time = time.monotonic()
                _LOGGER.debug("Rozpoczęcie pętli odpytywania, interwał: %s sekund", self.scan_interval)

                data = self._read_modbus_data()

                if data:
                    retry_count = 0
                    for sensor in self.sensors:
                        try:
                            sensor.update_state(data)
                        except Exception as e:
                            _LOGGER.error("Błąd aktualizacji sensora %s: %s", sensor.name, e)
                else:
                    retry_count += 1
                    _LOGGER.error("Nie udało się pobrać danych Modbus. Próba %d z %d", retry_count, max_retries)
                    if retry_count >= max_retries:
                        _LOGGER.error("Zatrzymano odpytywanie po %d nieudanych próbach", max_retries)
                        break

                elapsed_time = time.monotonic() - start_time
                sleep_time = max(0, self.scan_interval - elapsed_time)
                await asyncio.sleep(sleep_time)
        except asyncio.CancelledError:
            _LOGGER.info("Zatrzymano odpytywanie Modbus")
        finally:
            self.client.close()

    def _read_modbus_data(self):
        """Odczyt danych z Modbus."""
        try:
            start_address = SENSORS[0]["address"]
            end_address = SENSORS[-1]["address"]
            count = (end_address - start_address) + 2

            if not self.client.connect():
                _LOGGER.error("Nie udało się połączyć z Modbus")
                return None

            result = self.client.read_holding_registers(address=start_address, count=count, slave=self.slave)
            if result and hasattr(result, "registers"):
                _LOGGER.debug("Odczytane dane Modbus: %s", result.registers)
                return result.registers
            else:
                _LOGGER.warning("Brak odpowiedzi z urządzenia Modbus")
        except Exception as e:
            _LOGGER.error("Błąd podczas odczytu Modbus: %s", e)
        return None

    async def async_update_scan_interval(self, new_interval):
        """Zmień interwał odpytywania."""
        self.scan_interval = new_interval
        _LOGGER.info("Zaktualizowano interwał odświeżania na %s sekund", new_interval)

    async def async_stop_polling(self):
        """Zatrzymaj odpytywanie Modbus."""
        self._stop_event.set()

class Orno517Sensor(SensorEntity):
    """Sensor ORNO 517."""

    def __init__(self, sensor, device_name, entry_id, slave_id):
        self._name = f"{device_name} {sensor['name']}"
        self._address = sensor["address"]
        self._data_type = sensor["data_type"]
        self._unit = sensor.get("unit")
        self._device_class = sensor.get("device_class")
        self._state = None
        self._unique_id = f"{entry_id}_{slave_id}_{sensor['address']}"

        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry_id)},
            "name": device_name,
            "manufacturer": "ORNO",
            "model": "OR-517",
            "sw_version": "1.0",
        }

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def state(self):
        return self._state

    @property
    def unit_of_measurement(self):
        return self._unit

    @property
    def device_class(self):
        return self._device_class

    def update_state(self, data):
        """Aktualizuj stan na podstawie danych Modbus."""
        try:
            index = self._address - SENSORS[0]["address"]
            if index < 0 or index >= len(data):
                self._state = None
            else:
                if self._data_type == "int16":
                    self._state = data[index]
                elif self._data_type == "float32":
                    self._state = round(self._convert_to_float32(data[index:index + 2]), 2)
            self.async_write_ha_state()
        except Exception as e:
            _LOGGER.error("Błąd aktualizacji sensora %s: %s", self.name, e)

    @staticmethod
    def _convert_to_float32(registers):
        """Konwertuj rejestry na float32."""
        import struct
        try:
            raw = (registers[0] << 16) | registers[1]
            return struct.unpack(">f", raw.to_bytes(4, byteorder="big"))[0]
        except Exception as e:
            _LOGGER.error("Błąd konwersji danych: %s", e)
            return None
