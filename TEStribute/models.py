"""
Object models for representing nested, dependent data structures.
"""
import enum


class Mode(enum.Enum):
    """
    Enumerator class for different TEStribute run modes.
    """
    random = -1
    cost = 0
    time = 1


# TODO: Implement classes that represent the following data structures:
# - "task_info" => better: make use of TES `tesTaskInfo` model with `bravado`
# - "object_info" => better: make use of DRS `Object` model with `bravado`
# - "combinations"
# - "ranked_services"