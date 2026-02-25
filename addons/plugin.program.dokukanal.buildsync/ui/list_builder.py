# -*- coding: utf-8 -*-
"""
Plugin lists: add_item, end_of_directory, set_plugin_category.
Requires handle and ADDON_URL from caller; for plugin lists only (not service).
Display (colors, bold): ListItem labels depend on skin; some skins support [B]…[/B].
"""
import urllib.parse
from core import config
from core import kodi_api

ADDON_ID = config.ADDON_ID
ADDON_PATH = config.ADDON_PATH
ADDON_URL = "plugin://%s" % ADDON_ID
ICON = ADDON_PATH + '/resources/images/icon.png'


def add_item(handle, label, action, icon=None, **kwargs):
    """
    Add a leaf entry to the plugin list.
    action: action=... (e.g. backup, restore). kwargs are appended as URL parameters.
    """
    if icon is None:
        icon = ICON
    url = "%s/?action=%s" % (ADDON_URL, action)
    if kwargs:
        url += "&" + "&".join("%s=%s" % (k, urllib.parse.quote_plus(str(v))) for k, v in kwargs.items())
    li = kodi_api.ListItem(label)
    li.setArt({'icon': icon})
    kodi_api.add_directory_item(handle=handle, url=url, listitem=li, is_folder=False)


def end_of_directory(handle):
    """Close the plugin list (only when handle >= 0)."""
    if handle >= 0:
        kodi_api.end_of_directory(handle)


def set_plugin_category(handle, category):
    """Set the category of the current list."""
    if handle >= 0:
        kodi_api.set_plugin_category(handle, category)
