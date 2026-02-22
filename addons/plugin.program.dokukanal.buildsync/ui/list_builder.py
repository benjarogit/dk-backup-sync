# -*- coding: utf-8 -*-
"""
Plugin-Listen: add_item, add_category_item, end_of_directory, set_plugin_category.
Benötigt Handle und ADDON_URL aus Aufrufer; nur für Plugin-Listen (nicht für Service).

Darstellung (Farben, Fett): Die Anzeige von ListItem-Labels (und optional setLabel2)
hängt vom Skin ab. Manche Skins unterstützen [B]…[/B] in Labels; eine optische Abhebung
(Einstellungen, Aktionen) ist nur dann sichtbar, wenn der Skin es rendert.
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
    Fügt einen Blatt-Eintrag zur Plugin-Liste hinzu.
    action: action=... (z. B. backup, restore). kwargs werden als URL-Parameter angehängt.
    """
    if icon is None:
        icon = ICON
    url = "%s/?action=%s" % (ADDON_URL, action)
    if kwargs:
        url += "&" + "&".join("%s=%s" % (k, urllib.parse.quote_plus(str(v))) for k, v in kwargs.items())
    li = kodi_api.ListItem(label)
    li.setArt({'icon': icon})
    kodi_api.add_directory_item(handle=handle, url=url, listitem=li, is_folder=False)


def add_category_item(handle, label, category_name, icon=None):
    """Fügt einen Kategorie-Ordner zur Plugin-Liste hinzu."""
    url = "%s/?action=category&name=%s" % (ADDON_URL, urllib.parse.quote(category_name, safe=''))
    li = kodi_api.ListItem(label)
    li.setArt({'icon': icon or ICON})
    kodi_api.add_directory_item(handle=handle, url=url, listitem=li, is_folder=True)


def end_of_directory(handle):
    """Schließt die Plugin-Liste (nur bei handle >= 0)."""
    if handle >= 0:
        kodi_api.end_of_directory(handle)


def set_plugin_category(handle, category):
    """Setzt die Kategorie der aktuellen Liste."""
    if handle >= 0:
        kodi_api.set_plugin_category(handle, category)
