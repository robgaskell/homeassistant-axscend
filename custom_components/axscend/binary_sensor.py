"""Binary sensor platform for axscend."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)

from .entity import IntegrationBlueprintEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import AxscendDataUpdateCoordinator
    from .data import AxscendConfigEntry

ENTITY_DESCRIPTIONS = (
    BinarySensorEntityDescription(
        key="at_home",
        name="At Home",
        device_class=BinarySensorDeviceClass.PRESENCE,
    ),
)


def _haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two GPS coordinates in meters.

    Uses Haversine formula.
    """
    r = 6371000  # Earth's radius in meters

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return r * c


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AxscendConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the binary_sensor platform."""
    async_add_entities(
        AxscendAtHomeBinarySensor(
            hass=hass,
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class AxscendAtHomeBinarySensor(IntegrationBlueprintEntity, BinarySensorEntity):
    """Axscend binary_sensor class for home presence detection."""

    def __init__(
        self,
        hass: HomeAssistant,
        coordinator: AxscendDataUpdateCoordinator,
        entity_description: BinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary_sensor class."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self.hass = hass
        asset_id = coordinator.config_entry.runtime_data.asset_id
        # Ensure unique ID per entity
        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_{asset_id}_{entity_description.key}"
        )

    @property
    def is_on(self) -> bool:
        """Return true if the asset is within the home location radius."""
        if not self.coordinator.data:
            return False

        # Get Home Assistant home location
        home_latitude = self.hass.config.latitude
        home_longitude = self.hass.config.longitude

        if home_latitude is None or home_longitude is None:
            return False

        # Get home location radius from Home Assistant configuration
        # Default to 100m if not configured
        home_radius = (
            self.hass.config.radius if self.hass.config.radius is not None else 100
        )

        # Get asset GPS coordinates
        asset_data = self.coordinator.data.get("asset", {})

        asset_latitude = asset_data.get("gps_latitude")
        asset_longitude = asset_data.get("gps_longitude")

        if asset_latitude is None or asset_longitude is None:
            return False

        # Calculate distance
        distance = _haversine_distance(
            home_latitude, home_longitude, asset_latitude, asset_longitude
        )

        # Return true if within home location radius
        return distance <= home_radius
