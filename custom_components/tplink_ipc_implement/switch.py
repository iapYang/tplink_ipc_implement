"""tplink_ipc_implement switch entity.

This module contains the TPLinkIPCLensMaskSwitch class which represents a tplink_ipc_implement switch entity.
"""

import asyncio
import json
import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .core import TPLinkIPCCore
from .device import TPLinkIPCDevice

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """设置开关实体."""
    data = hass.data[DOMAIN][entry.entry_id]

    ipc_core = TPLinkIPCCore(
        data["username"], data["password"], data["ip"], data["port"]
    )

    device = TPLinkIPCDevice(ipc_core, entry)

    device_info = await device.get_device_info()

    async_add_entities(
        [
            TPLinkIPCLensMaskSwitch(
                entry.entry_id,
                ipc_core,
                device_info,
            )
        ]
    )


class TPLinkIPCLensMaskSwitch(SwitchEntity):
    """表示TPLink IPC开关的实体."""

    def __init__(
        self,
        entry_id: str,
        ipc_core: TPLinkIPCCore,
        device_info: DeviceInfo,
    ) -> None:
        """初始化TPLink IPC开关实体."""
        self._is_on = False
        self._ipc_core = ipc_core
        self._key = entry_id
        self._device_info = device_info
        self._title = self._device_info.get("name")
        self._attr_unique_id = "{}.{}_{}".format(
            DOMAIN, "tplink_ipc_implement_lens_mask", self._key
        ).lower()
        self.entity_id = self._attr_unique_id
        self._update_task = None

    @property
    def name(self) -> str:
        """返回实体的名称."""
        return self._title + " Lens Mask"

    @property
    def is_on(self) -> bool:
        """返回开关状态."""
        return self._is_on

    @property
    def unique_id(self) -> str:
        """返回实体的唯一ID."""
        return self._attr_unique_id

    @property
    def device_info(self) -> DeviceInfo:
        """返回设备信息."""
        return self._device_info

    async def async_turn_on(self, **kwargs) -> None:
        """打开开关."""
        _LOGGER.debug("Turning on the switch")
        await self._ipc_core.post_data(
            json.dumps(
                {"method": "set", "lens_mask": {"lens_mask_info": {"enabled": "on"}}}
            )
        )
        self._is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        """关闭开关."""
        _LOGGER.debug("Turning off the switch")
        await self._ipc_core.post_data(
            json.dumps(
                {"method": "set", "lens_mask": {"lens_mask_info": {"enabled": "off"}}}
            )
        )
        self._is_on = False
        self.async_write_ha_state()

    async def async_added_to_hass(self):
        """当实体被添加到Home Assistant时调用."""
        self._update_task = asyncio.create_task(self._periodic_update())

    async def _periodic_update(self):
        """每30秒更新一次is_on状态."""
        while True:
            await self._update_is_on()
            await asyncio.sleep(30)

    async def _update_is_on(self):
        """更新is_on状态."""
        _LOGGER.debug("Updating the switch status")
        data = await self._ipc_core.post_data(
            json.dumps({"method": "get", "lens_mask": {"name": ["lens_mask_info"]}})
        )
        self._is_on = (
            data.get("lens_mask", {}).get("lens_mask_info", {}).get("enabled") == "on"
        )
        self.async_write_ha_state()
