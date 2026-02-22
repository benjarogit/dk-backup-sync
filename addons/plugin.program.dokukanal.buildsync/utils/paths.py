# -*- coding: utf-8 -*-
"""Path helpers: special://, join with USERDATA, etc."""
from core import config

USERDATA = config.USERDATA
ADDON_DATA = config.ADDON_DATA
HOME = config.HOME


def join_userdata(*parts):
    """Join path parts under USERDATA."""
    import os
    return os.path.join(USERDATA, *parts)


def join_addon_data(*parts):
    """Join path parts under ADDON_DATA."""
    import os
    return os.path.join(ADDON_DATA, *parts)
