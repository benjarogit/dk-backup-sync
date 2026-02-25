# -*- coding: utf-8 -*-
"""
Auto FTP Sync - Kodi service addon.
Syncs favourites and addon_data via FTP, optional image rotation and startup file copies.
Uses resources.lib.common for ADDON, settings, localization, log.

Architecture: each feature is a self-contained function (sync_favourites, sync_addon_data,
download_random_image, test_connection, test_image_sources, ensure_remote_structure, …).
Shared helpers: _load_settings, show_notification, _get_backend, _get_profile_settings, …
Service block (if __name__ == "__main__") runs only on Kodi start; external calls run one function only.
"""
import os
import random
import shutil
import urllib.request
import re
import xbmc
import xbmcvfs
import time
import zipfile

from resources.lib.common import ADDON, ADDON_ID, ADDON_PATH, USERDATA, L, log, safe_get_string, safe_get_bool


def _load_settings():
    """Load all service settings with safe getters; repair invalid values by rewriting defaults."""
    global ENABLED, IS_MAIN_SYSTEM, OVERWRITE_STATIC, CUSTOM_FOLDER, SPECIFIC_CUSTOM_FOLDER
    global STATIC_FOLDERS, IMAGE_SOURCE_IDX, IMAGE_LIST_URL, IMAGE_LOCAL_FOLDER, IMAGE_NETWORK_PATH
    global ENABLE_IMAGE_ROTATION, ENABLE_ADDON_SYNC, IMAGE_DISPLAY_MODE, FAVOURITES_SYNC_INTERVAL_MINUTES, FAVOURITES_SYNC_MODE
    ENABLED = safe_get_bool('enable_sync', False)
    IS_MAIN_SYSTEM = safe_get_bool('is_main_system', True)
    OVERWRITE_STATIC = safe_get_bool('overwrite_static', False)
    CUSTOM_FOLDER = safe_get_string('custom_folder', '')
    SPECIFIC_CUSTOM_FOLDER = safe_get_string('specific_custom_folder', '')
    static_raw = safe_get_string('static_folders', '')
    STATIC_FOLDERS = [f.strip() for f in static_raw.split(',') if f.strip()]
    try:
        IMAGE_SOURCE_IDX = int(safe_get_string('image_source', '0') or '0')
    except (ValueError, TypeError):
        IMAGE_SOURCE_IDX = 0
    IMAGE_LIST_URL = safe_get_string('image_list_url', '')
    IMAGE_LOCAL_FOLDER = xbmcvfs.translatePath(safe_get_string('image_local_folder', '') or '')
    IMAGE_NETWORK_PATH = (safe_get_string('image_network_path', '') or '').strip()
    ENABLE_IMAGE_ROTATION = safe_get_bool('enable_image_rotation', False)
    ENABLE_ADDON_SYNC = safe_get_bool('addon_sync', True)
    try:
        IMAGE_DISPLAY_MODE = int(safe_get_string('image_display_mode', '0') or '0')
    except (ValueError, TypeError):
        IMAGE_DISPLAY_MODE = 0
    try:
        FAVOURITES_SYNC_INTERVAL_MINUTES = int(safe_get_string('favourites_sync_interval_minutes', '20') or '20')
    except (ValueError, TypeError):
        FAVOURITES_SYNC_INTERVAL_MINUTES = 20
    raw_mode = (safe_get_string('favourites_sync_mode', 'merge') or 'merge').strip().lower()
    FAVOURITES_SYNC_MODE = raw_mode if raw_mode in ('merge', 'overwrite') else 'merge'


# Defaults (overwritten in _load_settings())
ENABLED = False
IS_MAIN_SYSTEM = True
OVERWRITE_STATIC = False
CUSTOM_FOLDER = ''
SPECIFIC_CUSTOM_FOLDER = ''
STATIC_FOLDERS = []
IMAGE_SOURCE_IDX = 0
IMAGE_LIST_URL = ''
IMAGE_LOCAL_FOLDER = ''
IMAGE_NETWORK_PATH = ''
ENABLE_IMAGE_ROTATION = False
ENABLE_ADDON_SYNC = True
IMAGE_DISPLAY_MODE = 0  # 0 = download, 1 = show directly from URL
FAVOURITES_SYNC_INTERVAL_MINUTES = 20  # 0 = only at start
FAVOURITES_SYNC_MODE = 'merge'  # 'merge' | 'overwrite'

# Image rotation: suppress notification for first 90s after start (no toast on start/settings actions)
_IMAGE_NOTIFICATION_QUIET_UNTIL = 0.0

# Pfade (ADDON_ID, ADDON_PATH, USERDATA aus common)
LOCAL_FAVOURITES = os.path.join(USERDATA, 'favourites.xml')
STATIC_FAVOURITES_PATH = os.path.join(USERDATA, 'addon_data', ADDON_ID, 'Static Favourites')
ICON_PATH = os.path.join(ADDON_PATH, 'resources', 'images', 'icon.png')
LOCAL_IMAGE_PATH = os.path.join(USERDATA, 'doku_background.jpg')
BACKGROUND_URL_FILE = os.path.join(USERDATA, 'doku_background_url.txt')
IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp')


def _get_profile_settings(connection_number):
    """
    Read connection settings for connection 1, 2 or 3.
    connection_number: 1, 2 or 3.
    Returns: dict with connection_type, host, user, password, base_path, sftp_port
    """
    if connection_number not in (1, 2, 3):
        connection_number = 1
    prefix = 'connection_%d_' % connection_number
    try:
        ct = int(safe_get_string(prefix + 'connection_type', '0') or '0')
    except (ValueError, TypeError):
        ct = 0
    ct = ('ftp', 'sftp', 'smb')[ct] if 0 <= ct <= 2 else 'ftp'
    return {
        'connection_type': ct,
        'host': safe_get_string(prefix + 'ftp_host', ''),
        'user': safe_get_string(prefix + 'ftp_user', ''),
        'password': safe_get_string(prefix + 'ftp_pass', ''),
        'base_path': safe_get_string(prefix + 'ftp_base_path', ''),
        'sftp_port': safe_get_string(prefix + 'sftp_port', '22'),
    }


def _get_active_profile_settings():
    """
    Read settings of the active connection (1, 2 or 3).
    If active is "None" (0): returns profile with empty host (no remote actions).
    Returns: dict with connection_type, host, user, password, base_path, sftp_port
    """
    try:
        active = int(safe_get_string('active_connection', '1') or '1')
    except (ValueError, TypeError):
        active = 1
    if active not in (1, 2, 3):
        # "None" (0) or invalid: empty profile so _has_connection_configured() is False
        p = _get_profile_settings(1)
        p['host'] = ''
        return p
    return _get_profile_settings(active)


def get_connection_summary(connection_number=None):
    """
    Liefert eine lesbare Auflistung der Verbindungseinstellungen (ohne Passwort)
    für die Anzeige im Dialog vor dem Verbindungstest.

    Args:
        connection_number: 1, 2 oder 3 für konkrete Verbindung; None für aktive Verbindung.

    Returns:
        Mehrzeiliger String (z. B. "Verbindung 1", "Typ: SFTP", "Host: …").
        Bei keinem Host: Hinweis "Nicht konfiguriert". Wenn connection_number None
        und keine Verbindung konfiguriert: nur L(30226), ohne "Aktive Verbindung (Verbindung 1)".
    """
    if connection_number in (1, 2, 3):
        p = _get_profile_settings(connection_number)
        label = "Verbindung %d" % connection_number
    else:
        if not _has_connection_configured():
            return L(30226)
        p = _get_active_profile_settings()
        try:
            active = int(safe_get_string('active_connection', '1') or '1')
        except (ValueError, TypeError):
            active = 1
        label = "Aktive Verbindung (Verbindung %d)" % active
    host = (p.get('host') or '').strip()
    if not host:
        return "%s\n\n%s" % (label, L(30226))
    ct = (p.get('connection_type') or 'ftp').upper()
    lines = [
        label,
        "",
        "Typ: %s" % ct,
        "Host: %s" % host,
        "Benutzer: %s" % ((p.get('user') or '').strip() or "-"),
        "Basispfad: %s" % ((p.get('base_path') or '').strip() or "."),
    ]
    if (p.get('connection_type') or '') == 'sftp':
        port = (p.get('sftp_port') or '').strip() or '22'
        lines.append("SFTP-Port: %s" % port)
    return "\n".join(lines)


def _has_connection_configured():
    """True, wenn in der aktiven Verbindung ein Host eingetragen ist (Remote-Aktionen sinnvoll)."""
    p = _get_active_profile_settings()
    return bool((p.get('host') or '').strip())


def _get_backend():
    """Return sync backend (FTP/SFTP/SMB) from connection settings."""
    from resources.lib import sync_backend
    p = _get_active_profile_settings()
    return sync_backend.get_backend(
        p['connection_type'], p['host'], p['user'], p['password'],
        p['base_path'] or '', p['sftp_port']
    )


def get_backend_for_connection(connection_number):
    """
    Return sync backend for connection 1, 2 or 3. For backup/restore via FTP/SFTP/SMB.
    connection_number: 1, 2 or 3. Returns None if not configured or invalid.
    """
    if connection_number not in (1, 2, 3):
        return None
    try:
        p = _get_profile_settings(connection_number)
        if not (p.get('host') or '').strip():
            return None
        from resources.lib import sync_backend
        return sync_backend.get_backend(
            p['connection_type'], p['host'], p['user'], p['password'],
            p['base_path'] or '', p.get('sftp_port') or '22'
        )
    except Exception as e:
        log("get_backend_for_connection(%s): %s" % (connection_number, e), xbmc.LOGDEBUG)
        return None


def test_current_connection():
    """
    Testet die aktuelle Verbindung (aus aktivem Profil).
    Returns: (success: bool, message: str)
    """
    try:
        p = _get_active_profile_settings()
        if not (p.get('host') or '').strip():
            return False, L(30317)
        from resources.lib import sync_backend
        backend = sync_backend.get_backend(
            p['connection_type'], p['host'], p['user'], p['password'],
            p['base_path'] or '', p['sftp_port']
        )
        base_path = (p.get('base_path') or '').strip().strip('/') or '.'
        backend.folder_exists(base_path)
        return True, L(30308)
    except Exception as e:
        log("test_connection: %s" % str(e), xbmc.LOGERROR)
        return False, L(30309) + " " + str(e)


def test_connection(connection_number):
    """
    Testet eine bestimmte Verbindung (1, 2 oder 3).
    Returns: (success: bool, message: str)
    """
    if connection_number not in (1, 2, 3):
        return False, L(30318)
    try:
        p = _get_profile_settings(connection_number)
        if not (p.get('host') or '').strip():
            return False, L(30317)
        from resources.lib import sync_backend
        backend = sync_backend.get_backend(
            p['connection_type'], p['host'], p['user'], p['password'],
            p['base_path'] or '', p['sftp_port']
        )
        base_path = (p.get('base_path') or '').strip().strip('/') or '.'
        backend.folder_exists(base_path)
        return True, L(30308)
    except Exception as e:
        log("test_connection(%d): %s" % (connection_number, str(e)), xbmc.LOGERROR)
        return False, L(30309) + " " + str(e)


def _get_image_source_label(source_index=None):
    """
    Liefert fuer die Bildquelle (0/1/2/3) einen kurzen Namen und optional Detail (URL/Pfad).
    source_index: 0/1/2/3 oder None = aktuelle Einstellung (IMAGE_SOURCE_IDX).
    Returns: (name: str, detail: str|None) z.B. ('Picsum.photos', None), ('Bildlisten-URL', 'https://...')
    """
    if source_index is None:
        _load_settings()
        src = IMAGE_SOURCE_IDX
    else:
        src = source_index
    if src == 0:
        url = (safe_get_string('image_list_url', '') or '').strip()
        return ('Bildlisten-URL', url if url else None)
    if src == 1:
        folder = (safe_get_string('image_local_folder', '') or '').strip()
        return ('Lokaler Ordner', folder if folder else None)
    if src == 2:
        path = (safe_get_string('image_network_path', '') or '').strip()
        return ('Netzwerkpfad (SMB)', path if path else None)
    if src == 3:
        return ('Picsum.photos', None)
    return ('Unbekannte Bildquelle', None)


def get_image_source_summary(connection_number=None):
    """
    Liefert einen kurzen lesbaren Text zur aktiven Bildquelle (fuer Vor-Dialog beim Test).
    connection_number wird ignoriert (nur eine Bildquelle pro Addon); Parameter fuer API-Konsistenz.
    Returns: z.B. "Aktiv: Picsum.photos" oder "Aktiv: Bildlisten-URL: https://..."
    """
    name, detail = _get_image_source_label(None)
    if detail:
        return "Aktiv: %s: %s" % (name, detail)
    return "Aktiv: %s" % name


def test_image_sources():
    """
    Testet die konfigurierte Bildquelle abhaengig von image_source:
    0 = URL-Liste (image_list_url), 1 = lokaler Ordner, 2 = SMB/Netzwerkpfad, 3 = Picsum.photos.
    Returns: (success: bool, message: str, tested_source: str) – tested_source fuer Nach-Dialog „Getestet: …“
    """
    try:
        src = int(safe_get_string('image_source', '0') or '0')
    except (ValueError, TypeError):
        src = 0
    name, detail = _get_image_source_label(src)
    tested_label = "%s: %s" % (name, detail) if detail else name

    # 0 = URL-Liste (Bildlisten-URL)
    if src == 0:
        url = (safe_get_string('image_list_url', '') or '').strip()
        if not url:
            return False, '%s: Keine Bildlisten-URL eingetragen.' % L(30146), tested_label
        try:
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'Kodi-Addon')
            with urllib.request.urlopen(req, timeout=15) as response:
                content = response.read(65536).decode('utf-8', errors='ignore')
            if not content.strip():
                return False, '%s: URL lieferte leere Antwort.' % L(30146), tested_label
            return True, L(30199), tested_label
        except urllib.error.URLError as e:
            log("test_image_sources URL error: %s" % str(e), xbmc.LOGERROR)
            return False, '%s: %s' % (L(30146), str(e.reason) if getattr(e, 'reason', None) else str(e)), tested_label
        except Exception as e:
            log("test_image_sources: %s" % str(e), xbmc.LOGERROR)
            return False, '%s: %s' % (L(30146), str(e)), tested_label

    # 1 = Lokaler Ordner
    if src == 1:
        folder = (safe_get_string('image_local_folder', '') or '').strip()
        if not folder:
            return False, '%s: Kein lokaler Bildordner eingetragen.' % L(30146), tested_label
        path = xbmcvfs.translatePath(folder) if folder.startswith('special://') else folder
        if not os.path.isdir(path):
            return False, '%s: Ordner nicht gefunden oder nicht lesbar.' % L(30146), tested_label
        return True, L(30199), tested_label

    # 2 = Netzwerkpfad (SMB)
    if src == 2:
        path = (safe_get_string('image_network_path', '') or '').strip().rstrip('/') + '/'
        if not path or path == '/':
            return False, '%s: Kein Netzwerkpfad eingetragen.' % L(30146), tested_label
        try:
            dirs, files = xbmcvfs.listdir(path)
            return True, L(30199), tested_label
        except Exception as e:
            log("test_image_sources SMB: %s" % str(e), xbmc.LOGERROR)
            return False, '%s: %s' % (L(30146), str(e)), tested_label

    # 3 = Picsum.photos
    if src == 3:
        try:
            req = urllib.request.Request('https://picsum.photos/1920/1080', headers={'User-Agent': 'Kodi-Addon/1.0'})
            with urllib.request.urlopen(req, timeout=15) as response:
                response.read(8192)
            return True, L(30199), tested_label
        except urllib.error.URLError as e:
            log("test_image_sources Picsum: %s" % str(e), xbmc.LOGERROR)
            return False, '%s: Picsum nicht erreichbar. %s' % (L(30146), str(e.reason) if getattr(e, 'reason', None) else str(e)), tested_label
        except Exception as e:
            log("test_image_sources: %s" % str(e), xbmc.LOGERROR)
            return False, '%s: %s' % (L(30146), str(e)), tested_label

    return False, '%s: Unbekannte Bildquelle.' % L(30146), tested_label


def _remote_path(*path_parts):
    """Baut Remote-Pfad für Sync (Basis aus aktivem Profil). Ordnerteile werden kleingeschrieben (case-insensitiv)."""
    base = (_get_active_profile_settings()['base_path'] or '').strip().strip('/')
    segs = [base, 'auto_fav_sync'] if base else ['auto_fav_sync']
    for p in path_parts:
        if not p:
            continue
        s = str(p).strip('/')
        # Ordner kleinschreiben, Dateinamen unverändert (z. B. favourites.xml, addon_data.zip)
        segs.append(s.lower() if '.' not in s else s)
    return '/' + '/'.join(segs)


def show_notification(message_id, duration=5000, **kwargs):
    """
    Zeigt eine Kodi-Notification an.

    Args:
        message_id (int): Die Message-ID für den Lokalisierungstext.
        duration (int): Anzeigedauer in Millisekunden. Standard 5000.
        **kwargs: Optionale Platzhalter für format() im lok. String.

    Returns:
        None
    """
    message = L(message_id).format(**kwargs)
    xbmc.executebuiltin(f'Notification({L(30001)}, {message}, {duration}, {ICON_PATH})')
    time.sleep(duration / 1000)  # Warte, bis die Benachrichtigung abgeschlossen ist


def sync_standard_favourites():
    """
    Synchronisiert die Haupt-Favoriten (favourites.xml) mit Union-Merge:
    Alle Geräte gleich; Ergebnis = Vereinigung von lokal und Server (dedupliziert).
    Vor dem Überschreiben wird die aktuelle favourites.xml nach favourites.xml.bak kopiert.

    Returns:
        bool: True bei Erfolg, sonst False.
    """
    from resources.lib import favourites_merge as fm
    if os.path.isfile(LOCAL_FAVOURITES):
        try:
            shutil.copy2(LOCAL_FAVOURITES, LOCAL_FAVOURITES + '.bak')
        except OSError as e:
            log("favourites.xml.bak konnte nicht erstellt werden: %s" % e, xbmc.LOGWARNING)
    backend = _get_backend()
    ftp_path = _remote_path(CUSTOM_FOLDER, 'favourites.xml')
    userdata_dir = os.path.dirname(LOCAL_FAVOURITES)
    server_temp = os.path.join(userdata_dir, 'favourites_server.xml')
    try:
        local_actions = fm.parse_favourites(LOCAL_FAVOURITES)
        server_actions = []
        if backend.download(ftp_path, server_temp):
            server_actions = fm.parse_favourites(server_temp)
        if FAVOURITES_SYNC_MODE == 'overwrite':
            merged = server_actions
        else:
            merged = fm.merge_union(local_actions, server_actions)
        fm.write_favourites(LOCAL_FAVOURITES, merged)
        return backend.upload(LOCAL_FAVOURITES, ftp_path)
    finally:
        if os.path.isfile(server_temp):
            try:
                os.remove(server_temp)
            except OSError:
                pass

def sync_static_favourites():
    """
    Synchronisiert statische Favoritenordner (z.B. Anime, Horror) mit Union-Merge.
    Speicherort: addon_data/plugin.program.dokukanal.buildsync/Static Favourites/<folder>/favourites.xml

    Returns:
        bool: True wenn mindestens ein Ordner verarbeitet wurde.
    """
    from resources.lib import favourites_merge as fm
    if not STATIC_FOLDERS:
        return False
    backend = _get_backend()
    userdata_dir = os.path.dirname(LOCAL_FAVOURITES)
    server_temp = os.path.join(userdata_dir, 'favourites_server_static.xml')
    for folder in STATIC_FOLDERS:
        folder_dir = os.path.join(STATIC_FAVOURITES_PATH, folder)
        if not xbmcvfs.exists(folder_dir):
            xbmcvfs.mkdirs(folder_dir)
        local_static_path = os.path.join(folder_dir, 'favourites.xml')
        remote_static_path = _remote_path(CUSTOM_FOLDER, folder, 'favourites.xml')
        try:
            local_actions = fm.parse_favourites(local_static_path) if xbmcvfs.exists(local_static_path) else []
            server_actions = []
            if backend.download(remote_static_path, server_temp):
                server_actions = fm.parse_favourites(server_temp)
            if FAVOURITES_SYNC_MODE == 'overwrite':
                merged = server_actions
            else:
                merged = fm.merge_union(local_actions, server_actions)
            fm.write_favourites(local_static_path, merged)
            backend.upload(local_static_path, remote_static_path)
        finally:
            if os.path.isfile(server_temp):
                try:
                    os.remove(server_temp)
                except OSError:
                    pass
    return True

def _update_background_skin_string():
    """Aktualisiert Skin.String(home.slideshowpath) damit das Skin das neue Hintergrundbild anzeigt.
    Immer lokaler Pfad (doku_background.jpg), da Kodi/Skin HTTP-URLs in Bildpfaden oft nicht unterstützt."""
    try:
        xbmc.executebuiltin('Skin.SetString(home.slideshowpath,special://userdata/doku_background.jpg)')
    except Exception as e:
        log("_update_background_skin_string: %s" % e, xbmc.LOGDEBUG)


def _copy_image_to_targets(source_path):
    """Copy image file from source_path to LOCAL_IMAGE_PATH (doku_background.jpg)."""
    try:
        with open(source_path, 'rb') as f:
            img_data = f.read()
        with open(LOCAL_IMAGE_PATH, 'wb') as f:
            f.write(img_data)
        _update_background_skin_string()
        return True
    except Exception as e:
        log(f"Failed to copy image to target: {e}", xbmc.LOGERROR)
        return False


def download_random_image():
    """
    Lädt ein zufälliges Bild (URL-Liste, lokaler Ordner oder Netzwerkpfad) und speichert es lokal.

    Returns:
        bool: True bei Erfolg, False wenn kein Bild geladen wurde.
    """
    if not ENABLE_IMAGE_ROTATION:
        return False

    # Bildquelle 0 = URL-Liste
    if IMAGE_SOURCE_IDX == 0:
        if not IMAGE_LIST_URL:
            return False
        try:
            with urllib.request.urlopen(IMAGE_LIST_URL) as response:
                content = response.read().decode('utf-8')
                image_urls = re.findall(r'\[img\](.*?)\[/img\]', content)
                if not image_urls:
                    log("No image URLs found in the list", xbmc.LOGERROR)
                    return False
                random_image_url = random.choice(image_urls)
                with urllib.request.urlopen(random_image_url) as img_response:
                    img_data = img_response.read()
                    with open(LOCAL_IMAGE_PATH, 'wb') as f:
                        f.write(img_data)
                if IMAGE_DISPLAY_MODE == 1:
                    try:
                        with open(BACKGROUND_URL_FILE, 'w') as f:
                            f.write(random_image_url)
                    except Exception:
                        pass
                    if time.time() >= _IMAGE_NOTIFICATION_QUIET_UNTIL:
                        show_notification(30180, 5000)
                else:
                    if time.time() >= _IMAGE_NOTIFICATION_QUIET_UNTIL:
                        show_notification(30031, 5000)
                _update_background_skin_string()
                xbmc.executebuiltin('ReloadSkin()')
                return True
        except Exception as e:
            log(f"Failed to download random image from URL: {e}", xbmc.LOGERROR)
            return False

    # Bildquelle 1 = Lokaler Ordner
    if IMAGE_SOURCE_IDX == 1:
        if not IMAGE_LOCAL_FOLDER or not os.path.isdir(IMAGE_LOCAL_FOLDER):
            return False
        try:
            files = [f for f in os.listdir(IMAGE_LOCAL_FOLDER)
                     if f.lower().endswith(IMAGE_EXTENSIONS)]
            if not files:
                return False
            chosen = os.path.join(IMAGE_LOCAL_FOLDER, random.choice(files))
            if _copy_image_to_targets(chosen):
                if time.time() >= _IMAGE_NOTIFICATION_QUIET_UNTIL:
                    show_notification(30031, 5000)
                xbmc.executebuiltin('ReloadSkin()')
                return True
        except Exception as e:
            log(f"Failed to pick image from local folder: {e}", xbmc.LOGERROR)
        return False

    # Bildquelle 2 = Netzwerkpfad (SMB/NFS)
    if IMAGE_SOURCE_IDX == 2:
        if not IMAGE_NETWORK_PATH:
            return False
        path = IMAGE_NETWORK_PATH.rstrip('/') + '/'
        try:
            dirs, files = xbmcvfs.listdir(path)
            images = [f for f in files if f.lower().endswith(IMAGE_EXTENSIONS)]
            if not images:
                return False
            chosen_name = random.choice(images)
            source_url = path + chosen_name
            f = xbmcvfs.File(source_url, 'rb')
            img_data = f.read()
            f.close()
            with open(LOCAL_IMAGE_PATH, 'wb') as out:
                out.write(img_data)
            _update_background_skin_string()
            if time.time() >= _IMAGE_NOTIFICATION_QUIET_UNTIL:
                show_notification(30031, 5000)
            xbmc.executebuiltin('ReloadSkin()')
            return True
        except Exception as e:
            log(f"Failed to pick image from network path: {e}", xbmc.LOGERROR)
        return False

    # Bildquelle 3 = Picsum.photos (Random)
    if IMAGE_SOURCE_IDX == 3:
        try:
            url = 'https://picsum.photos/1920/1080'
            req = urllib.request.Request(url, headers={'User-Agent': 'Kodi-AutoFTPSync/1.0'})
            with urllib.request.urlopen(req) as response:
                img_data = response.read()
            with open(LOCAL_IMAGE_PATH, 'wb') as f:
                f.write(img_data)
            if IMAGE_DISPLAY_MODE == 1:
                try:
                    url_saved = 'https://picsum.photos/1920/1080?random=%d' % int(time.time())
                    with open(BACKGROUND_URL_FILE, 'w') as f:
                        f.write(url_saved)
                except Exception:
                    pass
                if time.time() >= _IMAGE_NOTIFICATION_QUIET_UNTIL:
                    show_notification(30180, 5000)
            else:
                if time.time() >= _IMAGE_NOTIFICATION_QUIET_UNTIL:
                    show_notification(30031, 5000)
            _update_background_skin_string()
            xbmc.executebuiltin('ReloadSkin()')
            return True
        except Exception as e:
            log("Failed to download image from Picsum: %s" % e, xbmc.LOGERROR)
        return False

    return False


def ensure_remote_structure():
    """
    Legt die benötigte Remote-Ordnerstruktur (Hauptordner + statische Unterordner) an.
    Bei Fehlschlag: eine Meldung (30127) mit Verweis auf die Anleitung.
    Ohne konfigurierte Verbindung (kein Host): nichts tun, keine Meldung.

    Returns:
        bool: True wenn alle Ordner existieren (oder angelegt wurden), sonst False.
    """
    if not CUSTOM_FOLDER:
        return True
    if not _has_connection_configured():
        return True
    backend = _get_backend()
    main_folder = _remote_path(CUSTOM_FOLDER)
    folders_to_ensure = [main_folder] + [_remote_path(CUSTOM_FOLDER, f) for f in STATIC_FOLDERS]
    for path in folders_to_ensure:
        if backend.folder_exists(path):
            continue
        ensure = getattr(backend, 'ensure_folder', None)
        if callable(ensure):
            ensure(path)
        if not backend.folder_exists(path):
            show_notification(30127, 8000)  # Ordner konnten nicht angelegt werden → manuell (Anleitung)
            return False
    return True


def _favourites_local_backup_only():
    """Erstellt nur das lokale favourites.xml.bak (ohne Server). Returns True wenn Datei existierte."""
    if not os.path.isfile(LOCAL_FAVOURITES):
        return False
    try:
        shutil.copy2(LOCAL_FAVOURITES, LOCAL_FAVOURITES + '.bak')
        return True
    except OSError as e:
        log("favourites.xml.bak konnte nicht erstellt werden: %s" % e, xbmc.LOGWARNING)
        return False


def sync_favourites(no_notification=False):
    """
    Startet die Synchronisation der Standard-Favoriten sowie der statischen Ordner.
    Bei fehlender Verbindung: nur lokales .bak erstellen und Hinweis anzeigen.

    Args:
        no_notification: Wenn True, keine Notification anzeigen (z. B. Caller zeigt Dialog).

    Returns:
        (success: bool, message_id: int) für Anzeige durch Caller, sonst (None, None) bei alter Nutzung.
    """
    _load_settings()

    def _notify(msg_id, *a, **kw):
        if not no_notification:
            show_notification(msg_id, *a, **kw)

    # Zuerst: Keine Verbindung konfiguriert → nur lokale .bak erstellen und Erfolg anzeigen
    if not _has_connection_configured():
        if _favourites_local_backup_only():
            bak_path = LOCAL_FAVOURITES + '.bak'
            _notify(30220, 5000, path=bak_path)
            return (True, 30220, {'path': bak_path})
        _notify(30028, 5000)
        return (False, 30028)

    # Verbindung konfiguriert, aber kein benutzerdefinierter Ordner gesetzt
    if not CUSTOM_FOLDER:
        _notify(30022, 5000)
        return (False, 30022)

    p = _get_active_profile_settings()

    try:
        if not ensure_remote_structure():
            return (False, 30146)

        backend = _get_backend()
        if not backend.folder_exists(_remote_path(CUSTOM_FOLDER)):
            _notify(30023, 5000, folder=CUSTOM_FOLDER)
            return (False, 30023, {'folder': CUSTOM_FOLDER})

        result_std = sync_standard_favourites()
        result_stat = sync_static_favourites()

        if result_std or result_stat:
            _notify(30024, 5000)
            ct_map = {0: 'FTP', 1: 'SFTP', 2: 'SMB'}
            ct = ct_map.get(p.get('connection_type'), 'FTP')
            local_dir = os.path.dirname(LOCAL_FAVOURITES)
            remote_base = _remote_path(CUSTOM_FOLDER)
            return (True, 30314, {
                'connection': ct,
                'local': local_dir or LOCAL_FAVOURITES,
                'remote': remote_base,
            })
        _notify(30028, 5000)
        return (False, 30028)
    except Exception as e:
        log("sync_favourites failed: %s" % str(e), xbmc.LOGERROR)
        _notify(30146, 5000)
        return (False, 30315, {'error': str(e)})

def sync_addon_data():
    """
    Synchronisiert den addon_data-Ordner (lokal -> FTP / FTP -> lokal) mittels einer ZIP-Datei.

    Returns:
        bool: False, wenn die Funktion nicht ausgeführt wurde (z.B. deaktiviert). Sonst kein bestimmter Rückgabewert bei Erfolg.
    """
    if not ENABLE_ADDON_SYNC:
        return False  # Falls auf 'false' gesetzt, abbrechen
    if not CUSTOM_FOLDER and not IS_MAIN_SYSTEM:
        log("sync_addon_data: Custom Folder nicht gesetzt, überspringe Download.", xbmc.LOGINFO)
        return False

    log("Starte sync_addon_data() mit ZIP-Variante", xbmc.LOGINFO)
    local_base_path = xbmcvfs.translatePath('special://userdata/addon_data')
    local_zip_path = os.path.join(xbmcvfs.translatePath('special://userdata'), 'addon_data.zip')
    remote_zip_path = _remote_path(CUSTOM_FOLDER, 'addon_data.zip')

    def create_zip(source_dir, zip_path):
        """
        Erstellt eine ZIP-Datei von einem Quellverzeichnis.

        Args:
            source_dir (str): Pfad zum Quellordner.
            zip_path (str): Zielpfad für das ZIP.

        Returns:
            None
        """
        try:
            log(f"Starte die Erstellung der ZIP-Datei: {zip_path}", xbmc.LOGINFO)
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(source_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, source_dir)
                        zipf.write(file_path, arcname)
                        log(f"Datei zur ZIP hinzugefügt: {file_path} -> {arcname}", xbmc.LOGINFO)
            log(f"ZIP-Datei erstellt: {zip_path}", xbmc.LOGINFO)
        except Exception as e:
            log(f"Fehler beim Erstellen der ZIP-Datei: {str(e)}", xbmc.LOGERROR)

    def extract_zip(zip_path, target_dir):
        """
        Entpackt eine ZIP-Datei in ein Zielverzeichnis.

        Args:
            zip_path (str): Pfad zur ZIP-Datei.
            target_dir (str): Zielverzeichnis für das Entpacken.

        Returns:
            None
        """
        try:
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                zipf.extractall(target_dir)
                log(f"ZIP-Datei erfolgreich entpackt: {zip_path} -> {target_dir}", xbmc.LOGINFO)
        except Exception as e:
            log(f"Fehler beim Entpacken der ZIP-Datei: {str(e)}", xbmc.LOGERROR)

    backend = _get_backend()
    if IS_MAIN_SYSTEM:
        # ================
        # Upload-Zweig
        # ================
        if not backend.folder_exists(_remote_path(CUSTOM_FOLDER)):
            log("sync_addon_data: Remote-Ordner fehlt.", xbmc.LOGWARNING)
            show_notification(30123, 5000)
            return False
        log("Hauptsystem erkannt. Beginne ZIP-Erstellung.", xbmc.LOGINFO)
        if os.path.exists(local_base_path):
            create_zip(local_base_path, local_zip_path)
            if os.path.exists(local_zip_path):
                log(f"ZIP-Datei vorhanden: {local_zip_path}", xbmc.LOGINFO)
                if backend.upload(local_zip_path, remote_zip_path):
                    log(f"ZIP erfolgreich hochgeladen: {remote_zip_path}", xbmc.LOGINFO)
                    os.remove(local_zip_path)
                    show_notification(30020, 5000)  # z.B. "Addon-Daten erfolgreich hochgeladen"
                else:
                    log("FTP-Upload fehlgeschlagen.", xbmc.LOGERROR)
                    show_notification(30029, 5000)  # z.B. "Fehler beim Upload"
            else:
                log(f"FEHLER: ZIP-Datei wurde nicht erstellt: {local_zip_path}", xbmc.LOGERROR)
        else:
            log("Lokaler Ordner 'addon_data' existiert nicht.", xbmc.LOGERROR)

    else:
        # ===================
        # Download-Zweig
        # ===================
        if not backend.folder_exists(_remote_path(CUSTOM_FOLDER)):
            log("sync_addon_data: Remote-Ordner fehlt.", xbmc.LOGWARNING)
            show_notification(30123, 5000)
            return False
        log("Kein Hauptsystem. Versuche ZIP herunterzuladen.", xbmc.LOGINFO)
        # 1. ZIP herunterladen
        if backend.download(remote_zip_path, local_zip_path):
            log(f"ZIP-Datei vom Server heruntergeladen: {local_zip_path}", xbmc.LOGINFO)

            # 2. ZIP entpacken ins addon_data-Verzeichnis
            extract_zip(local_zip_path, local_base_path)

            # 3. Delete local ZIP again
            if os.path.exists(local_zip_path):
                os.remove(local_zip_path)
                log(f"Lokale ZIP-Datei gelöscht: {local_zip_path}", xbmc.LOGINFO)
            show_notification(30025, 5000)  # "Addon-Daten heruntergeladen & entpackt"
        else:
            log("ZIP-Download vom FTP fehlgeschlagen.", xbmc.LOGERROR)
            show_notification(30021, 5000)  # "Fehler beim Herunterladen"

def run_startup():
    """
    Hauptablauf beim Service-Start (Kodi startet service.py).
    Wird nur von service.py aufgerufen; beim "import auto_ftp_sync" nicht ausgefuehrt.
    """
    try:
        monitor = xbmc.Monitor()
        if monitor.waitForAbort(3):
            pass
    except Exception as e:
        log("startup delay: %s" % e, xbmc.LOGDEBUG)

    try:
        from resources.lib.settings_init import ensure_settings_initialized
        ensure_settings_initialized()
    except Exception as e:
        log("ensure_settings_initialized: %s" % e, xbmc.LOGDEBUG)
    try:
        _load_settings()
    except Exception as e:
        log("_load_settings: %s" % e, xbmc.LOGERROR)

    try:
        from resources.lib import first_run
        first_run.maybe_run()
    except Exception as e:
        log("first-run wizard: %s" % e, xbmc.LOGDEBUG)

    try:
        if not ENABLED:
            pass
        else:
            global _IMAGE_NOTIFICATION_QUIET_UNTIL
            _IMAGE_NOTIFICATION_QUIET_UNTIL = time.time() + 90
            from resources.lib import auto_clean
            _mon = xbmc.Monitor()
            log("Funktionen werden ausgefuehrt.", xbmc.LOGINFO)
            if _mon.abortRequested():
                pass
            else:
                try:
                    auto_clean.run_if_due()
                except Exception as e:
                    log("auto_clean.run_if_due: %s" % e, xbmc.LOGERROR)
            if _mon.abortRequested():
                pass
            elif _has_connection_configured():
                try:
                    ensure_remote_structure()
                except Exception as e:
                    log("ensure_remote_structure: %s" % e, xbmc.LOGERROR)
            if _mon.abortRequested():
                pass
            elif _has_connection_configured():
                try:
                    sync_addon_data()
                except Exception as e:
                    log("sync_addon_data: %s" % e, xbmc.LOGERROR)
            if _mon.abortRequested():
                pass
            else:
                try:
                    sync_favourites(no_notification=True)
                except Exception as e:
                    log("sync_favourites: %s" % e, xbmc.LOGERROR)
            if _mon.abortRequested():
                pass
            else:
                try:
                    download_random_image()
                except Exception as e:
                    log("download_random_image: %s" % e, xbmc.LOGERROR)
            if _mon.abortRequested():
                pass
            else:
                try:
                    auto_clean.clear_thumbs()
                    xbmc.executebuiltin('ReloadSkin()')
                    xbmc.executebuiltin('Container.Refresh()')
                except Exception as e:
                    log("clear_thumbs/ReloadSkin: %s" % e, xbmc.LOGERROR)

            if not _mon.abortRequested() and FAVOURITES_SYNC_INTERVAL_MINUTES > 0:
                interval_sec = FAVOURITES_SYNC_INTERVAL_MINUTES * 60
                period_monitor = xbmc.Monitor()
                while True:
                    if period_monitor.waitForAbort(interval_sec):
                        break
                    try:
                        _load_settings()
                    except Exception:
                        pass
                    if not ENABLED or not CUSTOM_FOLDER:
                        continue
                    try:
                        sync_favourites(no_notification=True)
                    except Exception as e:
                        log("sync_favourites (periodic): %s" % e, xbmc.LOGERROR)
    except Exception as e:
        log("startup: %s" % e, xbmc.LOGERROR)


if __name__ == "__main__":
    run_startup()
