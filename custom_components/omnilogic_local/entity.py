from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Generic, TypeVar, cast

from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from pyomnilogic_local import (
    CSAD,
    Backyard,
    Bow,
    Chlorinator,
    ChlorinatorEquipment,
    ColorLogicLight,
    CSADEquipment,
    Filter,
    Group,
    Heater,
    HeaterEquipment,
    Pump,
    Relay,
    Schedule,
    Sensor,
)
from pyomnilogic_local.models.mspconfig import MSPConfig
from pyomnilogic_local.omnitypes import OmniType

from .const import BACKYARD_SYSTEM_ID, DOMAIN, MANUFACTURER
from .coordinator import OmniLogicCoordinator
from .models.entity_index import EntityIndexData, TelemetryTypes

T = TypeVar("T", bound=EntityIndexData)

_LOGGER = logging.getLogger(__name__)

EquipmentTypes = TypeVar(
    "EquipmentTypes",
    bound=CSAD
    | Backyard
    | Bow
    | Chlorinator
    | ChlorinatorEquipment
    | ColorLogicLight
    | CSADEquipment
    | Filter
    | Group
    | Heater
    | HeaterEquipment
    | Pump
    | Relay
    | Schedule
    | Sensor,
)


class OmniLogicEntity(CoordinatorEntity[OmniLogicCoordinator], Generic[EquipmentTypes, T]):
    _attr_has_entity_name = True

    equipment: EquipmentTypes
    coordinator: OmniLogicCoordinator

    def __init__(
        self,
        coordinator: OmniLogicCoordinator,
        context: EquipmentTypes | int,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator=coordinator, context=context if isinstance(context, int) else context.system_id)
        if isinstance(context, int):
            self.system_id = context
            self.equipment = cast("EquipmentTypes", self.coordinator.omni.get_equipment_by_id(self.system_id))
        else:
            self.equipment = context
            self.system_id = context.system_id

        if self.equipment is not None:
            self.bow_id = self.equipment.bow_id if self.equipment.bow_id is not None else -1
        else:
            # If the equipment isn't found in the library collections yet, we can fall back to the coordinator data
            try:
                self.bow_id = self.coordinator.data[self.system_id].msp_config.bow_id
                if self.bow_id is None:
                    self.bow_id = -1
            except (KeyError, AttributeError):
                self.bow_id = -1

        self._extra_state_attributes: dict[str, Any] = {}
        subclass_name = self.__class__.__name__
        equipment_name = self.equipment.name if self.equipment else "Unknown"
        omni_type = self.equipment.omni_type if self.equipment else "Unknown"
        _LOGGER.debug("Configuring %s for %s - SystemID: %s, Name: %s", subclass_name, omni_type, self.system_id, equipment_name)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        # When we handle an update from the coordinator, we want to update the equipment object which we are holding a reference to
        # as it is the most current data from the library.
        if self.system_id is not None:
            _LOGGER.debug("updating %s - %s: %s", self.system_id, self.equipment.name, self.equipment)
            self.equipment = cast("EquipmentTypes", self.coordinator.omni.get_equipment_by_id(self.system_id))
        self.async_write_ha_state()

    @property
    def data(self) -> T:
        """Returns the data for this entity from the coordinator."""
        return cast("T", self.coordinator.data[self.system_id])

    def get_system_config(self) -> MSPConfig:
        """Returns the system config for the coordinator."""
        return self.coordinator.omni.mspconfig

    def get_telemetry_by_systemid(self, system_id: int) -> TelemetryTypes | None:
        """Returns the telemetry for a specific system ID."""
        return self.coordinator.omni.telemetry.get_telem_by_systemid(system_id)

    def set_telemetry(self, telemetry: dict[str, Any]) -> None:
        """Updates the telemetry for this entity in the coordinator data."""
        # This is a bit of a hack to update the local state before the next refresh
        for key, value in telemetry.items():
            setattr(self.data.telemetry, key, value)
        self.async_write_ha_state()

    def set_config(self, config: dict[str, Any]) -> None:
        """Updates the config for this entity in the coordinator data."""
        for key, value in config.items():
            setattr(self.data.msp_config, key, value)
        self.async_write_ha_state()

    @property
    def available(self) -> bool:
        _LOGGER.debug("available %s - %s: %s. %s", self.system_id, self.equipment.name, self.equipment.is_ready, self.equipment.telemetry)

        # Sensors (air/water temp) do not have their own telemetry object;
        # their data comes from Backyard/BodyOfWater telemetry.
        # So we skip the telemetry check for them.
        if self.equipment.omni_type == OmniType.SENSOR:
            return True

        if (hasattr(self.equipment, "telemetry") and self.equipment.telemetry is None) or not self.equipment.is_ready:
            return False
        return True

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        # If we have a BOW ID, then we associate with that BOWs device, if not, we associate with the Backyard
        if self.equipment.bow_id is not None and self.equipment.bow_id != -1:
            identifiers = {(DOMAIN, f"bow_{self.bow_id}")}
        else:
            identifiers = {(DOMAIN, f"backyard_{BACKYARD_SYSTEM_ID}")}
        return DeviceInfo(
            identifiers=identifiers,
            manufacturer=MANUFACTURER,
        )

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        base_attributes: dict[str, Any] = {
            "omni_system_id": self.system_id,
            "omni_bow_id": self.bow_id,
        }
        return self._extra_state_attributes | base_attributes

    @property
    def name(self) -> Any:
        return self._attr_name if hasattr(self, "_attr_name") else self.equipment.name

    @property
    def unique_id(self) -> str | None:
        return f"{self.bow_id} {self.system_id} {self.name}"

    # @callback
    async def _schedule_refresh_callback(self, now: datetime) -> None:
        """Callback function executed by async_call_later."""
        # `now` is the timestamp argument required by async_call_later callbacks

        # Use the non-blocking version of the refresh request
        await self.coordinator.async_request_refresh()
