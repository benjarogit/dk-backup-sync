# -*- coding: utf-8 -*-
"""
Central module for actions with confirmation dialog.

Actions invoked from settings (test connection, save favourites, test image source) use
confirm_then_run here; the actual action shows its own progress and result dialog.
Uses resources.lib.common for ADDON, L, log.
"""
import xbmc
import xbmcgui

from resources.lib.common import ADDON, L, log


def confirm_then_run(title, message, action, yeslabel=None, nolabel=None):
    """
    Show yesno(title, message) with buttons. On Yes, action() is called.
    No progress or result dialog (for actions with their own UI, e.g. Backup/Restore).
    """
    dialog = xbmcgui.Dialog()
    title_s = (str(title or '').strip()) or ADDON.getAddonInfo('name')
    message_s = (str(message or '').strip()) or L(30146)
    xbmc.sleep(300)
    yes = dialog.yesno(
        title_s,
        message_s,
        yeslabel=yeslabel if yeslabel is not None else L(30227),
        nolabel=nolabel if nolabel is not None else L(30228),
    )
    if yes:
        action()
