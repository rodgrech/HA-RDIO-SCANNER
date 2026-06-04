"""Sensors for Rdio Scanner."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import RdioScannerData
from .const import DOMAIN
from .coordinator import RdioScannerDataUpdateCoordinator


@dataclass(frozen=True, kw_only=True)
class RdioScannerSensorDescription(SensorEntityDescription):
    """Describe a Rdio Scanner sensor."""

    value_fn: Callable[[RdioScannerData], Any]


SENSORS: tuple[RdioScannerSensorDescription, ...] = (
    RdioScannerSensorDescription(
        key="status",
        name="Status",
        translation_key="status",
        value_fn=lambda data: "Connected" if data.connected else "Disconnected",
    ),
    RdioScannerSensorDescription(
        key="url",
        name="URL",
        translation_key="url",
        value_fn=lambda data: data.url,
    ),
    RdioScannerSensorDescription(
        key="branding",
        name="Branding",
        translation_key="branding",
        value_fn=lambda data: data.branding,
    ),
    RdioScannerSensorDescription(
        key="email",
        name="Email",
        translation_key="email",
        value_fn=lambda data: data.email,
    ),
    RdioScannerSensorDescription(
        key="systems",
        name="Systems",
        translation_key="systems",
        value_fn=lambda data: data.systems_count,
    ),
    RdioScannerSensorDescription(
        key="talkgroups",
        name="Talkgroups",
        translation_key="talkgroups",
        value_fn=lambda data: data.talkgroups_count,
    ),
    RdioScannerSensorDescription(
        key="groups",
        name="Groups",
        translation_key="groups",
        value_fn=lambda data: data.groups_count,
    ),
    RdioScannerSensorDescription(
        key="tags",
        name="Tags",
        translation_key="tags",
        value_fn=lambda data: data.tags_count,
    ),
    RdioScannerSensorDescription(
        key="admin_configured",
        name="Admin configured",
        translation_key="admin_configured",
        value_fn=lambda data: "Yes" if data.admin_configured else "No",
    ),
    RdioScannerSensorDescription(
        key="admin_error",
        name="Admin error",
        translation_key="admin_error",
        value_fn=lambda data: data.admin_error,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Rdio Scanner sensors."""
    coordinator: RdioScannerDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        RdioScannerSensor(coordinator, entry, description) for description in SENSORS
    )


class RdioScannerSensor(CoordinatorEntity[RdioScannerData], SensorEntity):
    """Rdio Scanner sensor."""

    entity_description: RdioScannerSensorDescription

    def __init__(
        self,
        coordinator: RdioScannerDataUpdateCoordinator,
        entry: ConfigEntry,
        description: RdioScannerSensorDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_has_entity_name = True
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "Rdio Scanner",
            "manufacturer": "Rdio Scanner",
            "model": "Local scanner server",
        }

    @property
    def native_value(self) -> Any:
        """Return the sensor value."""
        if self.coordinator.data is None:
            return None

        return self.entity_description.value_fn(self.coordinator.data)
