#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build Kodi repository: ZIPs und addons.xml aus dem Kodi-Addons-Ordner.
Quelle: KODI_ADDONS (Default: $HOME/.kodi/addons)
Ausgabe: dist/<addon_id>/<addon_id>-<version>.zip, addons.xml, addons.xml.md5, index.html
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
        content = f.read()
    # Match version in root <addon ...> tag, not in <?xml version="1.0" or <import version=
    m = re.search(r'<addon\s[^>]*version="([^"]+)"', content)
    return m.group(1) if m else None


def should_exclude(name):
    if name in EXCLUDE:
        return True
    if name.endswith(".pyc") or "__pycache__" in name:
        return True
    return False


def zip_addon(source_dir, zip_path, addon_id):
    """ZIP mit Addon-Inhalt – Dateien in addon_id/. Kodi braucht genau EINEN Ordner im Root
    (AddonInstaller.cpp: items.Size()==1 und items[0]->IsFolder()), daher zuerst Ordner-Eintrag."""
    os.makedirs(os.path.dirname(zip_path), exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("%s/" % addon_id, "")
        for root, dirs, files in os.walk(source_dir):
            dirs[:] = [d for d in dirs if not should_exclude(d)]
            for f in files:
                if should_exclude(f):
                    continue
                path = os.path.join(root, f)
                rel = os.path.relpath(path, source_dir)
                arcname = "%s/%s" % (addon_id, rel)
                zf.write(path, arcname)


def read_addon_xml(addon_dir):
    path = os.path.join(addon_dir, "addon.xml")
    if not os.path.isfile(path):
        return None
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read().strip()
    # XML-Deklaration entfernen (nur eine am Anfang von addons.xml erlaubt)
    if content.startswith("<?xml"):
        end = content.find("?>") + 2
        content = content[end:].lstrip()
    return content


def main():
    kodi_addons = get_kodi_addons_path()
    output_base = os.path.join(REPO_ROOT, "dist")
    os.makedirs(output_base, exist_ok=True)

    if not os.path.isdir(kodi_addons):
        print("Fehler: Kodi-Addons-Ordner nicht gefunden:", kodi_addons)
        print("Setze KODI_ADDONS auf den Pfad zu deiner Kodi addons/ (z. B. ~/.kodi/addons).")
        return 1

    addon_xmls = []
    repo_version = None
    for addon_id in ADDON_IDS:
        src = os.path.join(kodi_addons, addon_id)
        if not os.path.isdir(src):
            print("Hinweis: Übersprungen (nicht gefunden):", addon_id)
            continue
        version = get_version_from_addon_xml(src)
        if not version:
            print("Hinweis: Keine Version in addon.xml:", addon_id)
            continue
        if addon_id == "repository.dokukanal":
            repo_version = version
        out_dir = os.path.join(output_base, addon_id)
        zip_name = f"{addon_id}-{version}.zip"
        zip_path = os.path.join(out_dir, zip_name)
        zip_addon(src, zip_path, addon_id)
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

    if repo_version:
        index_path = os.path.join(REPO_ROOT, "index.html")
        zip_filename = f"repository.dokukanal-{repo_version}.zip"
        index_content = f'''<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>Doku-Kanal Repository</title></head>
<body>
<p><a href="dist/repository.dokukanal/{zip_filename}">{zip_filename}</a></p>
</body>
</html>
'''
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(index_content)
        print("Erstellt:", index_path)
    return 0


if __name__ == "__main__":
    exit(main())
