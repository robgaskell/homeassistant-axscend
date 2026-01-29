"""Sensor platform for homeassistant_axscend."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)

from .entity import IntegrationBlueprintEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import AxscendDataUpdateCoordinator
    from .data import AxscendConfigEntry

ENTITY_DESCRIPTIONS = (
    SensorEntityDescription(
        key="asset_name",
        name="Asset Name",
        icon="mdi:tag",
    ),
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
    SensorEntityDescription(
        key="last_movement",
        name="Last Movement",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:clock",
    ),
    SensorEntityDescription(
        key="last_position",
        name="Last Position",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:clock",
    ),
    SensorEntityDescription(
        key="battery",
        name="Battery Level",
        device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement="%",
        state_class=SensorStateClass.MEASUREMENT,
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

    def _get_battery_value(self, batt: str | int | None) -> int | float | None:
        """Convert battery value to int or float."""
        if batt is None:
            return None
        try:
            return int(batt)
        except (TypeError, ValueError):
            try:
                return float(batt)
            except (TypeError, ValueError):
                return None

    def _get_timestamp_iso8601(self, timestamp_str: str | None) -> datetime | None:
        """Convert timestamp from 'YYYY-MM-DD HH:MM:SS' to datetime object."""
        if not timestamp_str:
            return None
        try:
            # Parse the timestamp in the format "2026-01-29 21:23:24"
            # Return as timezone-aware datetime in UTC
            return datetime.strptime(str(timestamp_str), "%Y-%m-%d %H:%M:%S").replace(
                tzinfo=UTC
            )
        except (ValueError, TypeError):
            return None

    def _get_value_for_key(
        self, asset_data: dict, key: str
    ) -> str | int | float | datetime | None:
        """Extract the appropriate value from asset data based on key."""
        extractors = {
            "asset_name": lambda: asset_data.get("name")
            if asset_data.get("name")
            else None,
            "latitude": lambda: str(asset_data.get("gps_latitude"))
            if asset_data.get("gps_latitude")
            else None,
            "longitude": lambda: str(asset_data.get("gps_longitude"))
            if asset_data.get("gps_longitude")
            else None,
            "last_movement": lambda: self._get_timestamp_iso8601(
                asset_data.get("last_movement_timestamp")
            ),
            "last_position": lambda: self._get_timestamp_iso8601(
                asset_data.get("last_position_timestamp")
            ),
            "battery": lambda: self._get_battery_value(asset_data.get("batt_percent")),
        }
        return extractors.get(key, lambda: None)()

    @property
    def native_value(self) -> str | int | float | datetime | None:
        """Return the native value of the sensor."""
        if not self.coordinator.data:
            return None

        asset_data = self.coordinator.data.get("asset", {})
        return self._get_value_for_key(asset_data, self.entity_description.key)
