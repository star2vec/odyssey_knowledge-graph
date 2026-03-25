"""Stage 2: Entity and relation type definitions for the Odyssey KG."""
from enum import Enum


class EntityType(str, Enum):
    CHARACTER = "CHARACTER"
    DEITY = "DEITY"
    CREATURE = "CREATURE"
    LOCATION = "LOCATION"
    ARTIFACT = "ARTIFACT"
    EVENT = "EVENT"


class RelationType(str, Enum):
    # Family / kinship
    PARENT_OF = "PARENT_OF"
    CHILD_OF = "CHILD_OF"
    MARRIED_TO = "MARRIED_TO"

    # Combat / violence
    KILLS = "KILLS"
    WOUNDS = "WOUNDS"
    BLINDS = "BLINDS"

    # Journey / geography
    TRAVELS_TO = "TRAVELS_TO"
    DEPARTS_FROM = "DEPARTS_FROM"
    LOCATED_IN = "LOCATED_IN"

    # Divine / identity
    PROTECTS = "PROTECTS"
    PUNISHES = "PUNISHES"
    DISGUISES_AS = "DISGUISES_AS"
    RECOGNIZES = "RECOGNIZES"
    ENCHANTS = "ENCHANTS"
    DETAINS = "DETAINS"
