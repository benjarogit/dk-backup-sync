# -*- coding: utf-8 -*-
"""
Zentrales Modul für Aktionen mit Bestätigungs- und Ergebnis-Dialog.

Alle Aktionen mit „Bestätigung → Aktion → Ergebnis“ laufen über dieses Modul
(Verbindung testen, Bildquelle testen, Favoriten sichern, AutoClean, ggf. Install Skin).
addon.py delegiert nur noch; keine direkten xbmcgui.Dialog/xbmc.sleep-Aufrufe für diese Aktionen.

Für Aktionen mit Progress und Ergebnis-Dialog: confirm_then_run verwenden und die Aktion zeigt
intern Progress + dialog.ok (wie backup_restore.run_backup). So liegt die gesamte UI in einer
Funktion; run_with_info_and_confirm bleibt für leichte Aktionen ohne eigenen Progress.

Nutzt resources.lib.common für ADDON, L, log.
"""
import xbmc
import xbmcgui

from resources.lib.common import ADDON, L, log


def run_with_info_and_confirm(
    title,
    message,
    action,
    yeslabel=None,
    nolabel=None,
    success_title=None,
    error_title=None,
    progress_message=None,
):
    """
    Einheitliche Schablone: Erklärungstext (message) + Buttons (Starten/Abbrechen)
    -> DialogProgress während action() -> Ergebnis-Dialog (Erfolg oder Fehler).

    title: Dialogtitel.
    message: Erklärungstext (was passiert); wird im yesno-Dialog angezeigt.
    action: Callable ohne Argumente, Rückgabe (success: bool, message: str).
    yeslabel/nolabel: Button-Texte (Default: 30227 = Starten/Test, 30228 = Abbrechen).
    success_title/error_title: Titel für Ergebnis-Dialog.
    progress_message: Text während der Aktion (z. B. "Bitte warten…").
    """
    dialog = xbmcgui.Dialog()
    title_s = (str(title or '').strip()) or ADDON.getAddonInfo('name')
    message_s = (str(message or '').strip()) or L(30146)
    xbmc.sleep(300)
    if not dialog.yesno(
        title_s,
        message_s,
        yeslabel=yeslabel if yeslabel is not None else L(30227),
        nolabel=nolabel if nolabel is not None else L(30228),
    ):
        return
    err_title = (str(error_title or '').strip()) or ADDON.getAddonInfo('name')
    succ_title = (str(success_title or '').strip()) or title_s
    progress_msg = (str(progress_message or '').strip()) or L(30300)
    progress = xbmcgui.DialogProgress()
    progress.create(title_s, progress_msg)
    try:
        success, result_msg = action()
        try:
            progress.close()
        except Exception:
            pass
        result_msg = str(result_msg or '').strip() or L(30146)
        xbmc.sleep(200)
        dialog_title = succ_title if success else L(30146)
        dialog.ok(dialog_title, result_msg)
    except Exception as e:
        try:
            progress.close()
        except Exception:
            pass
        log(str(e), xbmc.LOGERROR)
        xbmc.sleep(200)
        err_msg = str(e).strip() if e else L(30146)
        dialog.ok(err_title, err_msg if err_msg else L(30146))
    finally:
        try:
            progress.close()
        except Exception:
            pass


def confirm_then_run(title, message, action, yeslabel=None, nolabel=None):
    """
    Zeigt yesno(title, message) mit Buttons. Bei Ja wird action() aufgerufen.
    Kein Progress- oder Ergebnis-Dialog (für Aktionen mit eigener UI, z. B. Backup/Restore).
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


def show_result(title, message, sleep_before=200):
    """
    Zeigt einen einfachen OK-Dialog mit Titel und Nachricht (z.B. AutoClean-Statistik).
    """
    dialog = xbmcgui.Dialog()
    if sleep_before:
        xbmc.sleep(sleep_before)
    message = str(message or '').strip() or L(30146)
    dialog.ok(title, message)


def show_text(title, text):
    """
    Zeigt scrollbaren Text (dialog.textviewer) – für Infos/Anleitungen.
    """
    dialog = xbmcgui.Dialog()
    dialog.textviewer(title, text or '')
