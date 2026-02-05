"""Custom types for axscend."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aiohttp import ClientSession
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .api import AxscendApiClient
    from .coordinator import AxscendDataUpdateCoordinator


type AxscendConfigEntry = ConfigEntry[AxscendData]


@dataclass
class AxscendData:
    """Data for the Axscend integration."""

    client: AxscendApiClient
    coordinator: AxscendDataUpdateCoordinator
    integration: Integration
    asset_id: str
    session: ClientSession
