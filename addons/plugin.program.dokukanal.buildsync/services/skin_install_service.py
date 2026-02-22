# -*- coding: utf-8 -*-
"""Skin-Installation: install_skin_or_show_info. Rueckgabe (bool, str)."""
from typing import Tuple
from core import config
from core import kodi_api
from core import settings

L = settings.L


def install_skin_or_show_info():
    """
    Prueft ob skin.dokukanal installiert ist; zeigt Info oder startet InstallAddon.
    Returns: (True, "bereits installiert") oder (False, "") nach Install-Befehl.
    """
    try:
        import xbmcaddon
        xbmcaddon.Addon('skin.dokukanal')
        return (True, L(30176))
    except RuntimeError:
        kodi_api.sleep(300)
        kodi_api.executebuiltin('InstallAddon(skin.dokukanal)')
        return (False, '')
