# -*- coding: utf-8 -*-
"""
Backup and Restore (ZIP snapshot) for Kodi userdata / full home.
Uses addon settings for paths. Supports restore from local file or URL.
Uses resources.lib.common for ADDON, paths, log.
Validation: manifest (creator + version) and path whitelist (userdata/ and addons/ only).
"""
import json
import os
import zipfile
import urllib.request
from datetime import datetime

import xbmc
import xbmcgui
import xbmcvfs

from resources.lib.common import ADDON, ADDON_ID, ADDON_PATH, HOME, USERDATA, log

ADDONS_DIR = os.path.join(HOME, 'addons')

# Excludes (folder names or path fragments)
EXCLUDE_DIRS = ['cache', 'temp', 'packages', 'archive_cache']
ADDONS_EXCLUDE = ['packages']  # addons subdirs to skip in build backup
EXCLUDE_FILES = ['kodi.log', 'kodi.old.log', 'xbmc.log', 'xbmc.old.log', '.DS_Store']
DATA_PATH = os.path.join(USERDATA, 'addon_data')

# Only files with this prefix count as build backup (create_backup_core writes doku_backup_DDMMYYYY_HHMM.zip)
BACKUP_FILENAME_PREFIX = "doku_backup_"
# Manifest in ZIP: proves origin, prevents loading foreign ZIPs
BACKUP_MANIFEST_FILENAME = "doku_backup_manifest.json"
BACKUP_MANIFEST_VERSION = 1
# Allowed top-level paths in backup (no path traversal, no other folders)
BACKUP_ALLOWED_PREFIXES = ("userdata/", "userdata\\", "addons/", "addons\\")


def _load_backup_config():
    """Load configurable backup list from resources/backup_restore.json. Returns None on error."""
    try:
        json_path = os.path.join(ADDON_PATH, 'resources', 'backup_restore.json')
        if not os.path.exists(json_path):
            return None
        import json
        with open(json_path, 'r', encoding='utf-8', errors='ignore') as f:
            data = json.load(f)
        return data if isinstance(data, list) else None
    except Exception as e:
        log("Load backup config: %s" % e, xbmc.LOGDEBUG)
        return None


def _collect_backup_items_from_config(config, include_addon_data=True):
    """
    Collect (abs_path, arcname) for ZIP. arcname relative to userdata (favourites.xml or addon_data/...).
    setting_id: include only when setting is true (e.g. backup_include_addon_data).
    """
    to_add = []
    for item in config:
        if not isinstance(item, dict):
            continue
        path_type = item.get('path') or 'user_path'
        base = USERDATA if path_type == 'user_path' else DATA_PATH
        setting_id = item.get('setting_id')
        if setting_id:
            try:
                if not ADDON.getSettingBool(setting_id):
                    continue
            except Exception:
                continue
        if item.get('file'):
            f = item.get('file')
            abs_path = os.path.join(base, f)
            if os.path.isfile(abs_path):
                rel = f if path_type == 'user_path' else os.path.join('addon_data', f)
                to_add.append((abs_path, rel))
        elif item.get('folder'):
            folder = item.get('folder')
            folder_path = os.path.join(USERDATA, folder) if path_type == 'data_path' else os.path.join(base, folder)
            if not os.path.isdir(folder_path):
                continue
            for root, dirs, files in os.walk(folder_path):
                dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
                for f in files:
                    if f in EXCLUDE_FILES or f.startswith('._'):
                        continue
                    abs_path = os.path.join(root, f)
                    rel = os.path.relpath(abs_path, USERDATA)
                    to_add.append((abs_path, rel))
    return to_add


def _get_backup_path():
    path = ADDON.getSettingString('backup_path')
    if path:
        return xbmcvfs.translatePath(path)
    return os.path.join(HOME, 'backups')


def get_backup_path_display():
    """Liefert den Backup-Speicherort als Anzeigetext fuer Dialoge (z. B. Vor-Dialog Backup)."""
    if ADDON.getSettingBool('backup_save_to_connection'):
        conn = (ADDON.getSettingString('backup_connection') or '1').strip() or '1'
        remote = (ADDON.getSettingString('backup_remote_path') or 'backups').strip() or 'backups'
        return ADDON.getLocalizedString(30329) + " %s: %s" % (conn, remote)
    path = (ADDON.getSettingString('backup_path') or '').strip()
    if path:
        return xbmcvfs.translatePath(path)
    return xbmcvfs.translatePath(os.path.join(HOME, 'backups'))


def _get_restore_path():
    path = ADDON.getSettingString('restore_path')
    if path:
        return xbmcvfs.translatePath(path)
    return HOME


def _download_zip_from_url(url, target_path, progress_dialog=None):
    """
    Download a ZIP file from url to target_path.
    progress_dialog: optional xbmcgui.DialogProgress to update.
    Returns True on success, False on failure.
    """
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Kodi-Addon'})
        with urllib.request.urlopen(req, timeout=60) as resp:
            total = int(resp.headers.get('Content-Length', 0)) or None
            read_so_far = 0
            chunk_size = 65536
            with open(target_path, 'wb') as f:
                while True:
                    chunk = resp.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    read_so_far += len(chunk)
                    if progress_dialog and total and total > 0:
                        pct = min(100, int(read_so_far / total * 100))
                        progress_dialog.update(pct, ADDON.getLocalizedString(30067))
        return True
    except Exception as e:
        log("Download failed: %s" % e, xbmc.LOGERROR)
        return False


def _collect_addons_for_backup():
    """Collect (abs_path, zip_arcname) for addons/ with zip_arcname = addons/rel."""
    to_add = []
    if not os.path.isdir(ADDONS_DIR):
        return to_add
    for root, dirs, files in os.walk(ADDONS_DIR):
        dirs[:] = [d for d in dirs if d not in ADDONS_EXCLUDE]
        for f in files:
            if f in EXCLUDE_FILES or f.startswith('._') or f.lower().endswith('.pyo'):
                continue
            abs_path = os.path.join(root, f)
            rel = os.path.relpath(abs_path, ADDONS_DIR)
            to_add.append((abs_path, os.path.join('addons', rel)))
    return to_add


def _restart_kodi():
    """
    Restart Kodi in a cross-platform way.
    Linux/Windows (incl. WSL2): RestartApp. Android: RestartApp (some builds support it).
    Darwin (macOS) / iOS: RestartApp not implemented in Kodi, so Quit so user can reopen manually.
    """
    try:
        platform_os = (xbmc.getInfoLabel('System.Platform.OS') or '').strip().lower()
    except Exception:
        platform_os = ''
    if platform_os in ('darwin', 'ios'):
        try:
            xbmc.executebuiltin('Quit')
        except Exception as e:
            log("Quit: %s" % e, xbmc.LOGERROR)
        return
    try:
        xbmc.executebuiltin('RestartApp')
    except Exception as e:
        log("RestartApp: %s" % e, xbmc.LOGERROR)


def _format_size(size):
    for u in ('B', 'KB', 'MB', 'GB'):
        if size < 1024:
            return f"{size:.1f} {u}"
        size /= 1024
    return f"{size:.1f} TB"


def create_backup_core(include_addon_data=True, target_base=None, progress_callback=None):
    """
    Build-Backup ohne Dialoge. progress_callback(i, total, arcname) optional.
    Returns: (True, success_message) or (False, error_message).
    """
    backup_base = target_base or _get_backup_path()
    try:
        if not os.path.isdir(backup_base):
            os.makedirs(backup_base, exist_ok=True)
    except OSError as e:
        log("Cannot create backup dir: %s" % e, xbmc.LOGERROR)
        return False, ADDON.getLocalizedString(30043)

    name = "doku_backup_%s.zip" % datetime.now().strftime('%d%m%Y_%H%M')
    zip_path = os.path.join(backup_base, name)

    config = _load_backup_config()
    if config:
        userdata_items = _collect_backup_items_from_config(config, include_addon_data)
    else:
        source_root = USERDATA
        exclude_dirs = list(EXCLUDE_DIRS)
        if not include_addon_data:
            exclude_dirs.append('addon_data')
        userdata_items = []
        for root, dirs, files in os.walk(source_root):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            rel_root = os.path.relpath(root, source_root)
            if rel_root == '.':
                rel_root = ''
            for f in files:
                if f in EXCLUDE_FILES or f.startswith('._') or f.lower().endswith('.pyo'):
                    continue
                userdata_items.append((os.path.join(root, f), os.path.join(rel_root, f) if rel_root else f))

    to_add = [(p, os.path.join('userdata', a)) for p, a in userdata_items]
    to_add.extend(_collect_addons_for_backup())

    total = len(to_add)
    if total == 0:
        return False, ADDON.getLocalizedString(30044), None

    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED, allowZip64=True) as zf:
            for i, (abs_path, zip_arcname) in enumerate(to_add):
                if progress_callback and callable(progress_callback):
                    if progress_callback(i, total, zip_arcname):
                        if os.path.exists(zip_path):
                            try:
                                os.remove(zip_path)
                            except OSError:
                                pass
                        return False, ADDON.getLocalizedString(30146), None
                try:
                    zf.write(abs_path, zip_arcname)
                except Exception as e:
                    log("Skip %s: %s" % (zip_arcname, e), xbmc.LOGERROR)
            # Manifest: origin + version for restore validation (against foreign/renamed ZIPs)
            manifest = {
                "creator": ADDON_ID,
                "version": BACKUP_MANIFEST_VERSION,
                "timestamp": datetime.now().isoformat(),
            }
            zf.writestr(BACKUP_MANIFEST_FILENAME, json.dumps(manifest, indent=None))
        size = os.path.getsize(zip_path)
        return True, ADDON.getLocalizedString(30041).format(path=zip_path, size=_format_size(size)), zip_path
    except Exception as e:
        log("Backup failed: %s" % e, xbmc.LOGERROR)
        return False, ADDON.getLocalizedString(30042).format(err=str(e)), None


def create_backup(include_addon_data=True, target_base=None):
    """
    Build backup: ZIP with userdata and addons. Shows progress and result dialog.
    If backup_save_to_connection: ZIP to temp, then upload to connection.
    """
    dialog = xbmcgui.Dialog()
    progress = xbmcgui.DialogProgress()
    progress.create(ADDON.getLocalizedString(30001), ADDON.getLocalizedString(30040))

    def progress_cb(i, total, arcname):
        if progress.iscanceled():
            return True
        pct = int((i + 1) / total * 100) if total else 0
        progress.update(pct, "%d / %d\n%s" % (i + 1, total, arcname))
        return False

    success, msg, zip_path = create_backup_core(include_addon_data, target_base, progress_callback=progress_cb)
    try:
        progress.close()
    except Exception:
        pass
    if not success:
        dialog.ok(ADDON.getLocalizedString(30001), msg)
        return False
    # Optional: auf Verbindung hochladen
    if ADDON.getSettingBool('backup_save_to_connection'):
        conn_num = (ADDON.getSettingString('backup_connection') or '1').strip() or '1'
        try:
            conn_int = int(conn_num) if conn_num in ('1', '2', '3') else 1
        except (ValueError, TypeError):
            conn_int = 1
        remote_path = (ADDON.getSettingString('backup_remote_path') or 'backups').strip().rstrip('/') or 'backups'
        try:
            import sys
            addon_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            if addon_path not in sys.path:
                sys.path.insert(0, addon_path)
            import auto_ftp_sync
            backend = auto_ftp_sync.get_backend_for_connection(conn_int)
            if not backend:
                dialog.ok(ADDON.getLocalizedString(30001), ADDON.getLocalizedString(30043) + " (Verbindung %s)" % conn_num)
                if zip_path and os.path.exists(zip_path):
                    try:
                        os.remove(zip_path)
                    except OSError:
                        pass
                return False
            backend.ensure_folder(remote_path)
            remote_file = remote_path + '/' + os.path.basename(zip_path)
            if backend.upload(zip_path, remote_file):
                size_str = _format_size(os.path.getsize(zip_path)) if zip_path and os.path.exists(zip_path) else ""
                try:
                    os.remove(zip_path)
                except OSError:
                    pass
                dialog.ok(ADDON.getLocalizedString(30001), ADDON.getLocalizedString(30041).format(path="Verbindung %s: %s" % (conn_num, remote_file), size=size_str))
            else:
                dialog.ok(ADDON.getLocalizedString(30001), ADDON.getLocalizedString(30068))
                return False
        except Exception as e:
            log("Backup upload to connection: %s" % e, xbmc.LOGERROR)
            dialog.ok(ADDON.getLocalizedString(30001), ADDON.getLocalizedString(30068) + "\n%s" % str(e))
            return False
    else:
        dialog.ok(ADDON.getLocalizedString(30001), msg)
    return True


def restore_from_zip_core(zip_path, wipe_first=False, is_from_url=False, progress_callback=None):
    """
    Restore from ZIP ohne Dialoge. progress_callback(i, total, name) -> True = cancel.
    Returns: (True, success_message) or (False, error_message). Ruft _restart_kodi() bei Erfolg.
    """
    if not zip_path or not zip_path.endswith('.zip'):
        return False, ADDON.getLocalizedString(30042).format(err="No path")
    zip_path = xbmcvfs.translatePath(zip_path) if zip_path.startswith('special://') else zip_path
    if not os.path.exists(zip_path):
        return False, ADDON.getLocalizedString(30042).format(err="File not found")

    if wipe_first:
        cache_path = xbmcvfs.translatePath('special://temp')
        if os.path.exists(cache_path):
            try:
                import shutil
                for entry in os.listdir(cache_path):
                    full = os.path.join(cache_path, entry)
                    if os.path.isfile(full):
                        os.remove(full)
                    elif os.path.isdir(full) and entry != 'archive_cache':
                        shutil.rmtree(full, ignore_errors=True)
            except Exception as e:
                log("Wipe temp: %s" % e, xbmc.LOGERROR)

    extract_root = os.path.normpath(HOME)
    errors = []
    try:
        with zipfile.ZipFile(zip_path, 'r', allowZip64=True) as zf:
            names = [n for n in zf.namelist() if not n.endswith('/')]
            total = len(names)
            for i, name in enumerate(names):
                if progress_callback and callable(progress_callback) and progress_callback(i, total, name):
                    return False, ADDON.getLocalizedString(30146)
                if name == BACKUP_MANIFEST_FILENAME:
                    continue
                norm = name.replace('\\', '/')
                if '..' in norm or not any(norm.startswith(p.replace('\\', '/')) for p in BACKUP_ALLOWED_PREFIXES):
                    log("Restore skip disallowed path: %s" % name, xbmc.LOGDEBUG)
                    continue
                if ADDON_ID in name and 'addon_data' in name:
                    continue
                try:
                    target = os.path.normpath(os.path.join(extract_root, name))
                    if not target.startswith(extract_root):
                        log("Restore path traversal skip: %s" % name, xbmc.LOGDEBUG)
                        continue
                    zf.extract(name, extract_root)
                except Exception as e:
                    errors.append("%s: %s" % (name, e))
                    log("Extract error %s: %s" % (name, e), xbmc.LOGERROR)
        msg = ADDON.getLocalizedString(30141)
        if errors:
            msg += "\n" + ADDON.getLocalizedString(30048).format(count=len(errors))
        _restart_kodi()
        return True, msg
    except zipfile.BadZipFile as e:
        log("Bad zip: %s" % e, xbmc.LOGERROR)
        return False, ADDON.getLocalizedString(30042).format(err=str(e))
    except Exception as e:
        log("Restore failed: %s" % e, xbmc.LOGERROR)
        return False, ADDON.getLocalizedString(30042).format(err=str(e))


def restore_from_zip(zip_path=None, wipe_first=False, is_from_url=False):
    """
    Restore from a ZIP file into userdata (or home).
    zip_path: full path to zip; if None, show browse dialog.
    is_from_url: True if ZIP came from URL (temp file); no "delete backup?" question, temp is removed by caller.
    """
    dialog = xbmcgui.Dialog()
    progress = xbmcgui.DialogProgress()
    if not zip_path:
        zip_path = dialog.browseSingle(1, ADDON.getLocalizedString(30045), 'files', mask='.zip', useThumbs=False)
    if not zip_path or not zip_path.endswith('.zip'):
        return False
    zip_path = xbmcvfs.translatePath(zip_path) if zip_path.startswith('special://') else zip_path
    if not os.path.exists(zip_path):
        dialog.ok(ADDON.getLocalizedString(30001), ADDON.getLocalizedString(30042).format(err="File not found"))
        return False
    if not _is_valid_build_backup(zip_path):
        dialog.ok(ADDON.getLocalizedString(30001), ADDON.getLocalizedString(30325))
        return False

    progress.create(ADDON.getLocalizedString(30001), ADDON.getLocalizedString(30046))

    def progress_cb(i, total, name):
        if progress.iscanceled():
            return True
        pct = int((i + 1) / total * 100) if total else 0
        progress.update(pct, "%d / %d\n%s" % (i + 1, total, name))
        return False

    success, msg = restore_from_zip_core(zip_path, wipe_first, is_from_url, progress_callback=progress_cb)
    try:
        progress.close()
    except Exception:
        pass
    if not is_from_url and success and zip_path and os.path.exists(zip_path):
        if dialog.yesno(ADDON.getLocalizedString(30001), ADDON.getLocalizedString(30140), nolabel=ADDON.getLocalizedString(30142), yeslabel=ADDON.getLocalizedString(30143)):
            try:
                os.remove(zip_path)
            except OSError as e:
                log("Could not delete backup file: %s" % e, xbmc.LOGERROR)
    dialog.ok(ADDON.getLocalizedString(30001), msg)
    return success


def run_backup():
    """Entry: create backup; include addon_data from setting."""
    include_addon_data = ADDON.getSettingBool('backup_include_addon_data')
    create_backup(include_addon_data=include_addon_data)


def _is_valid_build_backup(zip_path):
    """
    Prüft, ob die ZIP ein gültiges Build-Backup ist:
    - Bevorzugt: doku_backup_manifest.json mit creator=ADDON_ID und version=BACKUP_MANIFEST_VERSION.
    - Legacy (ohne Manifest): mindestens ein Eintrag userdata/, alle Einträge unter userdata/ oder addons/, kein '..'.
    - Jeder Eintrag muss unter userdata/ oder addons/ liegen, kein Path-Traversal.
    Verhindert: umbenannte Fremd-ZIPs, schädliche Pfade, Einschleusen von Code.
    """
    if not zip_path or not str(zip_path).lower().endswith('.zip') or not os.path.exists(zip_path):
        return False
    try:
        with zipfile.ZipFile(zip_path, 'r', allowZip64=True) as zf:
            names = zf.namelist()
            has_manifest = BACKUP_MANIFEST_FILENAME in names
            if has_manifest:
                try:
                    raw = zf.read(BACKUP_MANIFEST_FILENAME).decode('utf-8')
                    manifest = json.loads(raw)
                except (ValueError, KeyError, TypeError, UnicodeDecodeError) as e:
                    log("Backup manifest invalid %s: %s" % (zip_path, e), xbmc.LOGDEBUG)
                    return False
                if manifest.get('creator') != ADDON_ID or manifest.get('version') != BACKUP_MANIFEST_VERSION:
                    log("Backup manifest wrong creator/version: %s" % zip_path, xbmc.LOGDEBUG)
                    return False
            else:
                # Legacy: mindestens ein userdata-Eintrag
                if not any(n.startswith('userdata/') or n.startswith('userdata\\') for n in names):
                    log("Backup ZIP missing manifest and userdata: %s" % zip_path, xbmc.LOGDEBUG)
                    return False
            for n in names:
                if n == BACKUP_MANIFEST_FILENAME or n.endswith('/'):
                    continue
                norm = n.replace('\\', '/')
                if '..' in norm:
                    log("Backup ZIP path traversal rejected: %s" % n, xbmc.LOGDEBUG)
                    return False
                if not any(norm.startswith(p.replace('\\', '/')) for p in BACKUP_ALLOWED_PREFIXES):
                    log("Backup ZIP disallowed path: %s" % n, xbmc.LOGDEBUG)
                    return False
        return True
    except (zipfile.BadZipFile, OSError, Exception) as e:
        log("Invalid or unreadable backup ZIP %s: %s" % (zip_path, e), xbmc.LOGDEBUG)
        return False


def _get_local_backup_zips():
    """
    Nur gültige Build-Backups im konfigurierten Backup-Ordner: Dateiname doku_backup_*.zip und
    Inhalt enthält userdata/. Neueste zuerst. Andere ZIPs werden ignoriert.
    """
    backup_dir = _get_backup_path()
    if not backup_dir or not os.path.isdir(backup_dir):
        return []
    try:
        files = [f for f in os.listdir(backup_dir)
                 if f.startswith(BACKUP_FILENAME_PREFIX) and f.lower().endswith('.zip')]
        paths = [os.path.join(backup_dir, f) for f in files]
        valid = [p for p in paths if _is_valid_build_backup(p)]
        valid.sort(key=lambda p: os.path.getmtime(p), reverse=True)
        return valid
    except OSError as e:
        log("List backup dir %s: %s" % (backup_dir, e), xbmc.LOGDEBUG)
        return []


def run_restore():
    """Entry: Local / URL / From connection. Back = cancel. Local: backup path or browse. URL: restore_url or ask. Connection: list remote, download, restore."""
    dialog = xbmcgui.Dialog()
    title = ADDON.getLocalizedString(30038) + " – " + ADDON.getLocalizedString(30320)
    choices = [
        ADDON.getLocalizedString(30064),  # Choose local file
        ADDON.getLocalizedString(30065),  # Choose external file (URL)
        ADDON.getLocalizedString(30329),  # Von Verbindung (FTP/SFTP/SMB)
    ]
    idx = dialog.select(title, choices)
    if idx < 0:
        return  # Back = Abbrechen
    wipe = ADDON.getSettingBool('restore_wipe')
    if dialog.yesno(ADDON.getLocalizedString(30001), ADDON.getLocalizedString(30050)):
        wipe = True
        try:
            ADDON.setSettingBool('restore_wipe', True)
        except Exception:
            pass
    else:
        try:
            ADDON.setSettingBool('restore_wipe', False)
        except Exception:
            pass

    if idx == 0:
        # Local: check backup folder from settings first
        zip_list = _get_local_backup_zips()
        if zip_list:
            choice_labels = [os.path.basename(p) for p in zip_list]
            choice_labels.append(ADDON.getLocalizedString(30324))  # Choose other file...
            sel = dialog.select(ADDON.getLocalizedString(30064), choice_labels)
            if sel < 0:
                return
            if sel == len(zip_list):
                restore_from_zip(zip_path=None, wipe_first=wipe, is_from_url=False)
            else:
                restore_from_zip(zip_path=zip_list[sel], wipe_first=wipe, is_from_url=False)
        else:
            restore_from_zip(zip_path=None, wipe_first=wipe, is_from_url=False)
        return

    if idx == 2:
        # From connection: list backups on server, select, download, restore
        conn_num = (ADDON.getSettingString('backup_connection') or '1').strip() or '1'
        try:
            conn_int = int(conn_num) if conn_num in ('1', '2', '3') else 1
        except (ValueError, TypeError):
            conn_int = 1
        remote_path = (ADDON.getSettingString('backup_remote_path') or 'backups').strip().rstrip('/') or 'backups'
        try:
            import sys
            addon_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            if addon_path not in sys.path:
                sys.path.insert(0, addon_path)
            import auto_ftp_sync
            backend = auto_ftp_sync.get_backend_for_connection(conn_int)
            if not backend:
                dialog.ok(ADDON.getLocalizedString(30001), ADDON.getLocalizedString(30043) + " (Verbindung %s)" % conn_num)
                return
            names = backend.listdir(remote_path) or []
            zips = [n for n in names if n.startswith(BACKUP_FILENAME_PREFIX) and n.lower().endswith('.zip')]
            if not zips:
                dialog.ok(ADDON.getLocalizedString(30001), ADDON.getLocalizedString(30044) + "\n(%s: %s)" % (ADDON.getLocalizedString(30329), remote_path))
                return
            zips.sort(reverse=True)  # newest first (filename contains date)
            sel = dialog.select(ADDON.getLocalizedString(30329), zips)
            if sel < 0:
                return
            remote_file = remote_path + '/' + zips[sel]
            temp_dir = xbmcvfs.translatePath('special://temp')
            temp_zip = os.path.join(temp_dir, 'restore_connection.zip')
            progress = xbmcgui.DialogProgress()
            progress.create(ADDON.getLocalizedString(30001), ADDON.getLocalizedString(30067))
            if not backend.download(remote_file, temp_zip):
                progress.close()
                dialog.ok(ADDON.getLocalizedString(30001), ADDON.getLocalizedString(30068))
                return
            progress.close()
            if not _is_valid_build_backup(temp_zip):
                dialog.ok(ADDON.getLocalizedString(30001), ADDON.getLocalizedString(30325))
                return
            try:
                restore_from_zip(zip_path=temp_zip, wipe_first=wipe, is_from_url=True)
            finally:
                if os.path.exists(temp_zip):
                    try:
                        os.remove(temp_zip)
                    except OSError:
                        pass
        except Exception as e:
            log("Restore from connection: %s" % e, xbmc.LOGERROR)
            dialog.ok(ADDON.getLocalizedString(30001), ADDON.getLocalizedString(30068) + "\n%s" % str(e))
        return

    # idx == 1: URL
    url = (ADDON.getSettingString('restore_url') or '').strip()
    if not url or not url.startswith(('http://', 'https://')):
        url = dialog.input(ADDON.getLocalizedString(30066), type=xbmcgui.INPUT_ALPHANUM)
        if not url or not url.strip():
            return
        url = url.strip()
        if not url.startswith(('http://', 'https://')):
            dialog.ok(ADDON.getLocalizedString(30001), ADDON.getLocalizedString(30068))
            return
        try:
            ADDON.setSettingString('restore_url', url)
        except Exception:
            pass

    temp_dir = xbmcvfs.translatePath('special://temp')
    temp_zip = os.path.join(temp_dir, 'restore_download.zip')
    progress = xbmcgui.DialogProgress()
    progress.create(ADDON.getLocalizedString(30001), ADDON.getLocalizedString(30067))
    if not _download_zip_from_url(url, temp_zip, progress_dialog=progress):
        progress.close()
        dialog.ok(ADDON.getLocalizedString(30001), ADDON.getLocalizedString(30068))
        return
    progress.close()

    if not os.path.exists(temp_zip) or not temp_zip.endswith('.zip'):
        dialog.ok(ADDON.getLocalizedString(30001), ADDON.getLocalizedString(30068))
        return
    if not _is_valid_build_backup(temp_zip):
        dialog.ok(ADDON.getLocalizedString(30001), ADDON.getLocalizedString(30325))
        return
    try:
        restore_from_zip(zip_path=temp_zip, wipe_first=wipe, is_from_url=True)
    finally:
        if os.path.exists(temp_zip):
            try:
                os.remove(temp_zip)
            except OSError:
                pass
