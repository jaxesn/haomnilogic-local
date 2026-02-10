from __future__ import annotations

from dataclasses import dataclass
from typing import TypeVar

from pyomnilogic_local.models.mspconfig import (
    MSPBackyard,
    MSPBoW,
    MSPCSAD,
    MSPChlorinator,
    MSPChlorinatorEquip,
    MSPColorLogicLight,
    MSPFilter,
    MSPHeaterEquip,
    MSPPump,
    MSPRelay,
    MSPSchedule,
    MSPSensor,
    MSPVirtualHeater,
)
from pyomnilogic_local.models.telemetry import (
    TelemetryBackyard,
    TelemetryBoW,
    TelemetryCSAD,
    TelemetryChlorinator,
    TelemetryColorLogicLight,
    TelemetryFilter,
    TelemetryGroup,
    TelemetryHeater,
    TelemetryPump,
    TelemetryRelay,
    TelemetryValveActuator,
    TelemetryVirtualHeater,
)


TelemetryTypes = (
    TelemetryBackyard
    | TelemetryBoW
    | TelemetryCSAD
    | TelemetryChlorinator
    | TelemetryColorLogicLight
    | TelemetryFilter
    | TelemetryGroup
    | TelemetryHeater
    | TelemetryPump
    | TelemetryRelay
    | TelemetryValveActuator
    | TelemetryVirtualHeater
)


@dataclass
class EntityIndexData:
    msp_config: (
        MSPBackyard
        | MSPBoW
        | MSPCSAD
        | MSPChlorinator
        | MSPChlorinatorEquip
        | MSPColorLogicLight
        | MSPFilter
        | MSPHeaterEquip
        | MSPPump
        | MSPRelay
        | MSPSchedule
        | MSPSensor
        | MSPVirtualHeater
    )
    telemetry: TelemetryTypes | None


EntityIndexT = dict[int, EntityIndexData]


class EntityIndexBackyard(EntityIndexData):
    msp_config: MSPBackyard
    telemetry: TelemetryBackyard


class EntityIndexBodyOfWater(EntityIndexData):
    msp_config: MSPBoW
    telemetry: TelemetryBoW


class EntityIndexColorLogicLight(EntityIndexData):
    msp_config: MSPColorLogicLight
    telemetry: TelemetryColorLogicLight


class EntityIndexFilter(EntityIndexData):
    msp_config: MSPFilter
    telemetry: TelemetryFilter


class EntityIndexHeater(EntityIndexData):
    msp_config: MSPVirtualHeater
    telemetry: TelemetryVirtualHeater


class EntityIndexHeaterEquip(EntityIndexData):
    msp_config: MSPHeaterEquip
    telemetry: TelemetryHeater


class EntityIndexChlorinator(EntityIndexData):
    msp_config: MSPChlorinator
    telemetry: TelemetryChlorinator


class EntityIndexCSAD(EntityIndexData):
    msp_config: MSPCSAD
    telemetry: TelemetryCSAD


class EntityIndexChlorinatorEquip(EntityIndexData):
    msp_config: MSPChlorinatorEquip
    telemetry: TelemetryChlorinator


class EntityIndexPump(EntityIndexData):
    msp_config: MSPPump
    telemetry: TelemetryPump


class EntityIndexRelay(EntityIndexData):
    msp_config: MSPRelay
    telemetry: TelemetryRelay


class EntityIndexSensor(EntityIndexData):
    msp_config: MSPSensor
    telemetry: None


class EntityIndexValveActuator(EntityIndexData):
    msp_config: MSPRelay
    telemetry: TelemetryValveActuator


EntityIndexTypeVar = TypeVar(
    "EntityIndexTypeVar",
    EntityIndexBackyard,
    EntityIndexBodyOfWater,
    EntityIndexChlorinator,
    EntityIndexChlorinatorEquip,
    EntityIndexColorLogicLight,
    EntityIndexCSAD,
    EntityIndexFilter,
    EntityIndexHeater,
    EntityIndexHeaterEquip,
    EntityIndexPump,
    EntityIndexRelay,
    EntityIndexSensor,
    EntityIndexValveActuator,
)
