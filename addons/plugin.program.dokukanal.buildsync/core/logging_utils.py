# -*- coding: utf-8 -*-
"""
Logging mit einheitlichem Präfix für alle Addon-Meldungen.
Nutzt core.kodi_api.raw_log; kein direkter xbmc-Import.
"""
from core import config
from core import kodi_api

LOG_PREFIX = "[DokuKanal BuildSync]"


def log(msg, level=1):
    """
    Schreibt eine Zeile ins Kodi-Log mit Addon-Präfix.
    level: xbmc.LOGDEBUG=0, LOGINFO=1, LOGWARNING=2, LOGERROR=3
    """
    kodi_api.raw_log("%s %s" % (LOG_PREFIX, msg), level)
