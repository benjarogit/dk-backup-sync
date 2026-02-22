# -*- coding: utf-8 -*-
"""
Initialisierung der Addon-Settings, damit getSetting* nicht mit „Invalid setting type“ abbricht.
Beim ersten Lauf oder nach Schema-Update werden versteckte/ interne Settings mit Defaults belegt.
Sync: Empfehlung „Debug für Skin“ in Skin-Setting DebugInfo übernehmen.
"""
import xbmcaddon

from resources.lib.common import ADDON

SCHEMA_VERSION = "1"
SKIN_ID = "skin.dokukanal"


def _skin_installed():
    try:
        xbmcaddon.Addon(SKIN_ID)
        return True
    except RuntimeError:
        return False


def _set_skin_debug(enabled):
    try:
        skin = xbmcaddon.Addon(SKIN_ID)
        skin.setSettingBool("DebugInfo", bool(enabled))
    except Exception:
        pass


def _sync_recommend_skin_debug():
    """Übernimmt die Einstellung recommend_skin_debug in das Skin-Setting DebugInfo."""
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


def ensure_settings_initialized():
    """Stellt sicher, dass settings_schema_version gesetzt ist und interne Settings lesbar sind."""
    try:
        current = ADDON.getSettingString("settings_schema_version") or ""
        if current == SCHEMA_VERSION:
            _ensure_skin_debug_default()
            _sync_recommend_skin_debug()
            return
    except (TypeError, Exception):
        pass
    try:
        ADDON.setSettingString("settings_schema_version", SCHEMA_VERSION)
        ADDON.setSettingBool("skin_startup_default_set", False)
        _ensure_skin_debug_default()
        _sync_recommend_skin_debug()
    except Exception:
        pass
