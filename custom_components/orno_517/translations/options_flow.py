"""Opcje konfiguracji dla ORNO 517."""
import voluptuous as vol
from homeassistant import config_entries
from .const import CONF_SCAN_INTERVAL
import logging

_LOGGER = logging.getLogger(__name__)

class Orno517OptionsFlowHandler(config_entries.OptionsFlow):
    """Handler opcji konfiguracji dla ORNO 517."""

    def __init__(self, config_entry):
        """Inicjalizacja."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Pierwszy krok opcji konfiguracji."""
        errors = {}

        if user_input is not None:
            try:
                scan_interval = int(user_input[CONF_SCAN_INTERVAL])
                if scan_interval < 10 or scan_interval > 3600:
                    raise ValueError("Interwał musi być w zakresie 10-3600 sekund.")
                _LOGGER.info("Zapisano opcje: %s", user_input)
                return self.async_create_entry(title="", data=user_input)
            except ValueError:
                _LOGGER.error("Nieprawidłowa wartość interwału: %s", user_input)
                errors["base"] = "invalid_scan_interval"
            except Exception as e:
                _LOGGER.error("Niespodziewany błąd: %s", e)
                errors["base"] = "unknown_error"

        current_scan_interval = self.config_entry.options.get(CONF_SCAN_INTERVAL, 20)
        _LOGGER.debug("Aktualny interwał: %s", current_scan_interval)

        options_schema = vol.Schema(
            {
                vol.Required(CONF_SCAN_INTERVAL, default=current_scan_interval): int,
            }
        )
        return self.async_show_form(step_id="init", data_schema=options_schema, errors=errors)
