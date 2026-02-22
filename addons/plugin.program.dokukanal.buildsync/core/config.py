# -*- coding: utf-8 -*-
"""
Addon-Konfiguration: ADDON-Objekt, IDs, Pfade, Konstanten.
Extrahiert aus resources.lib.common; keine xbmc*-Aufrufe außer über zentrales Addon-Objekt.
"""
import xbmcaddon
import xbmcvfs

ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo('id')
ADDON_PATH = xbmcvfs.translatePath(ADDON.getAddonInfo('path'))

HOME = xbmcvfs.translatePath('special://home')
USERDATA = xbmcvfs.translatePath('special://userdata')
TEMP = xbmcvfs.translatePath('special://temp')
ADDON_DATA = xbmcvfs.translatePath('special://userdata/addon_data/%s' % ADDON_ID)

ICON_PATH = ADDON_PATH + '/resources/images/icon.png'
