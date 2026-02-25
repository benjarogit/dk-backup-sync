# -*- coding: utf-8 -*-
"""
Autostop: stop paused playback after X minutes; sleep timer for playing playback.
Migrated from service.autostop (jbinkley60), integrated into BuildSync.
Uses Kodi Player API (works with xstream and all sources using Kodi player).
"""
import time
import xbmc
import xbmcgui
from resources.lib.common import ADDON_PATH, L, log, safe_get_string, safe_get_bool, safe_set_string

ADDON_ICON = ADDON_PATH + '/resources/images/icon.png'
NOTIFYCOUNT = [0]  # list so it's mutable in nested scope


def _get(setting_id, default=''):
    return safe_get_string(setting_id, default)


def _get_bool(setting_id, default=False):
    return safe_get_bool(setting_id, default)


def _set(setting_id, value):
    safe_set_string(setting_id, str(value) if value is not None else '')


def play_count(plcount, padjust, plflag, paflag, asevlog):
    """Compute play counter (seconds) depending on pause/play and padjust."""
    match = 0
    if plflag == 0 and paflag == 0:
        plcount = 0
        match = 1
    elif padjust == 'None':
        plcount += 1
        match = 2
    elif padjust == 'Pause' and plflag == 1:
        plcount += 1
        match = 3
    elif padjust == 'Pause' and paflag == 1:
        pass  # plcount = plcount
        match = 4
    elif padjust == 'Reset' and plflag == 1:
        plcount += 1
        match = 5
    elif padjust == 'Reset' and paflag == 1:
        plcount = 0
        match = 6

    if asevlog and plcount % 10 == 0:
        log('Autostop playCount: %s %s %s %s %s' % (plcount, padjust, plflag, paflag, match), xbmc.LOGINFO)
    return plcount


def sleep_notify(plcount, plstoptime, plflag, plnotify, plextend, asevlog, paflag):
    """Show sleep-timer notification and extension dialog."""
    extime = float(_get('autostop_extime', '0') or '0')
    notifyset = _get('autostop_notifyset', 'no')
    varextnotify = _get('autostop_varextnotify', 'no')
    totalstoptime = plstoptime + extime
    msgdialogprogress = xbmcgui.DialogProgress()

    if plstoptime > 0 and plcount + plnotify >= totalstoptime * 60 and (plflag > 0 or (plflag == 0 and paflag == 1)):
        if notifyset == 'no' and varextnotify == 'no':
            msgdialogprogress.create(L(30367), L(30368))
            _set('autostop_notifyset', 'yes')
            NOTIFYCOUNT[0] = 0
            log('Autostop notify counter started.', xbmc.LOGINFO)
        elif notifyset == 'yes':
            NOTIFYCOUNT[0] += 1
            if NOTIFYCOUNT[0] >= plnotify:
                percent = 0
                msgdialogprogress.close()
            else:
                percent = 100 - int(float(NOTIFYCOUNT[0]) / float(plnotify) * 100)
                tremain = str(plnotify - NOTIFYCOUNT[0])
                message = L(30368) + tremain + L(30369)
                msgdialogprogress.update(percent, message)
            if asevlog and plcount % 10 == 0:
                log('Autostop notify counter: %s %s %s %s %s %s' % (
                    plcount, plnotify, totalstoptime * 60, percent, NOTIFYCOUNT[0], plstoptime), xbmc.LOGINFO)
            if msgdialogprogress.iscanceled():
                if plextend > 0:
                    extime = extime + plextend
                    _set('autostop_extime', str(extime))
                    extmins = str(plextend)
                else:
                    extmins = var_extension(totalstoptime, plcount, asevlog)
                    extime = extime + float(extmins)
                    _set('autostop_extime', str(extime))
                msgdialogprogress.close()
                dialog = xbmcgui.Dialog()
                mgenlog = L(30370) + extmins + L(30371)
                log(mgenlog, xbmc.LOGINFO)
                dialog.notification(L(30372), mgenlog, ADDON_ICON, 3000)
                _set('autostop_notifyset', 'no')
        elif notifyset == 'yes' and plflag == 0 and paflag == 0:
            msgdialogprogress.close()
            _set('autostop_notifyset', 'no')

    if plflag > 0 and asevlog and plcount % 10 == 0:
        log('Autostop sleepNotify counter: %s %s %s' % (plcount + plnotify, plstoptime * 60, totalstoptime * 60), xbmc.LOGINFO)
    if plflag == 0 and paflag == 0 and extime > 0:
        _set('autostop_extime', '0')


def var_extension(plstoptime, plcount, asevlog):
    """Dialog for variable extension (minutes or end of file)."""
    pselect = [
        "10 minutes", "20 minutes", "30 minutes", "40 minutes",
        "50 minutes", "60 minutes", "90 minutes"
    ]
    remtime = check_time(plstoptime, plcount, asevlog)
    if float(remtime) > 0:
        pselect.append("End of current file (" + remtime + " mins)")
    if _get_bool('autostop_stopplay', False):
        pselect.append("[COLOR blue]Stop Playback Now[/COLOR]")

    ddialog = xbmcgui.Dialog()
    selection = ddialog.select(L(30373), pselect)
    if selection < 0:
        extension = '5'
    elif 'minutes' in pselect[selection]:
        extension = (pselect[selection])[:2].strip()
        if not extension.isdigit():
            extension = '10'
    elif 'End' in pselect[selection]:
        extension = check_time(plstoptime, plcount, asevlog)
    elif 'Stop' in pselect[selection]:
        extension = '0'
        stop_playback(L(30372), L(30374))
        return '0'
    else:
        extension = '5'
    return extension


def stop_playback(notifymsg, logmsg):
    """Stop playback, show notification, optional screensaver."""
    try:
        player = xbmc.Player()
        if player.isPlayingVideo():
            ptag = player.getVideoInfoTag()
            ptitle = ptag.getTitle() if ptag else ''
        elif player.isPlayingAudio():
            ptag = player.getMusicInfoTag()
            ptitle = ptag.getTitle() if ptag else ''
        else:
            ptitle = "playing file"
        pos = player.getTime()
        player.stop()
        mgenlog = logmsg + (ptitle or '') + ' at: ' + time.strftime("%H:%M:%S", time.gmtime(pos))
        log(mgenlog, xbmc.LOGINFO)
        dialog = xbmcgui.Dialog()
        dialog.notification(notifymsg, mgenlog, ADDON_ICON, 5000)
        if _get_bool('autostop_screensaver', False):
            xbmc.executebuiltin('ActivateScreensaver')
        if _get_bool('autostop_asreset', False):
            _set('autostop_plstop', '0')
            log('Autostop sleep timer reset to 0.', xbmc.LOGINFO)
        _set('autostop_notifyset', 'no')
        _set('autostop_varextnotify', 'no')
    except Exception as e:
        log('Autostop error when stopping playback: %s' % e, xbmc.LOGINFO)


def check_time(plstoptime, plcount, asevlog):
    """Remaining play time until end of file (for extension option)."""
    try:
        player = xbmc.Player()
        currpos = player.getTime()
        endpos = int(player.getTotalTime())
        remaintime = endpos - currpos - (plstoptime * 60 - plcount) - (10 - plcount % 10) - 1
        if remaintime > 10800:
            remaintime = 10800
        extension = '{:.2f}'.format(remaintime / float(60))
        if asevlog:
            log('Autostop extension time: %s %s %s %s %s' % (currpos, endpos, plcount, remaintime, extension), xbmc.LOGINFO)
        _set('autostop_varextnotify', 'yes')
        return extension
    except Exception as e:
        log('Autostop error getting remaining time: %s' % e, xbmc.LOGINFO)
    return '-1'


def check_notify():
    """Ensure notification time and stop time are not identical."""
    try:
        plnotify = int(_get('autostop_plnotify', '0') or '0')
        plstoptime = int(_get('autostop_plstop', '0') or '0')
        if plstoptime > 0 and plnotify == plstoptime * 60:
            _set('autostop_plnotify', '300')
            dialog = xbmcgui.Dialog()
            dialog.notification(L(30372), L(30375), ADDON_ICON, 5000)
    except Exception as e:
        log('Autostop checkNotify error: %s' % e, xbmc.LOGINFO)


class AutostopPlayer(xbmc.Player):
    def __init__(self):
        super(AutostopPlayer, self).__init__()
        self.paflag = 0
        self.plflag = 0

    def onPlayBackStarted(self):
        self.paflag = 0
        self.plflag = 1

    def onPlayBackPaused(self):
        self.paflag = 1
        self.plflag = 0

    def onPlayBackResumed(self):
        self.paflag = 0
        self.plflag = 1

    def onPlayBackEnded(self):
        self.paflag = 0
        self.plflag = 0

    def onPlayBackStopped(self):
        self.paflag = 0
        self.plflag = 0


def run_loop():
    """Main loop: run only when autostop_enabled. Runs in its own thread."""
    if not _get_bool('autostop_enabled', False):
        return
    _set('autostop_extime', '0')
    _set('autostop_notifyset', 'no')
    _set('autostop_varextnotify', 'no')
    check_notify()

    player = AutostopPlayer()
    monitor = xbmc.Monitor()
    pacount = 0
    plcount = 0

    log('Autostop service loop started.', xbmc.LOGINFO)

    while not monitor.abortRequested():
        pacount += 1
        padjust = _get('autostop_padjust', 'None')
        plstoptime = int(_get('autostop_plstop', '0') or '0')
        plnotify = int(_get('autostop_plnotify', '0') or '0')
        plextend = int(_get('autostop_plextend', '10') or '10')
        asevlog = 'true' if _get_bool('autostop_asevlog', False) else 'false'

        if pacount % 10 == 0:
            try:
                pastoptime = int(_get('autostop_pastop', '0') or '0')
                if pastoptime > 0 and pacount >= pastoptime * 60 and player.paflag == 1:
                    pacount = 0
                    stop_playback(L(30376), L(30377))
                elif player.paflag == 0:
                    pacount = 0
            except Exception as e:
                log('Autostop pause check error: %s' % e, xbmc.LOGINFO)

        plcount = play_count(plcount, padjust, player.plflag, player.paflag, asevlog)
        sleep_notify(plcount, plstoptime, player.plflag, plnotify, plextend, asevlog, player.paflag)

        if plcount % 10 == 0:
            try:
                plstoptime = int(_get('autostop_plstop', '0') or '0')
                padjust = _get('autostop_padjust', 'None')
                plnotify = int(_get('autostop_plnotify', '0') or '0')
                plextend = int(_get('autostop_plextend', '10') or '10')
                extime = float(_get('autostop_extime', '0') or '0')
                totalstoptime = plstoptime + extime
                if plstoptime > 0 and plcount >= totalstoptime * 60 and (
                    player.plflag > 0 or (player.plflag == 0 and player.paflag == 1)
                ):
                    plcount = 0
                    stop_playback(L(30372), L(30378))
                if plstoptime == 0:
                    plcount = 0
            except Exception as e:
                log('Autostop play stop check error: %s' % e, xbmc.LOGINFO)

        if monitor.waitForAbort(1):
            break

    log('Autostop service loop stopped.', xbmc.LOGINFO)
