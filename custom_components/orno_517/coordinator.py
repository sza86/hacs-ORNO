
from __future__ import annotations

import logging
import struct
from datetime import timedelta
from typing import Any, Dict, List, Tuple

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import SENSOR_DEFS, UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)

class OrnoCoordinator(DataUpdateCoordinator[Dict[str, Any]]):
    """Koordynator odczytów Modbus dla ORNO 517."""

    def __init__(self, hass: HomeAssistant, client, scan_interval_s: int | None = None) -> None:
        interval = timedelta(seconds=scan_interval_s) if scan_interval_s else UPDATE_INTERVAL
        super().__init__(hass, _LOGGER, name="ORNO Coordinator", update_interval=interval)
        self.client = client
        self._defs: List[Dict[str, Any]] = list(SENSOR_DEFS)

    async def _async_update_data(self) -> Dict[str, Any]:
        results: Dict[str, Any] = {}
        errors: List[Tuple[int, str]] = []

        for d in self._defs:
            addr: int = d["address"]
            dtype: str = d.get("dtype") or d.get("data_type", "uint16")
            name: str = d["name"]
            unit_type: str = d.get("input_type", "holding")  # holding | input
            scale: float = float(d.get("scale", 1.0))
            precision = d.get("precision")
            word_swap: bool = bool(d.get("word_swap", False))
            fallback: bool = bool(d.get("fallback", True))

            count = 1 if dtype in ("uint16", "int16") else 2

            async def _read(kind: str) -> List[int]:
                if kind == "holding":
                    return await self.client.read_holding_registers(addr, count)
                return await self.client.read_input_registers(addr, count)

            regs: List[int] | None = None
            try:
                regs = await _read(unit_type)
            except Exception as e1:
                if fallback:
                    try:
                        other = "input" if unit_type == "holding" else "holding"
                        regs = await _read(other)
                        _LOGGER.debug("ORNO: %s: fallback %s->%s OK", name, unit_type, other)
                    except Exception as e2:
                        errors.append((addr, f"{e1} / {e2}"))
                else:
                    errors.append((addr, str(e1)))

            if not regs:
                continue

            try:
                value = self._decode_registers(regs, dtype, word_swap)
            except Exception as dec_err:
                errors.append((addr, f"decode error: {dec_err}"))
                continue

            if scale != 1.0:
                value = value * scale
            if precision is not None and isinstance(value, (int, float)):
                value = round(value, int(precision))

            results[name] = value
            results[str(addr)] = value

        if not results and errors:
            raise UpdateFailed("Modbus: żadnego sensora nie udało się odczytać")

        if errors:
            for a, msg in errors:
                _LOGGER.warning("ORNO: problem z adresem %s: %s", a, msg)

        return results

    @staticmethod
    def _decode_registers(regs: List[int], dtype: str, word_swap: bool) -> Any:
        if dtype == "uint16":
            return int(regs[0] & 0xFFFF)

        if dtype == "int16":
            val = regs[0]
            if val & 0x8000:
                val -= 0x10000
            return int(val)

        if dtype in ("uint32", "float32"):
            if len(regs) < 2:
                raise ValueError("brak dwóch rejestrów dla wartości 32-bit")
            hi, lo = regs[0], regs[1]
            if word_swap:
                hi, lo = lo, hi
            raw = (hi << 16) | lo
            if dtype == "uint32":
                return int(raw & 0xFFFFFFFF)
            return struct.unpack(">f", raw.to_bytes(4, "big"))[0]

        raise ValueError(f"Nieznany data_type: {dtype}")
