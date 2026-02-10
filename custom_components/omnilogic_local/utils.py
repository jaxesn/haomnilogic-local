from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from pyomnilogic_local.models.mspconfig import MSPConfig, OmniBase
from pyomnilogic_local.omnitypes import OmniType

from .const import OMNI_TO_HASS_TYPES

if TYPE_CHECKING:
    from collections.abc import Iterable
    from .models.entity_index import EntityIndexT

_LOGGER = logging.getLogger(__name__)


def device_walk(base: OmniBase | MSPConfig, bow_id: int = -1) -> Iterable[OmniBase]:
    """Walk the OmniLogic device tree and yield individual devices with their bow_id."""
    for _key, value in base:
        if isinstance(value, OmniBase) and hasattr(value, "system_id"):
            device = value.without_subdevices()
            if bow_id != -1 and getattr(device, "bow_id", -1) == -1:
                device.bow_id = bow_id
            _LOGGER.debug(
                "device_walk found device: %s (Type: %s, SystemID: %s, BOW ID: %s)",
                device.name if hasattr(device, "name") else "Unnamed",
                device.omni_type,
                device.system_id,
                device.bow_id,
            )
            yield device

            child_bow_id = value.system_id if value.omni_type == OmniType.BOW else bow_id
            yield from device_walk(value, child_bow_id)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, OmniBase) and hasattr(item, "system_id"):
                    device = item.without_subdevices()
                    if bow_id != -1 and getattr(device, "bow_id", -1) == -1:
                        device.bow_id = bow_id
                    _LOGGER.debug(
                        "device_walk found device from list: %s (Type: %s, SystemID: %s, BOW ID: %s)",
                        device.name if hasattr(device, "name") else "Unnamed",
                        device.omni_type,
                        device.system_id,
                        device.bow_id,
                    )
                    yield device

                    child_bow_id = item.system_id if item.omni_type == OmniType.BOW else bow_id
                    yield from device_walk(item, child_bow_id)


def get_entities_of_hass_type(entities: EntityIndexT, hass_type: str) -> EntityIndexT:
    found = {}
    for system_id, entity in entities.items():
        if OMNI_TO_HASS_TYPES[entity.msp_config.omni_type] == hass_type:
            found[system_id] = entity
    return found


def get_entities_of_omni_types(entities: EntityIndexT, omni_types: list[OmniType]) -> EntityIndexT:
    found = {}
    for system_id, entity in entities.items():
        if entity.msp_config.omni_type in omni_types:
            found[system_id] = entity
    return found
