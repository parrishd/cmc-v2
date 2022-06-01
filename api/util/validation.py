import re
from uuid import UUID


def isBool(item):
    return type(item) == bool


def isfloat(item):
    # A float is a float
    if isinstance(item, float):
        return True

    # Ints are okay
    if isinstance(item, int):
        return True

    # Detect leading white-spaces
    if len(item) != len(item.strip()):
        return False

    # Some strings can represent floats or ints ( i.e. a decimal )
    if isinstance(item, str):
        # regex matching
        int_pattern = re.compile("^[0-9]*$")
        float_pattern = re.compile("^[0-9]*.[0-9]*$")
        if float_pattern.match(item) or int_pattern.match(item):
            return True
        else:
            return False


def isint(item):
    # Int is an int
    if isinstance(item, int):
        return True

    # Detect leading white-spaces
    if len(item) != len(item.strip()):
        return False

    # Some strings can represent floats or ints ( i.e. a decimal )
    if isinstance(item, str):
        # regex matching
        int_pattern = re.compile("^[0-9]*$")
        if int_pattern.match(item):
            return True
        else:
            return False


def isUUID(item):
    try:
        _ = UUID(item, version=4)
        return True
    except ValueError:
        return False
