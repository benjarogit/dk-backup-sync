# -*- coding: utf-8 -*-
"""
Statische Favoriten: Lesen von favourites.xml aus addon_data/.../Static Favourites/<folder>/.
Nutzt core.config und core.kodi_api.
"""
import os
import re
from core import config
from core import kodi_api

STATIC_FAVOURITES_BASENAME = 'Static Favourites'


def get_static_favourites_path():
    """Absoluter Pfad zum Static Favourites-Basisordner."""
    profile = kodi_api.translate_path(config.ADDON.getAddonInfo('profile'))
    return os.path.join(profile, STATIC_FAVOURITES_BASENAME)


def get_folder_path(folder_name):
    """Absoluter Pfad zum Ordner (z.B. .../Static Favourites/Anime)."""
    base = get_static_favourites_path()
    return os.path.join(base, folder_name.strip())


def get_favourites_xml_path(folder_name):
    """Absoluter Pfad zu favourites.xml fuer den Ordner."""
    return os.path.join(get_folder_path(folder_name), 'favourites.xml')


def read_favourites(folder_name):
    """
    Liest favourites.xml fuer den Ordner; liefert [(name, thumb, command), ...].
    """
    path = get_favourites_xml_path(folder_name)
    if not path or not os.path.exists(path):
        return []
    try:
        with open(path, 'rb') as f:
            xml = f.read().decode('utf-8', errors='replace')
    except Exception:
        return []
    items = []
    for m in re.finditer(r'<favourite\s+([^>]+)>(.*?)</favourite>', xml, re.DOTALL):
        attrs, body = m.group(1), m.group(2).strip()
        name = ''
        thumb = ''
        for attr in re.finditer(r'(\w+)="([^"]*)"', attrs):
            key, val = attr.group(1).lower(), attr.group(2)
            if key == 'name':
                name = val.replace('&quot;', '"').replace('&amp;', '&')
            elif key == 'thumb':
                thumb = val.replace('&quot;', '"').replace('&amp;', '&')
        cmd = body.replace('&quot;', '"').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
        if name or cmd:
            items.append((name or 'Item', thumb, cmd))
    return items
