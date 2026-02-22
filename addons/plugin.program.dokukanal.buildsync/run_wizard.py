# -*- coding: utf-8 -*-
"""
Einstieg fuer Ersteinrichtungs-Assistenten. RunScript(Addon-ID, MODE) aus Einstellungen.
Delegiert an addon (action=...) oder startet Wizard ueber wizard_service.
"""
import sys
import os
import xbmc
addon_path = os.path.dirname(os.path.abspath(__file__))
if addon_path not in sys.path:
    sys.path.insert(0, addon_path)

from core import logging_utils
log = logging_utils.log

_PLUGIN_BASE = "plugin://plugin.program.dokukanal.buildsync/"

_DIRECT_RUN_MODES = frozenset([
    "sync_favourites_now", "test_connection", "test_connection_1", "test_connection_2", "test_connection_3",
    "test_image_sources", "backup", "restore", "autoclean", "install_skin",
])

_ACTION_MODES = {
    "sync_favourites_now": "action=sync_favourites_now",
    "test_connection": "action=test_connection",
    "test_connection_1": "action=test_connection&connection=1",
    "test_connection_2": "action=test_connection&connection=2",
    "test_connection_3": "action=test_connection&connection=3",
    "test_image_sources": "action=test_image_sources",
    "backup": "action=backup",
    "restore": "action=restore",
    "autoclean": "action=autoclean",
    "install_skin": "action=install_skin",
    "info": "action=info",
    "info_server": "action=info&topic=server",
    "info_ordner": "action=info&topic=ordner",
    "info_verbindung": "action=info&topic=verbindung",
    "info_backup": "action=info&topic=backup",
    "info_empfohlen": "action=info&topic=empfohlen",
    "info_dateimanager": "action=info&topic=dateimanager",
    "debug": "action=debug",
}


if __name__ == "__main__":
    log("run_wizard argv=%s" % list(sys.argv), xbmc.LOGDEBUG)
    mode = None
    for idx in (2, 1):
        if len(sys.argv) <= idx:
            continue
        raw = str(sys.argv[idx]).strip()
        if raw in _DIRECT_RUN_MODES:
            mode = raw
            break
        if raw in _ACTION_MODES:
            mode = raw
            break
    if mode and mode in _DIRECT_RUN_MODES:
        log("run_wizard dispatch RunPlugin action=%s" % mode, xbmc.LOGDEBUG)
        url = _PLUGIN_BASE + "?" + _ACTION_MODES.get(mode, "action=" + mode)
        xbmc.executebuiltin("RunPlugin(%s)" % url)
        sys.exit(0)
    for idx in (2, 1):
        if len(sys.argv) <= idx:
            continue
        mode = str(sys.argv[idx]).strip()
        if mode in _ACTION_MODES:
            url = _PLUGIN_BASE + "?" + _ACTION_MODES[mode]
            log("run_wizard dispatch RunPlugin %s" % url, xbmc.LOGDEBUG)
            xbmc.executebuiltin("RunPlugin(%s)" % url)
            sys.exit(0)
        if "plugin://" in mode and ("action=" in mode or "mode=" in mode):
            xbmc.executebuiltin("RunPlugin(%s)" % mode)
            sys.exit(0)
    log("run_wizard starting wizard", xbmc.LOGDEBUG)
    from services import wizard_service
    wizard_service.reset_and_run_wizard()
