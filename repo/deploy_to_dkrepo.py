#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Einfaches Deploy-Skript für dkrepo.sunnyc.de.

Liest die fertigen Dateien aus dist/ und lädt sie per FTP nach /kodi/dk-repo hoch.
FTP-Zugangsdaten kommen **nur** aus Umgebungsvariablen – nichts wird ins Repo
oder nach GitHub committed.

Benötigte Umgebungsvariablen (z. B. in der Shell exportieren):

    export DKREPO_FTP_HOST="w01d3ed0.kasserver.com"
    export DKREPO_FTP_PORT="21"              # optional, Default 21
    export DKREPO_FTP_USER="dein_user"
    export DKREPO_FTP_PASS="dein_passwort"
    export DKREPO_FTP_BASEDIR="/dk-repo"

Aufruf:

    python3 repo/deploy_to_dkrepo.py

Danach liegen addons.xml, addons.xml.md5 und die ZIPs aus dist/ unter
DKREPO_FTP_BASEDIR auf dem Server.
"""

import ftplib
import os
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
DIST_DIR = REPO_ROOT / "dist"


def getenv_required(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise SystemExit(f"Umgebungsvariable {name} ist nicht gesetzt.")
    return value


def iter_dist_files() -> Iterable[Path]:
    """
    Alle Dateien in dist/ (rekursiv) liefern.
    """
    if not DIST_DIR.is_dir():
        raise SystemExit(f"dist-Verzeichnis nicht gefunden: {DIST_DIR}")
    for path in DIST_DIR.rglob("*"):
        if path.is_file():
            yield path


def ensure_remote_dirs(ftp: ftplib.FTP, remote_path: str) -> None:
    """
    Stellt sicher, dass alle Verzeichnisse für remote_path existieren.
    remote_path ist ein Pfad mit /, z. B. 'plugin.program.dokukanal.buildsync/file.zip'.
    """
    parts = remote_path.split("/")[:-1]  # alle Verzeichnisse, letzte Komponente ist Datei
    for part in parts:
        if not part:
            continue
        try:
            ftp.mkd(part)
        except ftplib.error_perm as e:
            # 550 "File exists" ignorieren, alles andere weiterreichen
            if not str(e).startswith("550"):
                raise
        ftp.cwd(part)
    # Danach wieder zum Basisverzeichnis zurück – wird vom Aufrufer gesetzt.


def deploy() -> None:
    host = getenv_required("DKREPO_FTP_HOST")
    port = int(os.environ.get("DKREPO_FTP_PORT") or "21")
    user = getenv_required("DKREPO_FTP_USER")
    password = getenv_required("DKREPO_FTP_PASS")
    basedir = getenv_required("DKREPO_FTP_BASEDIR").rstrip("/")

    print(f"Verbinde zu {host}:{port} als {user} …")
    with ftplib.FTP() as ftp:
        ftp.connect(host, port)
        ftp.login(user, password)
        ftp.cwd(basedir or "/")

        for local_path in iter_dist_files():
            rel = local_path.relative_to(DIST_DIR).as_posix()
            # Für jede Datei vom Basisverzeichnis aus arbeiten
            ftp.cwd(basedir or "/")
            # Verzeichnisse anlegen und in letztes Verzeichnis wechseln
            ensure_remote_dirs(ftp, rel)
            filename = rel.split("/")[-1]
            print(f"Upload: {rel}")
            with local_path.open("rb") as f:
                ftp.storbinary(f"STOR {filename}", f)

    print("Deploy nach dkrepo.sunnyc.de abgeschlossen.")


if __name__ == "__main__":
    deploy()

