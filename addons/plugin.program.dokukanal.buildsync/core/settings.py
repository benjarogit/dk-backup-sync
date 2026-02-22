# -*- coding: utf-8 -*-
"""
Einstellungen lesen/schreiben und Lokalisierung.
get_string/get_bool mit Reparatur bei Invalid setting type (wie safe_get_*).
Optional ensure_settings_initialized aus settings_init.
"""
from core import config

ADDON = config.ADDON


def L(msg_id):
    """Lokalisierung: Addon-String anhand msg_id (z. B. 30144)."""
    return ADDON.getLocalizedString(msg_id)


def get_string(setting_id, default=''):
    """
    Liest String-Setting. Bei Fehler (z. B. Invalid setting type): Default zurückschreiben, dann default zurückgeben.
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
    """Schreibt String-Setting. Bei Fehler still."""
    try:
        ADDON.setSettingString(setting_id, str(value) if value is not None else '')
    except (TypeError, Exception):
        pass


def set_bool(setting_id, value):
    """Schreibt Bool-Setting. Bei Fehler still."""
    try:
        ADDON.setSettingBool(setting_id, bool(value))
    except (TypeError, Exception):
        pass


def ensure_settings_initialized():
    """Stellt sicher, dass settings_schema_version gesetzt ist und interne Settings lesbar sind."""
    try:
        current = ADDON.getSettingString("settings_schema_version") or ""
        if current == "1":
            _sync_skin_debug()
            return
    except (TypeError, Exception):
        pass
    try:
        ADDON.setSettingString("settings_schema_version", "1")
        ADDON.setSettingBool("skin_startup_default_set", False)
        _ensure_skin_debug_default()
        _sync_skin_debug()
    except Exception:
        pass


def _skin_installed():
    try:
        import xbmcaddon
        xbmcaddon.Addon("skin.dokukanal")
        return True
    except RuntimeError:
        return False


def _set_skin_debug(enabled):
    try:
        import xbmcaddon
        skin = xbmcaddon.Addon("skin.dokukanal")
        skin.setSettingBool("DebugInfo", bool(enabled))
    except Exception:
        pass


def _sync_skin_debug():
    """Übernimmt recommend_skin_debug in das Skin-Setting DebugInfo."""
    if not _skin_installed():
        return
    try:
        on = ADDON.getSettingBool("recommend_skin_debug")
        _set_skin_debug(on)
    except Exception:
        pass


def _ensure_skin_debug_default():
    """Beim ersten Start mit installiertem Skin: Debug standardmäßig an."""
    if not _skin_installed():
        return
    try:
        if ADDON.getSettingBool("skin_debug_default_done"):
            return
        ADDON.setSettingBool("recommend_skin_debug", True)
        _set_skin_debug(True)
        ADDON.setSettingBool("skin_debug_default_done", True)
    except Exception:
        pass
