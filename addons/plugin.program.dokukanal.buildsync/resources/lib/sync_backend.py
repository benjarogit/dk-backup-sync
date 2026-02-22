# -*- coding: utf-8 -*-
"""
Sync backends: FTP, SFTP (via xbmcvfs if vfs.sftp present), SMB (via xbmcvfs).
Each backend provides: upload, download, folder_exists(remote_path), ensure_folder(remote_path).
"""
import ftplib
from urllib.parse import quote
import xbmc
import xbmcvfs

from resources.lib.common import log


def _norm_ftp_path(path):
    """Ensure path starts with / for FTP."""
    path = path.replace('\\', '/')
    return path if path.startswith('/') else '/' + path


class FTPBackend:
    """FTP backend using ftplib."""
    def __init__(self, host, user, password, base_path):
        self.host = host
        self.user = user
        self.password = password
        self.base_path = _norm_ftp_path(base_path.rstrip('/'))

    def _remote(self, path):
        p = path.replace('\\', '/')
        return p if p.startswith('/') else self.base_path + '/' + p.lstrip('/')

    def upload(self, local_path, remote_path):
        try:
            remote = self._remote(remote_path)
            with ftplib.FTP(self.host) as ftp:
                ftp.login(self.user, self.password)
                with open(local_path, 'rb') as f:
                    ftp.storbinary('STOR ' + remote, f)
            return True
        except Exception as e:
            log("FTP upload failed: %s" % e, xbmc.LOGERROR)
            return False

    def download(self, remote_path, local_path):
        try:
            remote = self._remote(remote_path)
            with ftplib.FTP(self.host) as ftp:
                ftp.login(self.user, self.password)
                with open(local_path, 'wb') as f:
                    ftp.retrbinary('RETR ' + remote, f.write)
            return True
        except Exception as e:
            log("FTP download failed: %s" % e, xbmc.LOGERROR)
            return False

    def folder_exists(self, remote_path):
        try:
            remote = self._remote(remote_path)
            with ftplib.FTP(self.host) as ftp:
                ftp.login(self.user, self.password)
                ftp.cwd(remote)
            return True
        except ftplib.error_perm as e:
            if '550' in str(e):
                return False
            log("FTP error: %s" % e, xbmc.LOGERROR)
            return False
        except Exception as e:
            log("FTP folder_exists failed: %s" % e, xbmc.LOGERROR)
            return False

    def ensure_folder(self, remote_path):
        """Create folder and parents on FTP; return True if folder exists afterwards."""
        try:
            remote = self._remote(remote_path).strip('/')
            if not remote:
                return self.folder_exists(remote_path)
            segs = [s for s in remote.split('/') if s]
            with ftplib.FTP(self.host) as ftp:
                ftp.login(self.user, self.password)
                for i in range(len(segs)):
                    sub = '/'.join(segs[: i + 1])
                    try:
                        ftp.cwd('/' + sub)
                    except ftplib.error_perm as e:
                        if '550' in str(e):
                            try:
                                ftp.mkd(segs[i])
                            except ftplib.error_perm as mkd_e:
                                log("FTP mkd failed for %s: %s" % (sub, mkd_e), xbmc.LOGERROR)
                                return self.folder_exists(remote_path)
                        else:
                            raise
            return self.folder_exists(remote_path)
        except Exception as e:
            log("FTP ensure_folder failed: %s" % e, xbmc.LOGERROR)
            return self.folder_exists(remote_path)

    def listdir(self, remote_path):
        """List names (files and dirs) in remote_path. Returns [] on error."""
        try:
            remote = self._remote(remote_path)
            with ftplib.FTP(self.host) as ftp:
                ftp.login(self.user, self.password)
                ftp.cwd(remote)
                return ftp.nlst()
        except Exception as e:
            log("FTP listdir failed: %s" % e, xbmc.LOGDEBUG)
            return []


class SFTPBackend:
    """SFTP backend using xbmcvfs (requires vfs.sftp addon). Remote path: absolute path on server."""
    def __init__(self, host, user, password, base_path, port=22):
        self.host = host
        self.port = int(port) if port else 22
        self.user = quote(user or '', safe='')
        self.password = quote(password or '', safe='')
        self._prefix = f"sftp://{self.user}:{self.password}@{host}:{self.port}/"

    def _remote_url(self, remote_path):
        p = (remote_path or '').replace('\\', '/').strip('/')
        return self._prefix + p if p else self._prefix.rstrip('/') + '/'

    def upload(self, local_path, remote_path):
        url = self._remote_url(remote_path)
        try:
            with open(local_path, 'rb') as f:
                data = f.read()
            f = xbmcvfs.File(url, 'wb')
            f.write(data)
            f.close()
            return True
        except Exception as e:
            log("SFTP upload failed: %s" % e, xbmc.LOGERROR)
            return False

    def download(self, remote_path, local_path):
        url = self._remote_url(remote_path)
        try:
            f = xbmcvfs.File(url, 'rb')
            data = f.read()
            f.close()
            with open(local_path, 'wb') as out:
                out.write(data)
            return True
        except Exception as e:
            log("SFTP download failed: %s" % e, xbmc.LOGERROR)
            return False

    def folder_exists(self, remote_path):
        try:
            url = self._remote_url(remote_path)
            if not url.endswith('/'):
                url += '/'
            dirs, files = xbmcvfs.listdir(url)
            return True
        except Exception:
            return False

    def ensure_folder(self, remote_path):
        """Create folder and parents on SFTP via xbmcvfs.mkdirs; return True if folder exists afterwards."""
        try:
            url = self._remote_url(remote_path)
            if not url.endswith('/'):
                url += '/'
            if xbmcvfs.mkdirs(url):
                return self.folder_exists(remote_path)
        except Exception as e:
            log("SFTP ensure_folder failed: %s" % e, xbmc.LOGERROR)
        return self.folder_exists(remote_path)

    def listdir(self, remote_path):
        """List names (files and dirs) in remote_path. Returns [] on error."""
        try:
            url = self._remote_url(remote_path)
            if not url.endswith('/'):
                url += '/'
            dirs, files = xbmcvfs.listdir(url)
            return list(dirs) + list(files)
        except Exception as e:
            log("SFTP listdir failed: %s" % e, xbmc.LOGDEBUG)
            return []


class SMBBackend:
    """SMB backend using xbmcvfs. remote_path = share/path (e.g. myshare/kodi/auto_fav_sync/...)."""
    def __init__(self, host, user, password, base_path):
        self.host = host
        self.user = quote(user or '', safe='')
        self.password = quote(password or '', safe='')
        self._prefix = f"smb://{self.user}:{self.password}@{host}/"

    def _remote_url(self, remote_path):
        p = (remote_path or '').replace('\\', '/').strip('/')
        return self._prefix + p if p else self._prefix.rstrip('/') + '/'

    def upload(self, local_path, remote_path):
        url = self._remote_url(remote_path)
        try:
            with open(local_path, 'rb') as f:
                data = f.read()
            f = xbmcvfs.File(url, 'wb')
            f.write(data)
            f.close()
            return True
        except Exception as e:
            log("SMB upload failed: %s" % e, xbmc.LOGERROR)
            return False

    def download(self, remote_path, local_path):
        url = self._remote_url(remote_path)
        try:
            f = xbmcvfs.File(url, 'rb')
            data = f.read()
            f.close()
            with open(local_path, 'wb') as out:
                out.write(data)
            return True
        except Exception as e:
            log("SMB download failed: %s" % e, xbmc.LOGERROR)
            return False

    def folder_exists(self, remote_path):
        try:
            url = self._remote_url(remote_path)
            if not url.endswith('/'):
                url += '/'
            dirs, files = xbmcvfs.listdir(url)
            return True
        except Exception:
            return False

    def ensure_folder(self, remote_path):
        """Create folder and parents on SMB via xbmcvfs.mkdirs; return True if folder exists afterwards."""
        try:
            url = self._remote_url(remote_path)
            if not url.endswith('/'):
                url += '/'
            if xbmcvfs.mkdirs(url):
                return self.folder_exists(remote_path)
        except Exception as e:
            log("SMB ensure_folder failed: %s" % e, xbmc.LOGERROR)
        return self.folder_exists(remote_path)

    def listdir(self, remote_path):
        """List names (files and dirs) in remote_path. Returns [] on error."""
        try:
            url = self._remote_url(remote_path)
            if not url.endswith('/'):
                url += '/'
            dirs, files = xbmcvfs.listdir(url)
            return list(dirs) + list(files)
        except Exception as e:
            log("SMB listdir failed: %s" % e, xbmc.LOGDEBUG)
            return []


def get_backend(connection_type, host, user, password, base_path, sftp_port='22'):
    """
    Return a sync backend. connection_type: 'ftp', 'sftp', 'smb'.
    """
    ct = (connection_type or 'ftp').strip().lower()
    if ct == 'sftp':
        return SFTPBackend(host, user, password, base_path, port=sftp_port)
    if ct == 'smb':
        return SMBBackend(host, user, password, base_path)
    return FTPBackend(host, user, password, base_path)
