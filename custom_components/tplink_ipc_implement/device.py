"""tplink_ipc_implement Device.

This module provides the device for interacting with tplink_ipc_implement devices.
"""

import json
import urllib.parse


class TPLinkIPCDevice:
    """TPLink IPC Device."""

    def __init__(self, tplink_ipc_implement_core) -> None:
        """Initialize the device."""
        self._tplink_ipc_implement_core = tplink_ipc_implement_core

    async def get_device_info(self):
        """Get device info."""
        device_data = await self._tplink_ipc_implement_core.post_data(
            json.dumps(
                {"method": "get", "device_info": {"name": ["basic_info", "info"]}}
            )
        )

        base_info = device_data.get("device_info", {}).get("basic_info", {})

        return {
            "manufacturer": base_info.get("manufacturer_name"),
            "model": base_info.get("device_model"),
            "default_name": base_info.get("device_name"),
            "sw_version": urllib.parse.unquote(base_info.get("sw_version")),
            "hw_version": base_info.get("hw_version"),
        }
