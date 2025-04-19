"""Integracja ORNO 517."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from .const import DOMAIN, PLATFORMS, CONF_SCAN_INTERVAL
import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Inicjalizacja integracji ORNO 517."""
    _LOGGER.debug("Rozpoczęto konfigurację integracji ORNO 517")
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Konfiguracja ORNO 517 na podstawie wpisu konfiguracyjnego."""
    _LOGGER.info("Rozpoczynanie konfiguracji wpisu ORNO 517: %s", entry.entry_id)
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    try:
        # Forward entry setups to the specified platforms
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
        _LOGGER.info("Pomyślnie skonfigurowano platformy dla ORNO 517")

        updater = hass.data[DOMAIN].get(f"{entry.entry_id}_updater")
        scan_interval = entry.options.get(CONF_SCAN_INTERVAL, 20)

        @callback
        def update_options(hass: HomeAssistant, entry: ConfigEntry):
            """Reaguj na zmiany opcji."""
            new_scan_interval = entry.options.get(CONF_SCAN_INTERVAL, scan_interval)
            _LOGGER.info("Nowy interwał odświeżania: %s sekund", new_scan_interval)
            if updater:
                hass.loop.create_task(updater.async_update_scan_interval(new_scan_interval))

        # Add the update listener
        entry.async_on_unload(entry.add_update_listener(update_options))

    except Exception as e:
        _LOGGER.error("Błąd podczas konfiguracji platform ORNO 517: %s", e, exc_info=True)
        return False

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Rozładuj wpis konfiguracyjny ORNO 517."""
    _LOGGER.info("Rozpoczynanie rozładowywania wpisu ORNO 517: %s", entry.entry_id)

    try:
        # Zatrzymaj updater, jeśli istnieje
        updater_key = f"{entry.entry_id}_updater"
        if updater_key in hass.data[DOMAIN]:
            updater = hass.data[DOMAIN][updater_key]
            await updater.async_stop_polling()

        unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
        if unload_ok:
            hass.data[DOMAIN].pop(entry.entry_id, None)
            _LOGGER.info("Pomyślnie rozładowano platformy dla ORNO 517")
        else:
            _LOGGER.warning("Nie udało się rozładować wszystkich platform dla ORNO 517")
    except Exception as e:
        _LOGGER.error("Błąd podczas rozładowywania platform ORNO 517: %s", e, exc_info=True)
        return False

    return unload_ok
