"""tplink_ipc_implement integration init.

This module provides the setup and unload functionality for the tplink_ipc_implement integration.
"""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .core import TPLinkIPCCore

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """设置配置条目."""
    hass.data.setdefault(DOMAIN, {})

    hass.data[DOMAIN][entry.entry_id] = {
        "data": entry.data,
        "core": TPLinkIPCCore(
            entry.data["username"],
            entry.data["password"],
            entry.data["ip"],
            entry.data["port"],
        ),
    }

    await hass.config_entries.async_forward_entry_setups(entry, ["switch"])

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """卸载配置条目."""
    await hass.config_entries.async_forward_entry_unload(entry, "switch")
    hass.data[DOMAIN].pop(entry.entry_id)

    return True
