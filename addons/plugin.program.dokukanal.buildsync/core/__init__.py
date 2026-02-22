# -*- coding: utf-8 -*-
"""
Core-Schicht: Konfiguration, Logging, Einstellungen, Kodi-API-Kapselung.
Alle Module importieren nur aus core (keine direkten xbmc*/xbmcaddon-Imports in services/ui).
"""
from core import config
from core import logging_utils
from core import settings
from core import kodi_api

__all__ = ['config', 'logging_utils', 'settings', 'kodi_api']
