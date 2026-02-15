# -*- coding: utf-8 -*-
"""
Ersteinrichtungs-Assistent: Geführter Dialog beim ersten Start.
Setzt Einstellungen und first_run_done-Flag. Ob der Wizard schon durchlaufen
wurde, wird ausschließlich über das Addon-Setting first_run_done (Bool) in
resources/settings.xml gehalten; Kodi speichert es persistent (Best Practice).
"""
import xbmc
import xbmcaddon
import xbmcgui

ADDON = xbmcaddon.Addon()


def _l(msg_id):
    return ADDON.getLocalizedString(msg_id)


def _step(heading_fmt, step, total, message):
    """Dialog-Titel mit Schritt-Anzeige (z. B. „Schritt 2 von 11“)."""
    return heading_fmt % (step, total), message


def run_wizard():
    """
    Zeigt den Ersteinrichtungs-Assistenten mit Willkommen und Einzelschritten.
    Setzt am Ende first_run_done auf true.
    """
    d = xbmcgui.Dialog()
    step_fmt = _l(30104)  # "Step %d of %d" / "Schritt %d von %d"
    total = 11

    # Schritt 1: Willkommen
    d.ok(_l(30102), _l(30103))

    # Schritt 2: Sync aktivieren?
    title, msg = _step(step_fmt, 2, total, _l(30105))
    enable_sync = d.yesno(title, msg)
    ADDON.setSettingBool('enable_sync', enable_sync)
    if not enable_sync:
        ADDON.setSettingBool('first_run_done', True)
        title, msg = _step(step_fmt, 3, 3, _l(30114))
        d.ok(title, msg)
        return

    # Schritt 3: Hauptsystem?
    title, msg = _step(step_fmt, 3, total, _l(30106))
    is_main = d.yesno(title, msg)
    ADDON.setSettingBool('is_main_system', is_main)

    # Schritt 4: Verbindungstyp
    conn_labels = [_l(30096), _l(30097), _l(30098)]  # FTP, SFTP, SMB
    title = "%s: %s" % (step_fmt % (4, total), _l(30107))
    idx = d.select(title, conn_labels)
    if idx < 0:
        return
    ADDON.setSettingString('connection_type', str(idx))

    # Schritt 5: Host
    title = "%s: %s" % (step_fmt % (5, total), _l(30108))
    host = d.input(title, type=xbmcgui.INPUT_IPADDRESS)
    if host is None:
        return
    ADDON.setSettingString('ftp_host', host or '')

    # Schritt 6: User
    title = "%s: %s" % (step_fmt % (6, total), _l(30109))
    user = d.input(title)
    if user is None:
        return
    ADDON.setSettingString('ftp_user', user or '')

    # Schritt 7: Passwort
    title = "%s: %s" % (step_fmt % (7, total), _l(30110))
    password = d.input(title, type=xbmcgui.INPUT_PASSWORD)
    if password is None:
        return
    ADDON.setSettingString('ftp_pass', password or '')

    # Schritt 8: Basispfad
    title = "%s: %s" % (step_fmt % (8, total), _l(30111))
    base = d.input(title, default='kodi')
    if base is None:
        return
    ADDON.setSettingString('ftp_base_path', base or '')

    # Schritt 9: Benutzerdefinierter Ordnername
    title = "%s: %s" % (step_fmt % (9, total), _l(30112))
    custom = d.input(title, default='MyDevice')
    if custom is None:
        return
    ADDON.setSettingString('custom_folder', custom or '')

    # Schritt 10: Optional Statische Ordner
    title = "%s: %s" % (step_fmt % (10, total), _l(30113))
    static = d.input(title, default='')
    if static is not None:
        ADDON.setSettingString('static_folders', static or '')

    # Schritt 11: Fertig + Hinweis Anleitung
    title, msg = _step(step_fmt, 11, total, _l(30114))
    d.ok(title, msg)
    ADDON.setSettingBool('first_run_done', True)
    xbmc.log("First-run wizard completed.", xbmc.LOGINFO)


def maybe_run():
    """Startet den Assistenten nur, wenn first_run_done noch nicht gesetzt ist."""
    try:
        if not ADDON.getSettingBool('first_run_done'):
            run_wizard()
    except Exception as e:
        xbmc.log(f"First-run wizard: {e}", xbmc.LOGERROR)


def reset_and_run():
    """Setzt first_run_done zurück und startet den Assistenten (Menüpunkt)."""
    ADDON.setSettingBool('first_run_done', False)
    run_wizard()
