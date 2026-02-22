# -*- coding: utf-8 -*-
"""
Aktionen mit Dialog-Ablauf: über action_dialog.run_with_info_and_confirm bzw. confirm_then_run.
Wird aus addon.py aufgerufen (identischer Ablauf wie Backup/Restore).
"""
import sys
import traceback

import xbmc
import xbmcgui
import xbmcvfs

from resources.lib import action_dialog
from resources.lib.common import ADDON, ADDON_PATH, L, log


def _ensure_auto_ftp_sync():
    """Stellt sicher, dass das Addon-Root im Pfad ist und auto_ftp_sync importierbar ist."""
    addon_path = xbmcvfs.translatePath(ADDON.getAddonInfo('path'))
    if addon_path not in sys.path:
        sys.path.insert(0, addon_path)


def run_test_connection(connection=None):
    """Verbindung testen: Bestätigung (confirm_then_run) → Aktion mit eigenem Progress und dialog.ok (wie Backup/Restore)."""
    xbmc.sleep(100)
    try:
        _ensure_auto_ftp_sync()
        import auto_ftp_sync
        conn_num = int(connection) if connection in ('1', '2', '3') else None
        try:
            summary = auto_ftp_sync.get_connection_summary(conn_num)
        except Exception as e:
            log("get_connection_summary: %s" % str(e), xbmc.LOGWARNING)
            summary = L(30226)
        message = "%s\n\n%s" % (L(30306), summary)

        def _do_test_connection():
            dialog = xbmcgui.Dialog()
            progress = xbmcgui.DialogProgress()
            try:
                progress.create(L(30144), L(30307))
                if conn_num is None:
                    success, msg = auto_ftp_sync.test_current_connection()
                else:
                    success, msg = auto_ftp_sync.test_connection(conn_num)
                progress.close()
                xbmc.sleep(200)
                title = L(30144) if success else ADDON.getAddonInfo('name')
                dialog.ok(title, msg)
            except Exception as e_inner:
                try:
                    progress.close()
                except Exception:
                    pass
                log("_do_test_connection: %s" % str(e_inner), xbmc.LOGERROR)
                xbmc.sleep(200)
                dialog.ok(ADDON.getAddonInfo('name'), str(e_inner) if e_inner else L(30146))

        action_dialog.confirm_then_run(
            L(30144),
            message,
            _do_test_connection,
            yeslabel=L(30227),
            nolabel=L(30228),
        )
    except Exception as e:
        log("run_test_connection: %s\n%s" % (str(e), traceback.format_exc()), xbmc.LOGERROR)
        xbmc.sleep(200)
        try:
            msg = str(e).strip() if e else L(30146)
            xbmcgui.Dialog().ok(L(30146), msg if msg else L(30146))
        except Exception:
            pass


def _format_sync_result(result):
    """Liefert die lokalisierte Meldung aus sync_favourites-Rückgabe oder None (wie plugin._format_sync_result)."""
    if not result or not isinstance(result, (tuple, list)) or len(result) < 2:
        return None
    msg_id = result[1]
    fmt_args = result[2] if len(result) == 3 and isinstance(result[2], dict) else None
    try:
        return L(msg_id).format(**fmt_args) if fmt_args else L(msg_id)
    except (KeyError, TypeError):
        return L(msg_id)


def run_sync_favourites():
    """Favoriten sichern: Bestätigung (confirm_then_run) → Aktion mit eigenem Progress und dialog.ok (wie Backup/Restore)."""
    xbmc.sleep(100)
    try:
        _ensure_auto_ftp_sync()
        import auto_ftp_sync
        dialog = xbmcgui.Dialog()
        progress = xbmcgui.DialogProgress()
        try:
            progress.create(L(30202), L(30300))
            result = auto_ftp_sync.sync_favourites(no_notification=True)
            progress.close()
            # Kurz warten, falls Kodi gerade Fenster schließt/Skin entlädt – danach Notification/Dialog zuverlässiger
            xbmc.sleep(1500)
            msg = _format_sync_result(result)
            if not (msg or '').strip():
                msg = L(30146)
            success = result and isinstance(result, (tuple, list)) and len(result) >= 1 and result[0]
            title = L(30202) if success else ADDON.getAddonInfo('name')
            msg_flat = (msg or '').replace('[CR]', ' ').replace('\n', ' ').replace(',', ' ').strip()[:200]
            # Zuerst Notification (bleibt sichtbar, auch wenn Kodi das Fenster schließt)
            try:
                icon_path = xbmcvfs.translatePath(ADDON.getAddonInfo('path')) + '/resources/images/icon.png'
                xbmc.executebuiltin('Notification(%s,%s,10000,%s)' % (title, msg_flat, icon_path))
            except Exception:
                pass
            dialog.ok(title, msg)
        except Exception as e_inner:
            try:
                progress.close()
            except Exception:
                pass
            log("run_sync_favourites: %s\n%s" % (str(e_inner), traceback.format_exc()), xbmc.LOGERROR)
            xbmc.sleep(200)
            err_msg = str(e_inner) if e_inner else L(30146)
            dialog.ok(ADDON.getAddonInfo('name'), err_msg)
            try:
                icon_path = xbmcvfs.translatePath(ADDON.getAddonInfo('path')) + '/resources/images/icon.png'
                xbmc.executebuiltin('Notification(%s,%s,8000,%s)' % (ADDON.getAddonInfo('name'), (err_msg or '').replace(',', ' ')[:200], icon_path))
            except Exception:
                pass
    except Exception as e:
        log("run_sync_favourites: %s\n%s" % (str(e), traceback.format_exc()), xbmc.LOGERROR)
        xbmc.sleep(200)
        try:
            msg = str(e).strip() if e else L(30146)
            xbmcgui.Dialog().ok(ADDON.getAddonInfo('name'), msg if msg else L(30146))
            try:
                icon_path = xbmcvfs.translatePath(ADDON.getAddonInfo('path')) + '/resources/images/icon.png'
                xbmc.executebuiltin('Notification(%s,%s,8000,%s)' % (ADDON.getAddonInfo('name'), (msg or '')[:200].replace(',', ' '), icon_path))
            except Exception:
                pass
        except Exception:
            pass


def run_test_image_sources():
    """Bildquelle testen: Bestätigung (confirm_then_run) → Aktion mit eigenem Progress und dialog.ok (wie Backup/Restore)."""
    xbmc.sleep(100)
    try:
        _ensure_auto_ftp_sync()
        import auto_ftp_sync

        def _do_test_image_sources():
            dialog = xbmcgui.Dialog()
            progress = xbmcgui.DialogProgress()
            try:
                progress.create(L(30200), L(30300))
                success, msg, tested_source = auto_ftp_sync.test_image_sources()
                progress.close()
                xbmc.sleep(200)
                title = L(30200) if success else ADDON.getAddonInfo('name')
                result_text = "%s\n\n%s" % (msg, L(30316) % tested_source) if tested_source else msg
                dialog.ok(title, result_text)
            except Exception as e_inner:
                try:
                    progress.close()
                except Exception:
                    pass
                log("_do_test_image_sources: %s" % str(e_inner), xbmc.LOGERROR)
                xbmc.sleep(200)
                dialog.ok(ADDON.getAddonInfo('name'), str(e_inner) if e_inner else L(30146))

        action_dialog.confirm_then_run(
            L(30200),
            L(30302),
            _do_test_image_sources,
            yeslabel=L(30227),
            nolabel=L(30228),
        )
    except Exception as e:
        log("run_test_image_sources: %s\n%s" % (str(e), traceback.format_exc()), xbmc.LOGERROR)
        xbmc.sleep(200)
        try:
            msg = str(e).strip() if e else L(30146)
            xbmcgui.Dialog().ok(L(30146), msg if msg else L(30146))
        except Exception:
            pass
