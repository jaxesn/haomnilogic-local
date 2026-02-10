from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from pyomnilogic_local import Backyard, Bow, HeaterEquipment

from .const import DOMAIN, KEY_COORDINATOR
from .coordinator import OmniLogicCoordinator
from .entity import OmniLogicEntity
from .types.entity_index import EntityIndexBackyard, EntityIndexBodyOfWater, EntityIndexHeaterEquip

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback


_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up the switch platform."""
    coordinator: OmniLogicCoordinator = hass.data[DOMAIN][entry.entry_id][KEY_COORDINATOR]
    entities: list[BinarySensorEntity] = []
    _LOGGER.debug("Setting up binary_sensor platform")

    # Create a binary sensor entity indicating if we are in Service Mode
    entities.append(OmniLogicServiceModeBinarySensorEntity(coordinator=coordinator, equipment=coordinator.omni.backyard))

    # Create binary sensor entities for each piece of Heater-Equipment

    for _, _, heater_equipment in coordinator.omni.all_heater_equipment.items():
        entities.append(
            OmniLogicHeaterEquipBinarySensorEntity(
                coordinator=coordinator,
                equipment=heater_equipment,
            )
        )

    # Create flow binary sensors for each BoW
    for _, _, bow in coordinator.omni.backyard.bow.items():
        entities.append(
            OmniLogicFlowBinarySensorEntity(
                coordinator=coordinator,
                equipment=bow,
            )
        )

    _LOGGER.debug("Adding %s binary_sensor entities", len(entities))
    async_add_entities(entities)


class OmniLogicServiceModeBinarySensorEntity(OmniLogicEntity[Backyard, EntityIndexBackyard], BinarySensorEntity):
    _attr_name = "Service Mode"

    @property
    def available(self) -> bool:
        # This is one of the few things we can pull from the telemetry even if we are in service mode
        return True

    @property
    def is_on(self) -> bool:
        return self.equipment.is_ready


class OmniLogicHeaterEquipBinarySensorEntity(OmniLogicEntity[HeaterEquipment, EntityIndexHeaterEquip], BinarySensorEntity):
    """Expose a binary state via a sensor based on telemetry data."""

    device_class = BinarySensorDeviceClass.HEAT

    @property
    def icon(self) -> str | None:
        return "mdi:water-boiler" if self.is_on else "mdi:water-boiler-off"

    @property
    def name(self) -> str:
        return f"{self.equipment.name} Status"

    @property
    def is_on(self) -> bool:
        return self.equipment.is_on


class OmniLogicFlowBinarySensorEntity(OmniLogicEntity[Bow, EntityIndexBodyOfWater], BinarySensorEntity):
    """Expose a binary state via a sensor based on telemetry data."""

    @property
    def icon(self) -> str | None:
        return "mdi:water-check" if self.is_on else "mdi:water-remove"

    @property
    def name(self) -> str:
        return f"{self.equipment.name} Status"

    @property
    def is_on(self) -> bool | None:
        return self.equipment.flow
