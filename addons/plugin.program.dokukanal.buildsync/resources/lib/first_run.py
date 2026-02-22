# -*- coding: utf-8 -*-
"""
Ersteinrichtungs-Assistent: Geführter Dialog beim ersten Start.
Setzt Einstellungen und first_run_done-Flag. Ob der Wizard schon durchlaufen
wurde, wird ausschließlich über das Addon-Setting first_run_done (Bool) in
resources/settings.xml gehalten; Kodi speichert es persistent (Best Practice).
Nutzt resources.lib.common für ADDON, L, safe_get_bool.
"""
import xbmc
import xbmcgui

from resources.lib.common import ADDON, L, log, safe_get_bool


def _safe_first_run_done(default=False):
    """Liest first_run_done sicher (common.safe_get_bool)."""
    return safe_get_bool('first_run_done', default)


def _step(heading_fmt, step, total, message):
    """Dialog-Titel mit Schritt-Anzeige (z. B. „Schritt 2 von 11“)."""
    return heading_fmt % (step, total), message


def run_wizard():
    """
    Zeigt den Ersteinrichtungs-Assistenten mit Willkommen, Multiselect „Was einrichten?“ und Einzelschritten.
    Setzt am Ende first_run_done auf true.
    """
    d = xbmcgui.Dialog()
    step_fmt = L(30104)  # "Step %d of %d" / "Schritt %d von %d"
    total = 13

    # Schritt 1: Willkommen
    d.ok(L(30102), L(30103))

    # Schritt 2: Multiselect „Was soll eingerichtet werden?“ (ParanoidWizard-Anleihe)
    choices = [L(30129), L(30130), L(30131), L(30132)]  # Sync, addon_data, Verbindung, Backup-Ordner
    preselect = [0, 1, 2]  # Sync, addon_data, Verbindung vorausgewählt
    sel = d.multiselect(L(30128), choices, preselect=preselect)
    if sel is None:
        ADDON.setSettingBool('first_run_done', True)
        return
    want_sync = 0 in sel
    want_addon_data = 1 in sel
    want_connection = 2 in sel
    want_backup_path = 3 in sel
    ADDON.setSettingBool('enable_sync', want_sync)
    ADDON.setSettingBool('addon_sync', want_addon_data)
    if not want_sync:
        ADDON.setSettingBool('first_run_done', True)
        title, msg = _step(step_fmt, 3, 3, L(30114))
        d.ok(title, msg)
        return

    # Schritt 3: Hauptsystem?
    title, msg = _step(step_fmt, 3, total, L(30106))
    is_main = d.yesno(title, msg)
    ADDON.setSettingBool('is_main_system', is_main)

    # Schritte 4–10: Verbindung (nur wenn gewählt) – schreibt in aktive Verbindung (1/2/3)
    if want_connection:
        try:
            active = int(ADDON.getSettingString('active_connection') or '1')
        except (ValueError, TypeError):
            active = 1
        if active not in (1, 2, 3):
            active = 1
        prefix = 'connection_%d_' % active
        conn_labels = [L(30096), L(30097), L(30098)]  # FTP, SFTP, SMB
        title = "%s: %s" % (step_fmt % (4, total), L(30107))
        idx = d.select(title, conn_labels)
        if idx < 0:
            ADDON.setSettingBool('first_run_done', True)
            return
        ADDON.setSettingString(prefix + 'connection_type', str(idx))
        title = "%s: %s" % (step_fmt % (5, total), L(30108))
        host = d.input(title, type=xbmcgui.INPUT_IPADDRESS)
        if host is None:
            ADDON.setSettingBool('first_run_done', True)
            return
        ADDON.setSettingString(prefix + 'ftp_host', host or '')
        title = "%s: %s" % (step_fmt % (6, total), L(30109))
        user = d.input(title)
        if user is None:
            ADDON.setSettingBool('first_run_done', True)
            return
        ADDON.setSettingString(prefix + 'ftp_user', user or '')
        title = "%s: %s" % (step_fmt % (7, total), L(30110))
        password = d.input(title, type=xbmcgui.INPUT_PASSWORD)
        if password is None:
            ADDON.setSettingBool('first_run_done', True)
            return
        ADDON.setSettingString(prefix + 'ftp_pass', password or '')
        title = "%s: %s" % (step_fmt % (8, total), L(30111))
        base = d.input(title, defaultt='kodi')
        if base is None:
            ADDON.setSettingBool('first_run_done', True)
            return
        ADDON.setSettingString(prefix + 'ftp_base_path', base or '')
        title = "%s: %s" % (step_fmt % (9, total), L(30112))
        custom = d.input(title, defaultt='MyDevice')
        if custom is None:
            ADDON.setSettingBool('first_run_done', True)
            return
        ADDON.setSettingString('custom_folder', custom or '')
        title = "%s: %s" % (step_fmt % (10, total), L(30113))
        static = d.input(title, defaultt='')
        if static is not None:
            ADDON.setSettingString('static_folders', static or '')

    # Optional: Backup-Ordner
    if want_backup_path:
        title = "%s: %s" % (step_fmt % (11, total), L(30133))
        path = d.input(title, defaultt='')
        if path is not None and path.strip():
            ADDON.setSettingString('backup_path', path.strip())

    # Optional: Quelle Doku-Kanal im Dateimanager eintragen
    title = "%s: %s" % (step_fmt % (12, total), L(30170))
    if d.yesno(title, L(30171)):
        try:
            from resources.lib import sources_xml
            ok, _ = sources_xml.ensure_doku_kanal_source()
            if not ok:
                log("Doku-Kanal source: add failed", xbmc.LOGWARNING)
        except Exception as e:
            log("Doku-Kanal source: %s" % e, xbmc.LOGWARNING)

    # Fertig + Hinweis Anleitung
    title, msg = _step(step_fmt, 13, total, L(30114))
    d.ok(title, msg)
    ADDON.setSettingBool('first_run_done', True)
    log("First-run wizard completed.", xbmc.LOGINFO)


def maybe_run():
    """Startet den Assistenten nur, wenn first_run_done noch nicht gesetzt ist."""
    if not _safe_first_run_done(default=False):
        run_wizard()


def reset_and_run():
    """Setzt first_run_done zurück und startet den Assistenten (Menüpunkt)."""
    ADDON.setSettingBool('first_run_done', False)
    run_wizard()
