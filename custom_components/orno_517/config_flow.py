"""Config flow dla ORNO 517."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN, CONF_HOST, CONF_PORT, CONF_SLAVE, CONF_SCAN_INTERVAL, CONF_DEVICE_NAME
import logging

_LOGGER = logging.getLogger(__name__)

class Orno517ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Obsługa config flow dla ORNO 517."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Obsługa kroku początkowego."""
        errors = {}

        if user_input is not None:
            try:
                # Weryfikacja danych wejściowych użytkownika
                _LOGGER.debug("Weryfikacja danych: %s", user_input)
                host = user_input[CONF_HOST]
                port = user_input[CONF_PORT]

                # Prosty test połączenia Modbus
                from pymodbus.client import ModbusTcpClient
                client = ModbusTcpClient(host=host, port=port, timeout=5)
                if not client.connect():
                    raise ValueError("Nie można połączyć się z hostem")

                client.close()
                return self.async_create_entry(title=user_input[CONF_DEVICE_NAME], data=user_input)
            except Exception as e:
                _LOGGER.error("Błąd podczas testowania połączenia: %s", e)
                errors["base"] = "cannot_connect"

        # Formularz konfiguracji
        data_schema = vol.Schema(
            {
                vol.Required(CONF_HOST): str,
                vol.Required(CONF_PORT, default=4196): int,
                vol.Required(CONF_SLAVE, default=2): int,
                vol.Optional(CONF_DEVICE_NAME, default="ORNO 517"): str,
                vol.Optional(CONF_SCAN_INTERVAL, default=20): vol.All(vol.Coerce(int), vol.Range(min=10, max=3600)),
            }
        )
        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        from .options_flow import Orno517OptionsFlowHandler
        return Orno517OptionsFlowHandler(config_entry)
