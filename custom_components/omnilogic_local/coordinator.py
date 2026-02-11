"""Example integration using DataUpdateCoordinator."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import TYPE_CHECKING

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .utils import device_walk

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from pyomnilogic_local import OmniLogic

    from .models.entity_index import EntityIndexT


# Import diagnostic data to reproduce issues
SIMULATION = False
if SIMULATION:
    # This line is only used during development when simulating a pool with diagnostic data
    # Disable the pylint and mypy alerts that don't like it when this variable isn't defined
    pass

_LOGGER = logging.getLogger(__name__)


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
        await self.omni.refresh(force=False)

        from .models.entity_index import EntityIndexData

        entities: EntityIndexT = {}
        for device in device_walk(self.omni.mspconfig):
            entities[device.system_id] = EntityIndexData(
                msp_config=device,
                telemetry=self.omni.telemetry.get_telem_by_systemid(device.system_id),
            )
        _LOGGER.debug("OmniLogic reported %s devices in the entity index", len(entities))
        return entities
