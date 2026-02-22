# -*- coding: utf-8 -*-
"""Backup/Restore: create_backup, restore_backup. Nur Rueckgabe (bool, str)."""
import os
from typing import Tuple, Optional
from core import settings
from resources.lib import backup_restore


def create_backup(progress_callback=None):
    """
    Erstellt Build-Backup (ZIP). Bei Einstellung „Auf Verbindung speichern“: ZIP in Temp, dann Upload.
    progress_callback(i, total, arcname) -> True = cancel.
    Returns: (success, message).
    """
    include_addon_data = settings.get_bool('backup_include_addon_data', True)
    save_to_connection = settings.get_bool('backup_save_to_connection', False)
    target_base = None
    if save_to_connection:
        import xbmcvfs
        target_base = os.path.join(xbmcvfs.translatePath('special://temp'), 'backup_upload')
        if not os.path.isdir(target_base):
            os.makedirs(target_base, exist_ok=True)
    success, msg, zip_path = backup_restore.create_backup_core(
        include_addon_data=include_addon_data,
        target_base=target_base,
        progress_callback=progress_callback,
    )
    if not success or not save_to_connection or not zip_path:
        return (success, msg)
    conn_num = (settings.get_string('backup_connection') or '1').strip() or '1'
    try:
        conn_int = int(conn_num) if conn_num in ('1', '2', '3') else 1
    except (ValueError, TypeError):
        conn_int = 1
    remote_path = (settings.get_string('backup_remote_path') or 'backups').strip().rstrip('/') or 'backups'
    try:
        import auto_ftp_sync
        backend = auto_ftp_sync.get_backend_for_connection(conn_int)
        if not backend:
            if zip_path and os.path.exists(zip_path):
                try:
                    os.remove(zip_path)
                except OSError:
                    pass
            return (False, backup_restore.ADDON.getLocalizedString(30043) + " (Verbindung %s)" % conn_num)
        backend.ensure_folder(remote_path)
        remote_file = remote_path + '/' + os.path.basename(zip_path)
        if backend.upload(zip_path, remote_file):
            size_str = backup_restore._format_size(os.path.getsize(zip_path)) if zip_path and os.path.exists(zip_path) else ""
            try:
                os.remove(zip_path)
            except OSError:
                pass
            return (True, backup_restore.ADDON.getLocalizedString(30041).format(
                path="Verbindung %s: %s" % (conn_num, remote_file),
                size=size_str))
        return (False, backup_restore.ADDON.getLocalizedString(30068))
    except Exception as e:
        from core import logging_utils
        logging_utils.log("Backup upload: %s" % e, 3)
        return (False, backup_restore.ADDON.getLocalizedString(30068) + "\n%s" % str(e))


def restore_backup(zip_path, wipe_first=False, is_from_url=False, progress_callback=None):
    """
    Stellt aus ZIP wieder her. progress_callback(i, total, name) -> True = cancel.
    Returns: (success, message).
    """
    return backup_restore.restore_from_zip_core(
        zip_path, wipe_first=wipe_first, is_from_url=is_from_url,
        progress_callback=progress_callback,
    )
