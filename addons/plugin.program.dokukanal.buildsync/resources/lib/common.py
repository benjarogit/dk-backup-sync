# -*- coding: utf-8 -*-
"""
Gemeinsame Addon-Grundlagen – eine zentrale Stelle für alle Module.

Alle Module können hier zurückgreifen auf:
- ADDON, ADDON_ID, ADDON_PATH
- L(msg_id) für Lokalisierung
- log(msg, level) mit einheitlichem Präfix
- safe_get_string / safe_get_bool für Einstellungen (mit Reparatur bei Fehler)
- Pfade: HOME, USERDATA, TEMP, ADDON_DATA

Kein xbmcplugin, nur xbmc/xbmcaddon/xbmcvfs – nutzbar von Service, Plugin und allen Libs.
"""
import xbmc
import xbmcaddon
import xbmcvfs

# Addon-Objekt und Basis-Infos (einmal pro Addon)
ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo('id')
ADDON_PATH = xbmcvfs.translatePath(ADDON.getAddonInfo('path'))

# Kodi-Pfade (für Backup, AutoClean, Favourites etc.)
HOME = xbmcvfs.translatePath('special://home')
USERDATA = xbmcvfs.translatePath('special://userdata')
TEMP = xbmcvfs.translatePath('special://temp')
ADDON_DATA = xbmcvfs.translatePath('special://userdata/addon_data/%s' % ADDON_ID)

LOG_PREFIX = "[DokuKanal BuildSync]"


def L(msg_id):
    """Lokalisierung: Addon-String anhand msg_id (z. B. 30144)."""
    return ADDON.getLocalizedString(msg_id)


def log(msg, level=xbmc.LOGINFO):
    """Log mit einheitlichem Präfix."""
    xbmc.log("%s %s" % (LOG_PREFIX, msg), level)


def safe_get_string(setting_id, default=''):
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
    """Schreibt String-Setting. Bei Fehler still."""
    try:
        ADDON.setSettingString(setting_id, str(value) if value is not None else '')
    except (TypeError, Exception):
        pass


def safe_set_bool(setting_id, value):
    """Schreibt Bool-Setting. Bei Fehler still."""
    try:
        ADDON.setSettingBool(setting_id, bool(value))
    except (TypeError, Exception):
        pass
