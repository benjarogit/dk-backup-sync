# -*- coding: utf-8 -*-
"""
Read/write settings and localization.
get_string/get_bool repair on Invalid setting type (like safe_get_*).
Optional ensure_settings_initialized from settings_init.
"""
from core import config

ADDON = config.ADDON


def L(msg_id):
    """Localization: addon string by msg_id (e.g. 30144)."""
    return ADDON.getLocalizedString(msg_id)


def get_string(setting_id, default=''):
    """
    Read string setting. On error (e.g. Invalid setting type): write default back, then return default.
    """
    try:
        return ADDON.getSettingString(setting_id) or default
    except (TypeError, Exception):
        try:
            ADDON.setSettingString(setting_id, default)
        except Exception:
            pass
        return default


def get_bool(setting_id, default=False):
    """
    Liest Bool-Setting. Bei Fehler: Default zurückschreiben, dann default zurückgeben.
    """
    try:
        return ADDON.getSettingBool(setting_id)
    except (TypeError, Exception):
        try:
            ADDON.setSettingBool(setting_id, default)
        except Exception:
            pass
        return default


def set_string(setting_id, value):
    """Write string setting. On error: silent."""
    try:
        ADDON.setSettingString(setting_id, str(value) if value is not None else '')
    except (TypeError, Exception):
        pass


def set_bool(setting_id, value):
    """Write bool setting. On error: silent."""
    try:
        ADDON.setSettingBool(setting_id, bool(value))
    except (TypeError, Exception):
        pass


def ensure_settings_initialized():
    """Ensure settings_schema_version is set and internal settings are readable."""
    try:
        current = ADDON.getSettingString("settings_schema_version") or ""
        if current == "1":
            return
    except (TypeError, Exception):
        pass
    try:
        ADDON.setSettingString("settings_schema_version", "1")
        ADDON.setSettingBool("skin_startup_default_set", False)
    except Exception:
        pass
