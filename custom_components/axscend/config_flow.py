"""Adds config flow for Axscend."""

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_API_TOKEN
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_create_clientsession
import aiohttp

from .api import (
    AxscendApiClient,
    AxscendApiClientAuthenticationError,
    AxscendApiClientCommunicationError,
    AxscendApiClientError,
)
from .const import CONF_ASSET_ID, DOMAIN, LOGGER


class AxscendFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Axscend."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the flow handler."""
        self._asset_name: str | None = None

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle a flow initialized by the user."""
        _errors = {}
        if user_input is not None:
            try:
                await self._test_credentials(
                    api_token=user_input[CONF_API_TOKEN],
                    asset_id=user_input[CONF_ASSET_ID],
                )
            except AxscendApiClientAuthenticationError as exception:
                LOGGER.warning(exception)
                _errors["base"] = "auth"
            except AxscendApiClientCommunicationError as exception:
                LOGGER.error(exception)
                _errors["base"] = "connection"
            except AxscendApiClientError as exception:
                LOGGER.exception(exception)
                _errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(
                    ## Do NOT use this in production code
                    ## The unique_id should never be something that can change
                    ## https://developers.home-assistant.io/docs/config_entries_config_flow_handler#unique-ids
                    unique_id=user_input[CONF_ASSET_ID]
                )
                self._abort_if_unique_id_configured()
                title = (
                    f"Axscend Asset '{self._asset_name}' ({user_input[CONF_ASSET_ID]})"
                )
                return self.async_create_entry(
                    title=title,
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_API_TOKEN,
                        default=(user_input or {}).get(CONF_API_TOKEN, vol.UNDEFINED),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.PASSWORD,
                        ),
                    ),
                    vol.Required(
                        CONF_ASSET_ID,
                        default=(user_input or {}).get(CONF_ASSET_ID, vol.UNDEFINED),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT,
                        ),
                    ),
                },
            ),
            errors=_errors,
        )

    async def _test_credentials(self, api_token: str, asset_id: str) -> None:
        """Validate credentials and fetch asset details."""
        # Use ThreadedResolver to avoid aiodns compatibility issues with Python 3.13
        connector = aiohttp.TCPConnector(resolver=aiohttp.resolver.ThreadedResolver())
        session = aiohttp.ClientSession(connector=connector)
        try:
            client = AxscendApiClient(
                api_token=api_token,
                session=session,
            )
            response = await client.async_get_asset(asset_id=asset_id)
            # Extract asset name from response
            self._asset_name = response.get("asset", {}).get("name", asset_id)
        finally:
            await session.close()
