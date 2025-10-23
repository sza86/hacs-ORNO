
from __future__ import annotations

import asyncio
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.const import CONF_HOST, CONF_PORT

from .const import (
    DOMAIN,
    PLATFORMS,
    CONF_UNIT_ID,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
)
from .modbus_client import ModbusTcpClient
from .coordinator import OrnoCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})

    host = entry.data[CONF_HOST]
    port = entry.data[CONF_PORT]
    unit_id = entry.data.get(CONF_UNIT_ID, 2)
    scan_interval = entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

    client = ModbusTcpClient(host, port=port, unit_id=unit_id)

    try:
        await client.connect()
    except Exception as err:
        _LOGGER.warning("ORNO: wstępne połączenie Modbus nieudane: %s", err)

    coordinator = OrnoCoordinator(hass, client, scan_interval_s=scan_interval)
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = {
        "client": client,
        "lock": asyncio.Lock(),
        "entry_data": entry.data,
        "coordinator": coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    _LOGGER.info(
        "ORNO: entry %s skonfigurowany (%s:%s, unit=%s, interval=%ss)",
        entry.entry_id, host, port, unit_id, scan_interval
    )
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    data = hass.data[DOMAIN].pop(entry.entry_id, None)

    if data and "client" in data:
        try:
            await data["client"].close()
        except Exception as err:
            _LOGGER.debug("ORNO: błąd przy zamykaniu klienta: %s", err)

    return unload_ok
