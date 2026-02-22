# -*- coding: utf-8 -*-
"""
Auto-Clean: clear cache, packages, optional thumb cache on a schedule.
Uses addon settings for enable/frequency/sub-options; next run stored in settings.
Nutzt resources.lib.common für ADDON, Pfade, log, safe_get_string, safe_set_string.
"""
import os
import shutil
import time
from datetime import datetime, timedelta

import xbmc
import xbmcvfs

from resources.lib.common import ADDON, ADDON_ID, HOME, USERDATA, TEMP, log, safe_get_string, safe_set_string

CACHE = os.path.join(HOME, 'cache')
PACKAGES = os.path.join(HOME, 'addons', 'packages')
ADDON_DATA = os.path.join(USERDATA, 'addon_data')

EXCLUDE_DIRS = ['archive_cache', 'meta_cache']
LOG_FILES = ['kodi.log', 'kodi.old.log', 'xbmc.log', 'xbmc.old.log']
USERDATA_LOG_FILES = ['kodi.log', 'kodi.old.log']
CACHE_SUBDIR_NAMES = frozenset(['cache', 'Cache', 'log', 'logs', 'temp', 'tmp', 'thumbnails', 'Thumbnails'])
PACKAGES_MIN_AGE_MINUTES = 3


def _get_setting(key, default=None):
    """Liest Setting (common.safe_get_string); bei Fehler default."""
    t = safe_get_string(key, default or '')
    return t if t else default


def _set_setting(key, value):
    """Schreibt Setting (common.safe_set_string)."""
    safe_set_string(key, value)


def clear_cache():
    """Clear special://home/cache and special://temp (excluding archive_cache and log files). Returns (deleted_count, deleted_bytes)."""
    deleted = 0
    total_bytes = 0
    for base_path in (CACHE, TEMP):
        if not os.path.isdir(base_path):
            continue
        try:
            for root, dirs, files in os.walk(base_path, topdown=True):
                dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
                for f in files:
                    if f in LOG_FILES:
                        continue
                    try:
                        path = os.path.join(root, f)
                        try:
                            total_bytes += os.path.getsize(path)
                        except OSError:
                            pass
                        os.unlink(path)
                        deleted += 1
                    except OSError:
                        pass
                for d in dirs:
                    try:
                        path = os.path.join(root, d)
                        if os.path.isdir(path):
                            try:
                                for _root, _dirs, _files in os.walk(path):
                                    for _f in _files:
                                        p = os.path.join(_root, _f)
                                        try:
                                            total_bytes += os.path.getsize(p)
                                        except OSError:
                                            pass
                            except OSError:
                                pass
                            shutil.rmtree(path, ignore_errors=True)
                            deleted += 1
                    except OSError:
                        pass
        except Exception as e:
            log("clear_cache %s: %s" % (base_path, e), xbmc.LOGERROR)
    if deleted > 0:
        log("Cache cleared, %s items removed" % deleted, xbmc.LOGINFO)
    return (deleted, total_bytes)


def clear_packages_startup():
    """Remove files in packages folder older than PACKAGES_MIN_AGE_MINUTES."""
    if not os.path.isdir(PACKAGES):
        return 0
    cutoff = datetime.utcnow() - timedelta(minutes=PACKAGES_MIN_AGE_MINUTES)
    deleted = 0
    try:
        for entry in os.listdir(PACKAGES):
            path = os.path.join(PACKAGES, entry)
            try:
                mtime = datetime.utcfromtimestamp(os.path.getmtime(path))
                if mtime <= cutoff:
                    if os.path.isfile(path):
                        os.unlink(path)
                        deleted += 1
                    elif os.path.isdir(path):
                        shutil.rmtree(path, ignore_errors=True)
                        deleted += 1
            except OSError:
                pass
        if deleted > 0:
            log("Packages cleared, %s items removed" % deleted, xbmc.LOGINFO)
    except Exception as e:
        log("clear_packages: %s" % e, xbmc.LOGERROR)
    return deleted


def clear_userdata_logs():
    """Clear or truncate kodi.log and kodi.old.log in special://userdata (only when setting enabled)."""
    deleted = 0
    for name in USERDATA_LOG_FILES:
        path = os.path.join(USERDATA, name)
        if not os.path.isfile(path):
            continue
        try:
            with open(path, 'w') as f:
                pass
            deleted += 1
        except OSError as e:
            log("clear_userdata_logs %s: %s" % (path, e), xbmc.LOGERROR)
    if deleted > 0:
        log("Userdata logs cleared: %s files" % deleted, xbmc.LOGINFO)
    return deleted


def clear_addon_data_caches(exclude_addon_ids=None):
    """Clear cache/log/temp subdirs under special://userdata/addon_data for each addon (except excluded)."""
    if exclude_addon_ids is None:
        exclude_addon_ids = set()
    else:
        exclude_addon_ids = set(exclude_addon_ids)
    if not os.path.isdir(ADDON_DATA):
        return 0
    total_deleted = 0
    for addon_id in os.listdir(ADDON_DATA):
        if addon_id in exclude_addon_ids:
            continue
        addon_path = os.path.join(ADDON_DATA, addon_id)
        if not os.path.isdir(addon_path):
            continue
        try:
            for root, dirs, files in os.walk(addon_path, topdown=True):
                for d in list(dirs):
                    if d in CACHE_SUBDIR_NAMES:
                        path = os.path.join(root, d)
                        try:
                            if os.path.isdir(path):
                                shutil.rmtree(path, ignore_errors=True)
                                total_deleted += 1
                        except OSError:
                            pass
                        dirs.remove(d)
        except Exception as e:
            log("clear_addon_data_caches %s: %s" % (addon_id, e), xbmc.LOGERROR)
    if total_deleted > 0:
        log("Addon data caches cleared: %s dirs" % total_deleted, xbmc.LOGINFO)
    return total_deleted


def clear_thumbs():
    """Clear Kodi texture cache database (Textures13.db)."""
    db_path = xbmcvfs.translatePath('special://database/Textures13.db')
    if not os.path.exists(db_path):
        return 0
    try:
        import sqlite3
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("DELETE FROM texture")
        cur.execute("DELETE FROM sizes")
        conn.commit()
        cur.execute("VACUUM")
        conn.commit()
        conn.close()
        log("Thumbnail cache cleared", xbmc.LOGINFO)
        return 1
    except Exception as e:
        log("clear_thumbs: %s" % e, xbmc.LOGERROR)
        return 0


def _format_size(bytes_val):
    """Format bytes as MB or KB for display."""
    if bytes_val >= 1024 * 1024:
        return "%.1f MB" % (bytes_val / (1024 * 1024))
    if bytes_val >= 1024:
        return "%.1f KB" % (bytes_val / 1024)
    return "%d B" % bytes_val


def run_auto_clean():
    """Run clean actions according to settings. Returns a short statistics string for display."""
    lines = []
    if _get_setting('autoclean_clearcache', 'true') == 'true':
        cnt, b = clear_cache()
        if cnt > 0:
            lines.append("Cache: %d %s, %s" % (cnt, "Einträge" if cnt != 1 else "Eintrag", _format_size(b)))
    if _get_setting('autoclean_clearpackages', 'true') == 'true':
        n = clear_packages_startup()
        if n > 0:
            lines.append("Packages: %d Dateien" % n)
    if _get_setting('autoclean_clearthumbs', 'false') == 'true':
        n = clear_thumbs()
        if n > 0:
            lines.append("Thumbnails: Datenbank geleert")
    if _get_setting('autoclean_clearlogs', 'false') == 'true':
        n = clear_userdata_logs()
        if n > 0:
            lines.append("Logs: %d Dateien geleert" % n)
    if _get_setting('autoclean_clearaddoncaches', 'false') == 'true':
        n = clear_addon_data_caches(exclude_addon_ids=[ADDON_ID])
        if n > 0:
            lines.append("Addon-Caches: %d Ordner geleert" % n)
    if lines:
        return "\n".join(lines)
    return ADDON.getLocalizedString(30319)


def get_next_run():
    """Return next run timestamp (epoch) from settings, or None."""
    next_run = _get_setting('autoclean_nextrun')
    if not next_run:
        return None
    try:
        return float(next_run)
    except ValueError:
        return None


def set_next_run():
    """Set next run time based on frequency (0=always, 1=daily, 2=3days, 3=weekly, 4=monthly)."""
    freq = int(_get_setting('autoclean_freq', '3') or '3')
    now = time.time()
    if freq == 0:
        next_ts = now + 60  # next run in 1 minute (effectively every startup)
    elif freq == 1:
        next_ts = now + 24 * 3600
    elif freq == 2:
        next_ts = now + 3 * 24 * 3600
    elif freq == 3:
        next_ts = now + 7 * 24 * 3600
    elif freq == 4:
        next_ts = now + 30 * 24 * 3600
    else:
        next_ts = now + 7 * 24 * 3600
    _set_setting('autoclean_nextrun', str(int(next_ts)))


def should_run():
    """True if auto-clean is enabled and due (or no next run set)."""
    if _get_setting('autoclean_enabled', 'false') != 'true':
        return False
    next_run = get_next_run()
    if next_run is None:
        return True
    return time.time() >= next_run


def run_if_due():
    """Called from startup: run auto-clean if enabled and due, then set next run."""
    if not should_run():
        return
    log("Running scheduled auto-clean", xbmc.LOGINFO)
    run_auto_clean()
    set_next_run()
