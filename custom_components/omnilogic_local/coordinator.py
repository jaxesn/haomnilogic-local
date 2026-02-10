"""Example integration using DataUpdateCoordinator."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import TYPE_CHECKING

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from pyomnilogic_local.models.mspconfig import MSPConfig, OmniBase
from pyomnilogic_local.omnitypes import OmniType

if TYPE_CHECKING:
    from collections.abc import Iterable

    from homeassistant.core import HomeAssistant
    from pyomnilogic_local import OmniLogic

    from .types.entity_index import EntityIndexT


# Import diagnostic data to reproduce issues
SIMULATION = False
if SIMULATION:
    # This line is only used during development when simulating a pool with diagnostic data
    # Disable the pylint and mypy alerts that don't like it when this variable isn't defined
    pass

_LOGGER = logging.getLogger(__name__)


def device_walk(base: OmniBase | MSPConfig, bow_id: int = -1) -> Iterable[OmniBase]:
    for _key, value in base:
        if isinstance(value, OmniBase) and hasattr(value, "system_id"):
            device = value.without_subdevices()
            if bow_id != -1 and getattr(device, "bow_id", -1) == -1:
                device.bow_id = bow_id
            yield device

            child_bow_id = value.system_id if value.omni_type == OmniType.BOW else bow_id
            yield from device_walk(value, child_bow_id)
        if isinstance(value, list):
            for item in value:
                if isinstance(item, OmniBase) and hasattr(item, "system_id"):
                    device = item.without_subdevices()
                    if bow_id != -1 and getattr(device, "bow_id", -1) == -1:
                        device.bow_id = bow_id
                    yield device

                    child_bow_id = item.system_id if item.omni_type == OmniType.BOW else bow_id
                    yield from device_walk(item, child_bow_id)


class OmniLogicCoordinator(DataUpdateCoordinator["EntityIndexT"]):
    """Hayward OmniLogic API coordinator."""

    omni: OmniLogic

    def __init__(self, hass: HomeAssistant, omni: OmniLogic, scan_interval: int) -> None:
        """Initialize my coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            # Name of the data. For logging purposes.
            name="OmniLogic",
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=timedelta(seconds=scan_interval),
        )
        self.omni = omni

    async def _async_update_data(self) -> EntityIndexT:
        """Update data via library."""
        await self.omni.refresh(force=True)

        from .types.entity_index import EntityIndexData

        entities: EntityIndexT = {}
        for device in device_walk(self.omni.mspconfig):
            entities[device.system_id] = EntityIndexData(
                msp_config=device,
                telemetry=self.omni.telemetry.get_telem_by_systemid(device.system_id),
            )
        return entities
