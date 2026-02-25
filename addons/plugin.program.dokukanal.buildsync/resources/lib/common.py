# -*- coding: utf-8 -*-
"""
Shared addon base – single place for all modules.

Modules can use: ADDON, ADDON_ID, ADDON_PATH; L(msg_id) for localization;
log(msg, level) with unified prefix; safe_get_string/safe_get_bool for settings (with repair on error);
paths: HOME, USERDATA, TEMP, ADDON_DATA.
No xbmcplugin; only xbmc/xbmcaddon/xbmcvfs – usable from service, plugin and all libs.
"""
import xbmc
import xbmcaddon
import xbmcvfs

# Addon object and base info (once per addon)
ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo('id')
ADDON_PATH = xbmcvfs.translatePath(ADDON.getAddonInfo('path'))

# Kodi paths (backup, AutoClean, favourites, etc.)
HOME = xbmcvfs.translatePath('special://home')
USERDATA = xbmcvfs.translatePath('special://userdata')
TEMP = xbmcvfs.translatePath('special://temp')
ADDON_DATA = xbmcvfs.translatePath('special://userdata/addon_data/%s' % ADDON_ID)

LOG_PREFIX = "[DokuKanal BuildSync]"


def L(msg_id):
    """Localization: addon string by msg_id (e.g. 30144)."""
    return ADDON.getLocalizedString(msg_id)


def log(msg, level=xbmc.LOGINFO):
    """Log with unified prefix."""
    xbmc.log("%s %s" % (LOG_PREFIX, msg), level)


def safe_get_string(setting_id, default=''):
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


def safe_get_bool(setting_id, default=False):
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


def safe_set_string(setting_id, value):
    """Write string setting. On error: silent."""
    try:
        ADDON.setSettingString(setting_id, str(value) if value is not None else '')
    except (TypeError, Exception):
        pass


def safe_set_bool(setting_id, value):
    """Write bool setting. On error: silent."""
    try:
        ADDON.setSettingBool(setting_id, bool(value))
    except (TypeError, Exception):
        pass
