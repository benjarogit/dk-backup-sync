# -*- coding: utf-8 -*-
"""Dialoge: Bestätigung, Fortschritt, Text, Ergebnis. Nutzt core.kodi_api."""
import xbmcgui

from core import config
from core import kodi_api
from core import logging_utils
from core import settings

ADDON = config.ADDON
L = settings.L
log = logging_utils.log


def show_confirm(title, message, yes_label=None, no_label=None):
    """yesno-Dialog. Gibt True bei Ja, sonst False zurueck."""
    dialog = kodi_api.Dialog()
    title_s = (str(title or '').strip()) or ADDON.getAddonInfo('name')
    message_s = (str(message or '').strip()) or L(30146)
    kodi_api.sleep(300)
    return dialog.yesno(title_s, message_s,
        yeslabel=yes_label if yes_label is not None else L(30227),
        nolabel=no_label if no_label is not None else L(30228))


def show_result(title, message, sleep_before=200):
    """OK-Dialog mit Titel und Nachricht."""
    dialog = kodi_api.Dialog()
    if sleep_before:
        kodi_api.sleep(sleep_before)
    message = str(message or '').strip() or L(30146)
    dialog.ok(title, message)


def show_text(title, text):
    """Scrollbarer Text (textviewer)."""
    dialog = kodi_api.Dialog()
    dialog.textviewer(title, text or '')


def show_ok(title, message):
    """Alias fuer show_result."""
    show_result(title, message)


def run_with_info_and_confirm(title, message, action, yeslabel=None, nolabel=None,
    success_title=None, error_title=None, progress_message=None):
    """yesno -> Progress waehrend action() -> Ergebnis-Dialog."""
    dialog = kodi_api.Dialog()
    title_s = (str(title or '').strip()) or ADDON.getAddonInfo('name')
    message_s = (str(message or '').strip()) or L(30146)
    kodi_api.sleep(300)
    if not dialog.yesno(title_s, message_s,
        yeslabel=yeslabel if yeslabel is not None else L(30227),
        nolabel=nolabel if nolabel is not None else L(30228)):
        return
    err_title = (str(error_title or '').strip()) or ADDON.getAddonInfo('name')
    succ_title = (str(success_title or '').strip()) or title_s
    progress_msg = (str(progress_message or '').strip()) or L(30300)
    progress = kodi_api.DialogProgress()
    progress.create(title_s, progress_msg)
    try:
        success, result_msg = action()
        try:
            progress.close()
        except Exception:
            pass
        result_msg = str(result_msg or '').strip() or L(30146)
        kodi_api.sleep(200)
        dialog_title = succ_title if success else L(30146)
        dialog.ok(dialog_title, result_msg)
    except Exception as e:
        try:
            progress.close()
        except Exception:
            pass
        from core import logging_utils
        logging_utils.log(str(e), 3)
        kodi_api.sleep(200)
        err_msg = str(e).strip() if e else L(30146)
        dialog.ok(err_title, err_msg if err_msg else L(30146))
    finally:
        try:
            progress.close()
        except Exception:
            pass


def confirm_then_run(title, message, action, yeslabel=None, nolabel=None):
    """yesno; bei Ja action() aufrufen."""
    if show_confirm(title, message, yes_label=yeslabel, no_label=nolabel):
        action()


class DialogConfirmWithInfo(xbmcgui.WindowXMLDialog):
    """
    Eigener Dialog: links Infotext (Textbox), rechts zwei oder drei Buttons.
    Ohne action_label_2: zwei Buttons (Aktion / Abbrechen), result True/False.
    Mit action_label_2: drei Buttons, result 0 (Button 5), 1 (Button 6), -1 (Button 7 / Back).
    """

    def __init__(self, *args, **kwargs):
        self._title = (str(kwargs.pop('title', '') or '')).strip() or ADDON.getAddonInfo('name')
        self._info_text = (str(kwargs.pop('info_text', '') or '')).strip() or L(30146)
        self._action_label = (str(kwargs.pop('action_label', '') or '')).strip() or L(30227)
        self._action_label_2 = kwargs.pop('action_label_2', None)
        if self._action_label_2 is not None:
            self._action_label_2 = (str(self._action_label_2 or '')).strip() or L(30227)
        self._cancel_label = (str(kwargs.pop('cancel_label', '') or '')).strip() or L(30228)
        self.result = False
        self._three_mode = False
        xbmcgui.WindowXMLDialog.__init__(self, *args)

    def onInit(self):
        self.getControl(1).setLabel(self._title)
        self.getControl(2).setText(self._info_text)
        self.getControl(5).setLabel(self._action_label)
        self.getControl(7).setLabel(self._cancel_label)
        try:
            c6 = self.getControl(6)
        except Exception as e:
            if self._action_label_2 is not None:
                log("DialogConfirmWithInfo: Control 6 nicht gefunden (%s) – Fallback" % e, 2)
                raise  # Fallback in show_confirm_three
            self._three_mode = False
        else:
            if self._action_label_2 is not None:
                self._three_mode = True
                c6.setLabel(self._action_label_2)
                c6.setVisible(True)
            else:
                c6.setVisible(False)
        self.setFocusId(5)

    def onClick(self, controlId):
        if controlId == 5:
            self.result = 0 if self._three_mode else True
            self.close()
        elif controlId == 6:
            self.result = 1
            self.close()
        elif controlId == 7:
            self.result = -1 if self._three_mode else False
            self.close()

    def onAction(self, action):
        aid = action.getId()
        if aid == xbmcgui.ACTION_PREVIOUS_MENU or aid == xbmcgui.ACTION_NAV_BACK:
            self.result = -1 if self._three_mode else False
            self.close()


def show_confirm_with_info(title, info_text, action_label, cancel_label):
    """
    Zeigt den Addon-Dialog DialogConfirmBuildSync (links Text, rechts zwei Buttons).
    Gibt True zurueck wenn Aktion gewaehlt, sonst False.
    Fallback: Bei Fehler (z. B. Skin ueberschreibt XML) wird yesno verwendet.
    """
    try:
        addon_path = ADDON.getAddonInfo('path')
        dialog = DialogConfirmWithInfo(
            'DialogConfirmBuildSync.xml', addon_path, 'Default', '1080i',
            title=title, info_text=info_text,
            action_label=action_label, cancel_label=cancel_label,
        )
        kodi_api.sleep(300)
        dialog.doModal()
        result = getattr(dialog, 'result', False)
        del dialog
        return result
    except Exception:
        return show_confirm(title, info_text, yes_label=action_label, no_label=cancel_label)


def confirm_with_info_then_run(title, info_text, action_label, cancel_label, action):
    """
    Zeigt show_confirm_with_info; bei True wird action() aufgerufen.
    Signatur wie confirm_with_select_then_run (Drop-in-Ersatz).
    """
    if show_confirm_with_info(title, info_text, action_label, cancel_label):
        action()


def confirm_with_select_then_run(title, info_text, action_label, cancel_label, action):
    """
    Select-Dialog (orientiert an Skin DialogSelect.xml, Liste mit Label/Label2):
    Eintrag 0 = Info-Text, 1 = Aktion ausfuehren, 2 = Abbrechen.
    Bei Wahl Index 1 wird action() aufgerufen.
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


def show_confirm_three(title, info_text, label1, label2, label_cancel):
    """
    Zeigt denselben Addon-Dialog wie show_confirm_with_info (Infotext links, Buttons rechts), mit drei Buttons.
    Gibt 0 (erster Button), 1 (zweiter Button) oder -1 (Abbrechen/Back) zurueck.
    Fallback nur bei Fehler: dialog.select (siehe Kodi-Log bei Problemen).
    """
    try:
        addon_path = ADDON.getAddonInfo('path')
        dialog = DialogConfirmWithInfo(
            'DialogConfirmBuildSync.xml', addon_path, 'Default', '1080i',
            title=title, info_text=info_text,
            action_label=label1, action_label_2=label2, cancel_label=label_cancel,
        )
        kodi_api.sleep(300)
        dialog.doModal()
        result = getattr(dialog, 'result', -1)
        del dialog
        return result
    except Exception as e:
        log("show_confirm_three: Custom-Dialog fehlgeschlagen, Fallback Select (%s)" % e, 2)
        import traceback
        log(traceback.format_exc(), 3)
        d = kodi_api.Dialog()
        idx = d.select(
            (str(title or '').strip()) or ADDON.getAddonInfo('name'),
            [(str(label1 or '').strip()), (str(label2 or '').strip()), (str(label_cancel or '').strip())]
        )
        return idx if idx >= 0 else -1
