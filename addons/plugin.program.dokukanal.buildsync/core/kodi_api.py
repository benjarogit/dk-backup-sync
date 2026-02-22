# -*- coding: utf-8 -*-
"""
Kapselung aller Kodi-Aufrufe (xbmc, xbmcgui, xbmcplugin, xbmcvfs).
Rest des Addons importiert nur aus core.kodi_api; keine direkten xbmc-Imports in services/ui.
"""
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmcvfs


def raw_log(msg, level=None):
    """Schreibt eine Zeile ins Kodi-Log (ohne Präfix)."""
    if level is None:
        level = xbmc.LOGINFO
    xbmc.log(msg, level)


def sleep(ms):
    """Kodi sleep in Millisekunden."""
    xbmc.sleep(ms)


def executebuiltin(cmd):
    """Führt einen Kodi-Builtin-Befehl aus."""
    xbmc.executebuiltin(cmd)


def translate_path(special_path):
    """Übersetzt special:// in absoluten Pfad."""
    return xbmcvfs.translatePath(special_path)


def get_addon():
    """Liefert das Addon-Objekt (xbmcaddon.Addon)."""
    return xbmcaddon.Addon()


def get_info_label(label):
    """Liest ein Kodi-Info-Label."""
    return xbmc.getInfoLabel(label) or ''


def Dialog():
    """Erstellt einen xbmcgui.Dialog."""
    return xbmcgui.Dialog()


def DialogProgress():
    """Erstellt einen xbmcgui.DialogProgress."""
    return xbmcgui.DialogProgress()


def ListItem(label=''):
    """Erstellt ein xbmcgui.ListItem."""
    return xbmcgui.ListItem(label)


def add_directory_item(handle, url, listitem, is_folder=False):
    """Fügt einen Eintrag zur Plugin-Liste hinzu."""
    xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=listitem, isFolder=is_folder)


def end_of_directory(handle):
    """Schließt die Plugin-Liste."""
    xbmcplugin.endOfDirectory(handle)


def set_plugin_category(handle, category):
    """Setzt die Kategorie der Plugin-Liste."""
    xbmcplugin.setPluginCategory(handle, category)


def set_content(handle, content):
    """Setzt den Inhaltstyp der Liste (optional)."""
    try:
        xbmcplugin.setContent(handle, content)
    except Exception:
        pass
