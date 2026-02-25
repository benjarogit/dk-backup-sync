# -*- coding: utf-8 -*-
"""Dialogs: confirmation, progress, text, result. Uses core.kodi_api."""
from core import config
from core import kodi_api
from core import logging_utils
from core import settings

ADDON = config.ADDON
L = settings.L
log = logging_utils.log


def show_confirm(title, message, yes_label=None, no_label=None):
    """Yes/no dialog. Returns True on Yes, otherwise False."""
    dialog = kodi_api.Dialog()
    title_s = (str(title or '').strip()) or ADDON.getAddonInfo('name')
    message_s = (str(message or '').strip()) or L(30146)
    kodi_api.sleep(300)
    return dialog.yesno(title_s, message_s,
        yeslabel=yes_label if yes_label is not None else L(30227),
        nolabel=no_label if no_label is not None else L(30228))


def show_result(title, message, sleep_before=200):
    """OK dialog with title and message."""
    dialog = kodi_api.Dialog()
    if sleep_before:
        kodi_api.sleep(sleep_before)
    message = str(message or '').strip() or L(30146)
    dialog.ok(title, message)


def show_text(title, text):
    """Scrollable text (textviewer)."""
    dialog = kodi_api.Dialog()
    dialog.textviewer(title, text or '')


def confirm_then_run(title, message, action, yeslabel=None, nolabel=None):
    """Yes/no; on Yes call action()."""
    if show_confirm(title, message, yes_label=yeslabel, no_label=nolabel):
        action()


def confirm_with_select_then_run(title, info_text, action_label, cancel_label, action):
    """
    Select dialog (oriented at skin DialogSelect.xml, list with Label/Label2):
    Entry 0 = info text, 1 = run action, 2 = cancel. On index 1, action() is called.
    """
    dialog = kodi_api.Dialog()
    choices = [
        (str(info_text or '').strip()) or L(30146),
        (str(action_label or '').strip()) or L(30227),
        (str(cancel_label or '').strip()) or L(30228),
    ]
    kodi_api.sleep(300)
    idx = dialog.select((str(title or '').strip()) or ADDON.getAddonInfo('name'), choices)
    if idx == 1:
        action()
