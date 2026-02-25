# -*- coding: utf-8 -*-
"""
Wrapper for all Kodi API calls (xbmc, xbmcgui, xbmcplugin, xbmcvfs).
Rest of addon imports only from core.kodi_api; no direct xbmc imports in services/ui.
"""
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmcvfs


def raw_log(msg, level=None):
    """Write one line to Kodi log (no prefix)."""
    if level is None:
        level = xbmc.LOGINFO
    xbmc.log(msg, level)


def sleep(ms):
    """Kodi sleep in milliseconds."""
    xbmc.sleep(ms)


def executebuiltin(cmd):
    """Execute a Kodi builtin command."""
    xbmc.executebuiltin(cmd)


def translate_path(special_path):
    """Translate special:// to absolute path."""
    return xbmcvfs.translatePath(special_path)


def get_addon():
    """Return the addon object (xbmcaddon.Addon)."""
    return xbmcaddon.Addon()


def get_info_label(label):
    """Read a Kodi info label."""
    return xbmc.getInfoLabel(label) or ''


def Dialog():
    """Create an xbmcgui.Dialog."""
    return xbmcgui.Dialog()


def DialogProgress():
    """Create an xbmcgui.DialogProgress."""
    return xbmcgui.DialogProgress()


def ListItem(label=''):
    """Create an xbmcgui.ListItem."""
    return xbmcgui.ListItem(label)


def add_directory_item(handle, url, listitem, is_folder=False):
    """Add an entry to the plugin list."""
    xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=listitem, isFolder=is_folder)


def end_of_directory(handle):
    """Close the plugin list."""
    xbmcplugin.endOfDirectory(handle)


def set_plugin_category(handle, category):
    """Set the plugin list category."""
    xbmcplugin.setPluginCategory(handle, category)


def set_content(handle, content):
    """Set the list content type (optional)."""
    try:
        xbmcplugin.setContent(handle, content)
    except Exception:
        pass
