"""tl_ipc integration config flow.

This module provides the config flow functionality for the tl_ipc integration.
"""

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN


class TLIpcConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """处理配置流的类."""

    async def async_step_user(self, user_input=None) -> FlowResult:
        """处理用户输入."""
        errors = {}
        if user_input is not None:
            return self.async_create_entry(title="TL IPC", data=user_input)

        data_schema = vol.Schema(
            {
                vol.Required("ip"): str,
                vol.Required("port", default=80): int,
                vol.Required("username", default="admin"): str,
                vol.Required("password"): str,
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

    async def async_step_init(self, user_input=None) -> FlowResult:
        """处理初始化步骤."""
        return await self.async_step_user(user_input)
