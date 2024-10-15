"""tplink_ipc_implement integration config flow.

This module provides the config flow functionality for the tplink_ipc_implement integration.
"""

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import DEFAULT_PORT, DEFAULT_USERNAME, DOMAIN


class TPLinkIPCConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """处理配置流的类."""

    async def async_step_user(self, user_input=None) -> FlowResult:
        """处理用户输入."""
        errors = {}
        if user_input is not None:
            return self.async_create_entry(title="TPLink IPC", data=user_input)

        data_schema = vol.Schema(
            {
                vol.Required("ip"): str,
                vol.Required("port", default=DEFAULT_PORT): int,
                vol.Required("username", default=DEFAULT_USERNAME): str,
                vol.Required("password"): str,
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

    async def async_step_init(self, user_input=None) -> FlowResult:
        """处理初始化步骤."""
        return await self.async_step_user(user_input)

    async def async_step_edit(self, user_input=None) -> FlowResult:
        """处理用户编辑输入."""
        errors = {}
        if user_input is not None:
            return self.async_create_entry(title="TPLink IPC", data=user_input)

        # 获取之前的输入数据
        entry_id = self.context.get("entry_id")
        if entry_id:
            entry = self.hass.config_entries.async_get_entry(entry_id)
            if entry:
                previous_data = entry.data
            else:
                previous_data = {
                    "ip": "",
                    "port": DEFAULT_PORT,
                    "username": DEFAULT_USERNAME,
                    "password": "",
                }
        else:
            previous_data = {
                "ip": "",
                "port": DEFAULT_PORT,
                "username": DEFAULT_USERNAME,
                "password": "",
            }

        data_schema = vol.Schema(
            {
                vol.Required("ip", default=previous_data["ip"]): str,
                vol.Required("port", default=previous_data["port"]): int,
                vol.Required("username", default=previous_data["username"]): str,
                vol.Required("password", default=previous_data["password"]): str,
            }
        )

        return self.async_show_form(
            step_id="edit", data_schema=data_schema, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """获取选项流."""
        return TPLinkIPCOptionsFlowHandler(config_entry)


class TPLinkIPCOptionsFlowHandler(config_entries.OptionsFlow):
    """处理配置入口选项的类."""

    def __init__(self, config_entry) -> None:
        """初始化选项流处理器."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """管理选项流的入口."""
        return await self.async_step_edit()

    async def async_step_edit(self, user_input=None):
        """处理用户编辑输入."""
        errors = {}
        if user_input is not None:
            self.hass.config_entries.async_update_entry(
                self.config_entry, data=user_input
            )
            return self.async_create_entry(title="", data={})

        previous_data = self.config_entry.data

        data_schema = vol.Schema(
            {
                vol.Required("ip", default=previous_data["ip"]): str,
                vol.Required("port", default=previous_data["port"]): int,
                vol.Required("username", default=previous_data["username"]): str,
                vol.Required("password", default=previous_data["password"]): str,
            }
        )

        return self.async_show_form(
            step_id="edit", data_schema=data_schema, errors=errors
        )
