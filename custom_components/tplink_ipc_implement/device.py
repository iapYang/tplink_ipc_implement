"""tplink_ipc_implement Device.

This module provides the device for interacting with tplink_ipc_implement devices.
"""

import json
import logging
import urllib.parse

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN
from .core import TPLinkIPCCore

_LOGGER = logging.getLogger(__name__)


class TPLinkIPCDevice:
    """TPLink IPC Device."""

    def __init__(self, ipc_core: TPLinkIPCCore, entry: ConfigEntry) -> None:
        """Initialize the device."""
        self._ipc_core = ipc_core
        self._entry = entry

    async def get_device_info(self):
        """Get device info."""
        try:
            device_data = await self._ipc_core.post_data(
                json.dumps(
                    {"method": "get", "device_info": {"name": ["basic_info", "info"]}}
                )
            )
        except Exception as e:
            _LOGGER.error("Failed to get device info: %s", e)
            device_data = None

        base_info = (device_data or {}).get("device_info", {}).get("basic_info", {})
        sw_version = base_info.get("sw_version")

        device_info_data = {
            "manufacturer": base_info.get("manufacturer_name"),
            "model": base_info.get("device_model"),
            "default_name": base_info.get("device_name"),
            "sw_version": urllib.parse.unquote(sw_version) if sw_version else None,
            "hw_version": base_info.get("hw_version"),
        }

        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            manufacturer=device_info_data.get("manufacturer"),
            model=device_info_data.get("model"),
            name=self._entry.title,
            sw_version=device_info_data.get("sw_version"),
            hw_version=device_info_data.get("hw_version"),
        )
