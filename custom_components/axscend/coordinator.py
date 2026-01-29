"""DataUpdateCoordinator for homeassistant_axscend."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    AxscendApiClientAuthenticationError,
    AxscendApiClientError,
)
from .const import LOGGER

if TYPE_CHECKING:
    from .data import AxscendConfigEntry


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class AxscendDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    config_entry: AxscendConfigEntry

    async def _async_update_data(self) -> Any:
        """Update data via library."""
        try:
            response = await self.config_entry.runtime_data.client.async_get_asset(
                asset_id=self.config_entry.runtime_data.asset_id
            )
            LOGGER.debug("Coordinator fetched data: %s", response)
        except AxscendApiClientAuthenticationError as exception:
            LOGGER.warning("Authentication failed during update: %s", exception)
            raise ConfigEntryAuthFailed(exception) from exception
        except AxscendApiClientError as exception:
            LOGGER.error("API error during update: %s", exception)
            raise UpdateFailed(exception) from exception
        else:
            return response
