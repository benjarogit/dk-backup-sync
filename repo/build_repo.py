#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build Kodi repository: ZIPs und addons.xml aus dem Kodi-Addons-Ordner.
Quelle: KODI_ADDONS (Default: $HOME/.kodi/addons)
Ausgabe: repo/output/<addon_id>/<addon_id>-<version>.zip, addons.xml, addons.xml.md5
"""
import hashlib
import os
import re
import zipfile

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ADDON_IDS = [
    "plugin.program.dokukanal.buildsync",
    "skin.dokukanal",
    "repository.dokukanal",
]
EXCLUDE = {"__pycache__", ".git", "*.pyc", ".gitignore"}


def get_kodi_addons_path():
    return os.environ.get("KODI_ADDONS") or os.path.join(
        os.path.expanduser("~"), ".kodi", "addons"
    )


def get_version_from_addon_xml(addon_dir):
    addon_xml = os.path.join(addon_dir, "addon.xml")
    if not os.path.isfile(addon_xml):
        return None
    with open(addon_xml, "r", encoding="utf-8", errors="replace") as f:
        m = re.search(r'version="([^"]+)"', f.read())
    return m.group(1) if m else None


def should_exclude(name):
    if name in EXCLUDE:
        return True
    if name.endswith(".pyc") or "__pycache__" in name:
        return True
    return False


def zip_addon(source_dir, zip_path):
    os.makedirs(os.path.dirname(zip_path), exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(source_dir):
            dirs[:] = [d for d in dirs if not should_exclude(d)]
            for f in files:
                if should_exclude(f):
                    continue
                path = os.path.join(root, f)
                arcname = os.path.relpath(path, source_dir)
                zf.write(path, arcname)


def read_addon_xml(addon_dir):
    path = os.path.join(addon_dir, "addon.xml")
    if not os.path.isfile(path):
        return None
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read().strip()


def main():
    kodi_addons = get_kodi_addons_path()
    output_base = os.path.join(REPO_ROOT, "repo", "output")
    os.makedirs(output_base, exist_ok=True)

    if not os.path.isdir(kodi_addons):
        print("Fehler: Kodi-Addons-Ordner nicht gefunden:", kodi_addons)
        print("Setze KODI_ADDONS auf den Pfad zu deiner Kodi addons/ (z. B. ~/.kodi/addons).")
        return 1

    addon_xmls = []
    for addon_id in ADDON_IDS:
        src = os.path.join(kodi_addons, addon_id)
        if not os.path.isdir(src):
            print("Hinweis: Übersprungen (nicht gefunden):", addon_id)
            continue
        version = get_version_from_addon_xml(src)
        if not version:
            print("Hinweis: Keine Version in addon.xml:", addon_id)
            continue
        out_dir = os.path.join(output_base, addon_id)
        zip_name = f"{addon_id}-{version}.zip"
        zip_path = os.path.join(out_dir, zip_name)
        zip_addon(src, zip_path)
        print("Erstellt:", zip_path)
        xml_content = read_addon_xml(src)
        if xml_content:
            addon_xmls.append(xml_content)

    addons_xml_content = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<addons>\n' + "\n".join(addon_xmls) + "\n</addons>\n"
    addons_xml_path = os.path.join(output_base, "addons.xml")
    with open(addons_xml_path, "w", encoding="utf-8") as f:
        f.write(addons_xml_content)
    print("Erstellt:", addons_xml_path)

    md5_path = os.path.join(output_base, "addons.xml.md5")
    with open(md5_path, "w", encoding="utf-8") as f:
        f.write(hashlib.md5(addons_xml_content.encode("utf-8")).hexdigest())
    print("Erstellt:", md5_path)
    return 0


if __name__ == "__main__":
    exit(main())
