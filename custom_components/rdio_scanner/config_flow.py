"""Config flow for Rdio Scanner."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_URL
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import RdioScannerClient, RdioScannerClientError, normalize_url
from .const import CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL, DEFAULT_URL, DOMAIN


class RdioScannerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Rdio Scanner."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            url = normalize_url(user_input[CONF_URL])
            password = user_input.get(CONF_PASSWORD) or None

            await self.async_set_unique_id(url)
            self._abort_if_unique_id_configured()

            client = RdioScannerClient(async_get_clientsession(self.hass), url, password)

            try:
                await client.async_test_connection()
            except RdioScannerClientError:
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(
                    title="Rdio Scanner",
                    data={CONF_URL: url, CONF_PASSWORD: password},
                    options={
                        CONF_SCAN_INTERVAL: user_input.get(
                            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                        )
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_URL, default=DEFAULT_URL): str,
                    vol.Optional(CONF_PASSWORD): str,
                    vol.Optional(
                        CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
                    ): vol.All(vol.Coerce(int), vol.Range(min=10, max=3600)),
                }
            ),
            errors=errors,
        )

    @staticmethod
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> RdioScannerOptionsFlow:
        """Create the options flow."""
        return RdioScannerOptionsFlow(config_entry)


class RdioScannerOptionsFlow(config_entries.OptionsFlow):
    """Handle options for Rdio Scanner."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize the options flow."""
        self._config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        """Manage integration options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_scan_interval = self._config_entry.options.get(
            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
        )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_SCAN_INTERVAL, default=current_scan_interval
                    ): vol.All(vol.Coerce(int), vol.Range(min=10, max=3600)),
                }
            ),
        )
