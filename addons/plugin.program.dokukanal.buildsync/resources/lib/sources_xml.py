# -*- coding: utf-8 -*-
"""
Erweitert sources.xml um die Quelle „Doku-Kanal“ (GitHub Repo).
Nur erweitern, niemals ersetzen. Bestehende Quellen bleiben unverändert.
"""
import xml.etree.ElementTree as ET
import xbmcvfs

DOKU_KANAL_SOURCE_NAME = "Doku-Kanal"
DOKU_KANAL_SOURCE_URL = "https://github.com/benjarogit/Auto-FTP-Sync-Plus-2026/tree/main/repo/output"


def ensure_doku_kanal_source():
    """
    Liest special://profile/sources.xml, fügt unter <files> eine Quelle
    „Doku-Kanal“ hinzu (falls noch nicht vorhanden), und speichert die Datei.
    Returns: (success: bool, message: str)
    """
    try:
        path = xbmcvfs.translatePath("special://profile/sources.xml")
    except Exception:
        return False, "special://profile not resolved"
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        return False, str(e)
    try:
        root = ET.fromstring(content)
    except ET.ParseError as e:
        return False, "Parse error: %s" % e
    files = root.find("files")
    if files is None:
        files = ET.SubElement(root, "files")
    for src in files.findall("source"):
        name_el = src.find("name")
        if name_el is not None and (name_el.text or "").strip() == DOKU_KANAL_SOURCE_NAME:
            return True, "already present"
    source = ET.SubElement(files, "source")
    name_el = ET.SubElement(source, "name")
    name_el.text = DOKU_KANAL_SOURCE_NAME
    path_el = ET.SubElement(source, "path")
    path_el.set("pathversion", "1")
    path_el.text = DOKU_KANAL_SOURCE_URL
    try:
        tree = ET.ElementTree(root)
        tree.write(path, encoding="utf-8", xml_declaration=True, default_namespace=None, method="xml")
    except Exception as e:
        return False, str(e)
    return True, "added"
