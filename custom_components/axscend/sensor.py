"""Sensor platform for homeassistant_axscend."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription

from .entity import IntegrationBlueprintEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import AxscendDataUpdateCoordinator
    from .data import AxscendConfigEntry

ENTITY_DESCRIPTIONS = (
    SensorEntityDescription(
        key="latitude",
        name="Latitude",
        icon="mdi:latitude",
    ),
    SensorEntityDescription(
        key="longitude",
        name="Longitude",
        icon="mdi:longitude",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: AxscendConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    async_add_entities(
        AxscendAssetSensor(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class AxscendAssetSensor(IntegrationBlueprintEntity, SensorEntity):
    """Axscend Asset Sensor class."""

    def __init__(
        self,
        coordinator: AxscendDataUpdateCoordinator,
        entity_description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        asset_id = coordinator.config_entry.runtime_data.asset_id
        # Ensure unique ID per entity
        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_{asset_id}_{entity_description.key}"
        )

    @property
    def native_value(self) -> str | None:
        """Return the native value of the sensor."""
        if not self.coordinator.data:
            return None

        asset_data = self.coordinator.data.get("asset", {})

        if self.entity_description.key == "latitude":
            return (
                str(asset_data.get("gps_latitude"))
                if asset_data.get("gps_latitude")
                else None
            )
        if self.entity_description.key == "longitude":
            return (
                str(asset_data.get("gps_longitude"))
                if asset_data.get("gps_longitude")
                else None
            )

        return None
