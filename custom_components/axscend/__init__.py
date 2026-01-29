"""
Custom integration to integrate homeassistant_axscend with Home Assistant.

For more details about this integration, please refer to
https://github.com/robgaskell/homeassistant_axscend
"""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

import aiohttp
from homeassistant.const import CONF_API_TOKEN, Platform
from homeassistant.loader import async_get_loaded_integration

from .api import AxscendApiClient
from .const import CONF_ASSET_ID, DOMAIN, LOGGER
from .coordinator import AxscendDataUpdateCoordinator
from .data import AxscendData

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import AxscendConfigEntry

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
]


# https://developers.home-assistant.io/docs/config_entries_index/#setting-up-an-entry
async def async_setup_entry(
    hass: HomeAssistant,
    entry: AxscendConfigEntry,
) -> bool:
    """Set up this integration using UI."""
    coordinator = AxscendDataUpdateCoordinator(
        hass=hass,
        logger=LOGGER,
        name=DOMAIN,
        update_interval=timedelta(minutes=5),
    )
    # Create a dedicated session using ThreadedResolver to avoid aiodns issues
    connector = aiohttp.TCPConnector(resolver=aiohttp.resolver.ThreadedResolver())
    # Create a dedicated ClientSession instead of using Home Assistant helper
    # to avoid passing connector twice into aiohttp.ClientSession
    session = aiohttp.ClientSession(connector=connector)

    entry.runtime_data = AxscendData(
        client=AxscendApiClient(
            api_token=entry.data[CONF_API_TOKEN],
            session=session,
        ),
        asset_id=entry.data[CONF_ASSET_ID],
        integration=async_get_loaded_integration(hass, entry.domain),
        coordinator=coordinator,
        session=session,
    )

    # https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: AxscendConfigEntry,
) -> bool:
    """Handle removal of an entry."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        # Close our dedicated aiohttp session
        try:
            await entry.runtime_data.session.close()
        except aiohttp.ClientError:
            LOGGER.exception("Error closing client session for %s", entry.entry_id)
    return unloaded


async def async_reload_entry(
    hass: HomeAssistant,
    entry: AxscendConfigEntry,
) -> None:
    """Reload config entry."""
    await hass.config_entries.async_reload(entry.entry_id)
