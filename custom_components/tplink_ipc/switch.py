import logging
from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .tplink_ipc_core import TplinkIpcCore

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """设置开关实体."""
    data = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [TplinkIpcSwitch(data["ip"], data["port"], data["username"], data["password"])]
    )


class TplinkIpcSwitch(SwitchEntity):
    """表示TP-Link IPC开关的实体."""

    def __init__(self, ip: str, port: int, username: str, password: str):
        self._ip = ip
        self._port = port
        self._username = username
        self._password = password
        self._is_on = False
        self._tplink_ipc_core = TplinkIpcCore(username, password, ip, port)

    @property
    def name(self) -> str:
        return "Lens Mask"

    @property
    def is_on(self) -> bool:
        return self._is_on

    async def async_turn_on(self, **kwargs) -> None:
        """打开开关."""
        _LOGGER.debug("Turning on the switch")
        await self._tplink_ipc_core.post_data(
            {"method": "set", "lens_mask": {"lens_mask_info": {"enabled": "on"}}}
        )
        self._is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        """关闭开关."""
        _LOGGER.debug("Turning off the switch")
        await self._tplink_ipc_core.post_data(
            {"method": "set", "lens_mask": {"lens_mask_info": {"enabled": "off"}}}
        )
        self._is_on = False
        self.async_write_ha_state()
