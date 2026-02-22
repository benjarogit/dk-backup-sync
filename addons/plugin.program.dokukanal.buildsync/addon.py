# -*- coding: utf-8 -*-
"""
Entry-Point und Routing. action -> eine Service-Funktion; keine Business-Logik im Router.
Handle -1 (Einstellungen): Marker-Logik; Listen-APIs nicht aufrufen.
"""
import os
import sys
import urllib.parse
import time
import xbmcvfs

from core import config
from core import kodi_api
from core import logging_utils
from core import settings
from utils.params import Params
from ui import dialogs
from ui import list_builder

ADDON = config.ADDON
ADDON_ID = config.ADDON_ID
ADDON_PATH = config.ADDON_PATH
ADDON_URL = "plugin://%s" % ADDON_ID
L = settings.L
log = logging_utils.log

_ACTION_MARKER_PATH = 'special://userdata/addon_data/%s/.dialog_action_marker' % ADDON_ID
_ACTION_MARKER_MAX_AGE = 20

try:
    HANDLE = int(sys.argv[1]) if len(sys.argv) > 1 else 0
except (ValueError, IndexError, TypeError):
    HANDLE = -1


def _format_sync_result(result):
    """Lokalisierte Meldung aus save_favorites-Rueckgabe."""
    if not result or not isinstance(result, (tuple, list)) or len(result) < 2:
        return None
    msg_id = result[1]
    fmt_args = result[2] if len(result) == 3 and isinstance(result[2], dict) else None
    try:
        return L(msg_id).format(**fmt_args) if fmt_args else L(msg_id)
    except (KeyError, TypeError):
        return L(msg_id)


def _run_action(action, connection=None, topic=None):
    """Dispatcher: action -> eine Service-Funktion + UI."""
    log("_run_action(action=%s)" % action, 1)
    if action == 'backup':
        from services import backup_service
        def do_backup():
            progress = kodi_api.DialogProgress()
            progress.create(L(30001), L(30040))
            def progress_cb(i, total, arcname):
                if progress.iscanceled():
                    return True
                pct = int((i + 1) / total * 100) if total else 0
                progress.update(pct, "%d / %d\n%s" % (i + 1, total, arcname))
                return False
            try:
                success, msg = backup_service.create_backup(progress_callback=progress_cb)
                dialogs.show_result(L(30001), msg)
            finally:
                try:
                    progress.close()
                except Exception:
                    pass
        from resources.lib import backup_restore
        backup_location = backup_restore.get_backup_path_display()
        backup_message = "%s\n\n%s: %s" % (L(30304), L(30051), backup_location)
        dialogs.confirm_then_run(L(30060), backup_message, do_backup, yeslabel=L(30311), nolabel=L(30228))
    elif action == 'restore':
        from resources.lib import backup_restore
        backup_restore.run_restore()
    elif action == 'autoclean':
        from services import autoclean_service
        def do_autoclean():
            success, msg = autoclean_service.run_autoclean()
            autoclean_service.set_next_run()
            dialogs.show_result(L(30001) if success else ADDON.getAddonInfo('name'), msg)
        dialogs.confirm_then_run(L(30054), L(30303), do_autoclean, yeslabel=L(30313), nolabel=L(30228))
    elif action == 'settings':
        ADDON.openSettings()
    elif action == 'info' or (action and action.startswith('info_')):
        topic = topic or (action[5:] if action.startswith('info_') else None)
        _show_info_dialog(topic)
    elif action == 'instructions':
        _run_instructions()
    elif action and action.startswith('show_help_'):
        topic = action.replace('show_help_', '', 1)
        _show_info_dialog(topic)
    elif action == 'open_plugin':
        kodi_api.executebuiltin('ActivateWindow(10025, "plugin://plugin.program.dokukanal.buildsync/", return)')
    elif action == 'test_connection':
        from services import network_service
        summary = network_service.get_connection_summary(connection)
        message = "%s\n\n%s" % (L(30306), summary)
        def do_test():
            progress = kodi_api.DialogProgress()
            progress.create(L(30144), L(30307))
            try:
                success, msg = network_service.test_connection(connection)
                progress.close()
                kodi_api.sleep(200)
                dialogs.show_result(L(30144) if success else ADDON.getAddonInfo('name'), msg)
            except Exception as e:
                try:
                    progress.close()
                except Exception:
                    pass
                log("test_connection: %s" % e, 3)
                kodi_api.sleep(200)
                dialogs.show_result(ADDON.getAddonInfo('name'), str(e))
        dialogs.confirm_then_run(L(30144), message, do_test, yeslabel=L(30227), nolabel=L(30228))
    elif action == 'about':
        _show_about_dialog()
    elif action == 'debug':
        kodi_api.executebuiltin('ActivateWindow(1288)')
    elif action == 'install_skin':
        from services import skin_install_service
        ok, msg = skin_install_service.install_skin_or_show_info()
        if ok:
            dialogs.show_result(L(30174), msg)
        else:
            kodi_api.sleep(300)
    elif action in ('wizard', 'first_run_again'):
        from services import wizard_service
        wizard_service.reset_and_run_wizard()
    elif action == 'sync_favourites_now':
        from services import favorites_service, network_service
        summary = network_service.get_connection_summary()
        fav_message = "%s\n\n%s" % (L(30301), summary)
        def do_sync():
            progress = kodi_api.DialogProgress()
            progress.create(L(30202), L(30300))
            try:
                result = favorites_service.save_favorites(no_notification=True)
                progress.close()
                kodi_api.sleep(200)
                msg = _format_sync_result(result)
                if not (msg or '').strip():
                    msg = L(30146)
                success = result and isinstance(result, (tuple, list)) and len(result) >= 1 and result[0]
                title = L(30202) if success else ADDON.getAddonInfo('name')
                msg_flat = (msg or '').replace('[CR]', ' ').replace('\n', ' ').strip()[:200]
                try:
                    kodi_api.executebuiltin('Notification(%s,%s,10000,%s)' % (title, msg_flat, config.ICON_PATH))
                except Exception:
                    pass
                dialogs.show_result(title, msg)
            except Exception as e:
                try:
                    progress.close()
                except Exception:
                    pass
                log("sync_favourites_now: %s" % e, 3)
                kodi_api.sleep(200)
                dialogs.show_result(ADDON.getAddonInfo('name'), str(e))
        dialogs.confirm_then_run(L(30202), fav_message, do_sync, yeslabel=L(30310), nolabel=L(30228))
    elif action == 'test_image_sources':
        from services import network_service
        summary = network_service.get_image_source_summary()
        message = "%s\n\n%s" % (L(30302), summary)
        def do_test():
            progress = kodi_api.DialogProgress()
            progress.create(L(30200), L(30300))
            try:
                success, msg, tested_source = network_service.test_image_sources()
                progress.close()
                kodi_api.sleep(200)
                result_text = msg
                if tested_source:
                    result_text = "%s\n\n%s" % (msg, L(30316) % tested_source)
                dialogs.show_result(L(30200) if success else ADDON.getAddonInfo('name'), result_text)
            except Exception as e:
                try:
                    progress.close()
                except Exception:
                    pass
                dialogs.show_result(ADDON.getAddonInfo('name'), str(e))
        dialogs.confirm_then_run(L(30200), message, do_test, yeslabel=L(30227), nolabel=L(30228))
    else:
        log("Unknown action: %s" % action, 0)


def _show_info_dialog(topic=None):
    if topic == 'server':
        title, text = L(30150), L(30151)
    elif topic == 'ordner':
        title, text = L(30152), L(30153)
    elif topic == 'verbindung':
        title, text = L(30154), L(30155)
    elif topic == 'backup':
        title, text = L(30156), L(30157)
    elif topic == 'empfohlen':
        title, text = L(30158), L(30159)
    elif topic == 'dateimanager':
        title, text = L(30172), L(30171)
    elif topic == 'general':
        title, text = L(30343), L(30344)
    elif topic == 'favourites':
        title, text = L(30345), L(30346)
    elif topic == 'connection':
        title, text = L(30154), L(30155)
    elif topic == 'image':
        title, text = L(30349), L(30350)
    elif topic == 'autoclean':
        title, text = L(30351), L(30352)
    elif topic == 'skin':
        title, text = L(30353), L(30354)
    else:
        title, text = L(30073), L(30074)
    dialogs.show_text(title, text)


def _run_instructions():
    """Show list of instruction topics; on selection show _show_info_dialog(topic)."""
    topics = [
        ('general', L(30343)),
        ('favourites', L(30345)),
        ('connection', L(30147)),
        ('backup', L(30156)),
        ('image', L(30349)),
        ('autoclean', L(30351)),
        ('skin', L(30353)),
    ]
    labels = [t[1] for t in topics]
    idx = kodi_api.Dialog().select(L(30342), labels)
    if idx >= 0 and idx < len(topics):
        _show_info_dialog(topics[idx][0])


def _show_about_dialog():
    plugin_name = ADDON.getAddonInfo('name')
    plugin_version = ADDON.getAddonInfo('version')
    skin_id = kodi_api.get_info_label('Skin.Id') or ''
    skin_name = kodi_api.get_info_label('Skin.Name') or skin_id or L(30075)
    skin_version = ''
    if skin_id:
        try:
            import xbmcaddon
            skin_addon = xbmcaddon.Addon(skin_id)
            skin_version = skin_addon.getAddonInfo('version') or ''
        except Exception:
            pass
    lines = ["Plugin: %s" % plugin_name, "Version: %s" % plugin_version, "Skin: %s" % skin_name]
    if skin_version:
        lines.append("Skin-Version: %s" % skin_version)
    if skin_id == 'skin.dokukanal':
        lines.append("")
        lines.append(L(30080))
    dialogs.show_text(L(30079), "[CR]".join(lines))


def _maybe_show_changelog_once():
    try:
        current = ADDON.getAddonInfo('version') or ''
        seen = ADDON.getSettingString('changelog_seen_version') or ''
        if seen and seen != current and current:
            kodi_api.Dialog().ok(L(30134), L(30135) % current)
        ADDON.setSettingString('changelog_seen_version', current)
    except Exception as e:
        log("changelog check: %s" % e, 0)


def route_main():
    if HANDLE < 0:
        return
    try:
        if xbmcvfs.exists(_ACTION_MARKER_PATH):
            try:
                f = xbmcvfs.File(_ACTION_MARKER_PATH, 'r')
                raw = f.read()
                f.close()
                t = float((raw or '').strip())
                if (time.time() - t) < _ACTION_MARKER_MAX_AGE:
                    list_builder.end_of_directory(HANDLE)
                    return
            except (ValueError, OSError, IOError, TypeError):
                pass
    except Exception:
        pass
    try:
        settings.ensure_settings_initialized()
    except Exception as e:
        log("settings init: %s" % e, 3)
    _maybe_show_changelog_once()
    list_builder.set_plugin_category(HANDLE, ADDON.getAddonInfo('name'))
    list_builder.add_item(HANDLE, L(30190), 'sync_favourites_now')
    list_builder.add_item(HANDLE, L(30144), 'test_connection')
    list_builder.add_item(HANDLE, L(30060), 'backup')
    list_builder.add_item(HANDLE, L(30063), 'restore')
    list_builder.add_item(HANDLE, L(30200), 'test_image_sources')
    list_builder.add_item(HANDLE, L(30054), 'autoclean')
    list_builder.add_item(HANDLE, L(30174), 'install_skin')
    list_builder.add_item(HANDLE, L(30342), 'instructions')
    list_builder.add_item(HANDLE, L(30191), 'settings')
    list_builder.end_of_directory(HANDLE)


def _add_settings_actions_items():
    if HANDLE < 0:
        return
    list_builder.set_plugin_category(HANDLE, L(30201))
    list_builder.add_item(HANDLE, L(30191), 'settings')
    list_builder.add_item(HANDLE, L(30190), 'sync_favourites_now')
    list_builder.add_item(HANDLE, L(30060), 'backup')
    list_builder.add_item(HANDLE, L(30063), 'restore')
    list_builder.add_item(HANDLE, L(30054), 'autoclean')
    list_builder.add_item(HANDLE, L(30196), 'test_connection', connection='1')
    list_builder.add_item(HANDLE, L(30197), 'test_connection', connection='2')
    list_builder.add_item(HANDLE, L(30198), 'test_connection', connection='3')
    list_builder.add_item(HANDLE, L(30200), 'test_image_sources')
    list_builder.add_item(HANDLE, L(30174), 'install_skin')
    list_builder.add_item(HANDLE, L(30192), 'info')
    list_builder.end_of_directory(HANDLE)


def route_category(name):
    if HANDLE < 0:
        return
    if name == 'settings_actions':
        _add_settings_actions_items()
    elif name == 'maintenance':
        list_builder.set_plugin_category(HANDLE, L(30070))
        list_builder.add_item(HANDLE, L(30060), 'backup')
        list_builder.add_item(HANDLE, L(30063), 'restore')
        list_builder.add_item(HANDLE, L(30054), 'autoclean')
        list_builder.end_of_directory(HANDLE)
    elif name == 'sync':
        list_builder.set_plugin_category(HANDLE, L(30069))
        list_builder.add_item(HANDLE, L(30190), 'sync_favourites_now')
        list_builder.add_item(HANDLE, L(30144), 'test_connection')
        list_builder.add_item(HANDLE, L(30196), 'test_connection', connection='1')
        list_builder.add_item(HANDLE, L(30197), 'test_connection', connection='2')
        list_builder.add_item(HANDLE, L(30198), 'test_connection', connection='3')
        list_builder.add_item(HANDLE, L(30200), 'test_image_sources')
        list_builder.add_item(HANDLE, L(30192), 'info')
        list_builder.add_item(HANDLE, L(30071), 'info', topic='server')
        list_builder.add_item(HANDLE, L(30079), 'about')
        list_builder.add_item(HANDLE, L(30100), 'wizard')
        list_builder.add_item(HANDLE, L(30193), 'install_skin')
        list_builder.end_of_directory(HANDLE)
    elif name == 'info':
        list_builder.set_plugin_category(HANDLE, L(30071))
        list_builder.add_item(HANDLE, L(30192), 'info')
        list_builder.add_item(HANDLE, L(30137), 'info')
        list_builder.add_item(HANDLE, L(30172), 'info', topic='dateimanager')
        list_builder.add_item(HANDLE, L(30138), 'debug')
        list_builder.end_of_directory(HANDLE)
    else:
        route_main()


def route_static(p):
    from utils import static_favourites
    folder_name = p.get_folder()
    if not folder_name and p.get_path():
        path_dec = urllib.parse.unquote_plus(p.get_path() or '')
        folder_name = path_dec.replace('\\', '/').strip('/').split('/')[-1]
    if folder_name and HANDLE >= 0:
        items = static_favourites.read_favourites(folder_name)
        for name, thumb, cmd in items:
            url = "%s/?action=execute&cmd=%s" % (ADDON_URL, urllib.parse.quote_plus(cmd))
            li = kodi_api.ListItem(label=name)
            if thumb:
                li.setArt({'icon': thumb, 'thumb': thumb})
            kodi_api.add_directory_item(handle=HANDLE, url=url, listitem=li, is_folder=False)
    list_builder.end_of_directory(HANDLE)


def route_execute(p):
    cmd = p.get_cmd()
    if cmd:
        cmd = urllib.parse.unquote_plus(cmd)
        if cmd:
            kodi_api.executebuiltin(cmd)
    list_builder.end_of_directory(HANDLE)
    sys.exit(0)


# --- Entry ---
_raw_url = sys.argv[2] if len(sys.argv) > 2 else ''
_param_str = _raw_url.split('?', 1)[1] if '?' in _raw_url else (_raw_url.lstrip('?') if _raw_url else '')
p = Params(_param_str)
action = p.get_action() or p.get_mode()
DIRECT_ACTIONS = frozenset([
    'backup', 'restore', 'autoclean', 'settings', 'sync_favourites_now', 'info', 'info_server', 'info_ordner',
    'info_verbindung', 'info_backup', 'info_empfohlen', 'info_dateimanager', 'test_connection', 'test_image_sources',
    'about', 'debug', 'install_skin', 'wizard', 'first_run_again', 'test_connection_1', 'test_connection_2', 'test_connection_3',
    'instructions', 'open_plugin',
    'show_help_general', 'show_help_favourites', 'show_help_connection', 'show_help_image', 'show_help_backup', 'show_help_autoclean'
])
if action is None and _param_str and '=' not in _param_str:
    bare = (_param_str or '').strip()
    if bare in DIRECT_ACTIONS:
        action = bare
if action is None and len(sys.argv) >= 3:
    arg2 = (sys.argv[2] or '').strip()
    if arg2 in DIRECT_ACTIONS:
        action = arg2
    elif arg2 and '=' not in arg2:
        decoded = urllib.parse.unquote_plus(arg2)
        if decoded in DIRECT_ACTIONS:
            action = decoded
if action is None and len(sys.argv) >= 2:
    try:
        int(sys.argv[1])
    except (ValueError, TypeError, IndexError):
        action = (sys.argv[1] or '').strip() or None
if action is None and len(sys.argv) >= 2 and str(sys.argv[1]).strip() in DIRECT_ACTIONS:
    action = str(sys.argv[1]).strip()
connection = p.get('connection')
if len(sys.argv) >= 2 and str(sys.argv[1]) in ('test_connection_1', 'test_connection_2', 'test_connection_3'):
    action = 'test_connection'
    connection = str(sys.argv[1])[-1]
if action is None and _param_str and (_param_str or '').strip() in ('test_connection_1', 'test_connection_2', 'test_connection_3'):
    action = 'test_connection'
    connection = (_param_str or '').strip()[-1]
category_name = p.get_name()

if action == 'execute':
    route_execute(p)
    sys.exit(0)
if action == 'static':
    if HANDLE >= 0:
        route_static(p)
    sys.exit(0)
if action == 'settings_actions':
    if HANDLE >= 0:
        _add_settings_actions_items()
    sys.exit(0)
if action in DIRECT_ACTIONS:
    log("direct action=%s handle=%s" % (action, HANDLE), 1)
    if HANDLE == -1:
        try:
            f = xbmcvfs.File(_ACTION_MARKER_PATH, 'w')
            f.write(str(time.time()))
            f.close()
        except Exception:
            pass
    if HANDLE >= 0:
        list_builder.end_of_directory(HANDLE)
        kodi_api.sleep(100)
    try:
        _run_action(action, connection=connection, topic=p.get('topic') if action == 'info' else None)
    except Exception as e:
        log("_run_action failed: %s" % e, 3)
        dialogs.show_result(ADDON.getAddonInfo('name'), str(e) or L(30146))
    if HANDLE >= 0:
        kodi_api.sleep(500)
        kodi_api.executebuiltin("Container.Refresh(%s)" % ADDON_URL)
    sys.exit(0)
if action == 'category' and category_name:
    if HANDLE >= 0:
        route_category(category_name)
    sys.exit(0)
if HANDLE >= 0:
    route_main()
else:
    sys.exit(0)
