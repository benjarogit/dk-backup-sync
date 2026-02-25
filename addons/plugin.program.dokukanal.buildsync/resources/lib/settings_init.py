# -*- coding: utf-8 -*-
"""
Initialize addon settings so getSetting* does not fail with Invalid setting type.
On first run or after schema update, hidden/internal settings get defaults.
"""
from resources.lib.common import ADDON

SCHEMA_VERSION = "1"


def ensure_settings_initialized():
    """Ensure settings_schema_version is set and internal settings are readable."""
    try:
        current = ADDON.getSettingString("settings_schema_version") or ""
        if current == SCHEMA_VERSION:
            return
    except (TypeError, Exception):
        pass
    try:
        ADDON.setSettingString("settings_schema_version", SCHEMA_VERSION)
        ADDON.setSettingBool("skin_startup_default_set", False)
    except Exception:
        pass
