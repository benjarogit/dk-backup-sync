# Doku-Kanal – Build & Sync + Skin

**[English](#english)** · **[Deutsch](#deutsch)**

---

<a name="english"></a>
## English

### Overview

The **Doku-Kanal** project provides a Kodi repository, the **Doku-Kanal (Build and Sync)** plugin, and the **Doku-Kanal (Skin)** for Kodi 21 (Omega) and newer.

| Component | Description |
|-----------|-------------|
| **Repository** | `repository.dokukanal` – Provides plugin and skin. Install once from ZIP, then get updates via Kodi’s Add-on manager. |
| **Plugin** | `plugin.program.dokukanal.buildsync` – Sync favourites and addon_data (FTP/SFTP/SMB), backup/restore, image rotation, AutoClean, Autostop. |
| **Skin** | `skin.dokukanal` – Arctic Zephyr–based skin, optimized for the plugin. |

---

### Plugin: Doku-Kanal (Build and Sync)

Synchronizes favourites and addon_data between devices, runs backups, rotates menu backgrounds, and cleans cache/thumbnails on a schedule. **No external addons required** – no Super Favourites, no xstream, no inputstreamhelper.

#### Features

| Area | Description |
|------|-------------|
| **Sync** | Syncs `favourites.xml` and optionally addon_data (ZIP) with a remote server. Configure what to sync in addon settings. |
| **Protocols** | **FTP**, **SFTP** (Kodi xbmcvfs), **SMB**. No extra addons for SFTP/SMB on supported Kodi builds. |
| **Connection profiles** | Up to 3 saved profiles (e.g. Home, Office, NAS). Select active profile under **Settings → Connection**. |
| **Static favourite folders** | Built-in folders (Anime, Horror, etc.) – no Super Favourites. Located in `addon_data/plugin.program.dokukanal.buildsync/Static Favourites/`. Editable in settings. |
| **Sync mode** | Merge (union) or overwrite. Favourites sync interval configurable (5–60 min or off). |
| **First-run wizard** | Guides through sync enable, main system, connection type, host, credentials, folder. Run again from plugin menu: “Run first-time setup again”. |
| **Image rotation** | Menu background from URL list, local folder, network path (SMB/NFS), or Picsum. **Settings → Images**. |
| **Backup** | Full userdata ZIP (local or URL). Optional addon_data. **Maintenance → Backup**. |
| **Restore** | Restore from local file or URL (with validation). Option to wipe cache before restore. **Maintenance → Restore**. |
| **Auto-Clean** | Deletes cache, packages, thumbnails, logs on a schedule. Configure interval in addon settings. |
| **Autostop** | Stop paused playback after X minutes, or sleep timer for playing media. Optional screensaver when stopping. Enable in **Settings → Autostop**. Works with all sources. |
| **Changelog** | View changelog from plugin menu. Shown once after update. |
| **Skin install** | Opens addon browser to install Doku-Kanal (Skin) from the repository. |

#### Plugin menu (Program Add-ons → Doku-Kanal)

- Sync favourites now
- Test connection
- Backup
- Restore
- Test image sources
- Auto-Clean
- Install skin
- Instructions
- Changelog
- Settings

#### Settings categories

- **General** – Enable sync, addon_data sync, main system flag
- **Favourites** – Sync interval, mode (merge/overwrite), static folders, custom folder
- **Connection** – Profile 1–3: host, port, user, password, base path (FTP/SFTP/SMB)
- **Images** – Source (URL list, folder, network path, Picsum), rotation interval
- **Backup** – Storage path (local or network)
- **Auto-Clean** – Enable, frequency, what to clear
- **Autostop** – Enable, pause timeout, sleep timer, screensaver

---

### Skin: Doku-Kanal

Based on **Arctic Zephyr** (jurialmunkey, beatmasterrs). Minimal, clean, elegant. Optimized for the Build and Sync plugin.

- **Font:** Geist
- **GlobalFanart:** Same source as home slideshow (`home.slideshowpath`)
- **Doku-Kanal shortcut:** Skin shortcut opens plugin directly (no addon-info crash). Icon and label configurable in skin settings.
- **Menu structure:** Wartung (Maintenance), Backup, Einstellungen (Settings) aligned with plugin.

**Requires:** script.skinshortcuts, script.globalsearch, script.image.resource.select, resource.images.weathericons.white, script.embuary.info, script.embuary.helper, plugin.video.themoviedb.helper.

---

### Repository: Doku-Kanal

- **info:** `https://dkrepo.sunnyc.de/addons.xml` (or your repo URL)
- **checksum:** `https://dkrepo.sunnyc.de/addons.xml.md5`
- **datadir:** `https://raw.githubusercontent.com/benjarogit/dk-backup-sync/main/dist/` – Addon ZIPs are served from GitHub.

If you host your own repo server: upload `addons.xml`, `addons.xml.md5`, and `repository.dokukanal/repository.dokukanal-1.0.0.zip` to your web root. For **install from zip** to work when users add the repo URL as source, use the Apache config in `repo/htaccess-for-dkrepo.txt` (no gzip for .zip, `Accept-Ranges: bytes`). Enable directory listing (`Options +Indexes`) so users can browse to the zip.

---

### Installation

**If "Install from zip" does nothing, use this (reliable):**

1. **Get the ZIP locally** – On a PC, download [repository.dokukanal-1.0.0.zip](https://github.com/benjarogit/dk-backup-sync/raw/main/dist/repository.dokukanal/repository.dokukanal-1.0.0.zip) and copy it to a USB stick or a folder Kodi can use as a source (e.g. SMB share, local storage).
2. **In Kodi, add a source** that points to that folder (or USB) – do **not** use an HTTPS/URL as the install source.
3. **Add-ons** → **Add-on browser** → **Install from zip file** → go to that source → select **repository.dokukanal-1.0.0.zip**.
4. Enable **Unknown sources** (Settings → Add-ons) if Kodi asks.
5. Then: **Add-ons** → **Install from repository** → **Doku-Kanal Repository** → install the plugin and optionally the skin.

**Option A – Repository (recommended once the ZIP is installed)**

1. **repository.dokukanal-1.0.0.zip** von [GitHub dist](https://github.com/benjarogit/dk-backup-sync/tree/main/dist/repository.dokukanal) oder [dkrepo.sunnyc.de](https://dkrepo.sunnyc.de/) herunterladen.
2. In Kodi: **Add-ons** → **Addon-Browser** → **Von ZIP-Datei installieren** → ZIP auswählen (am zuverlässigsten von lokaler Quelle/USB/SMB, nicht direkt von HTTPS).
3. **Add-ons** → **Aus Repository installieren** → **Doku-Kanal Repository** → **Doku-Kanal (Build and Sync)** und optional **Doku-Kanal (Skin)** installieren.
4. **Unbekannte Quellen** erlauben, falls nötig (Einstellungen → Add-ons).

**Option B – Direct ZIP**

Download plugin and skin ZIPs from [dist](https://github.com/benjarogit/dk-backup-sync/tree/main/dist) and install via **Install from zip file**. No repository, but no automatic updates.

#### Troubleshooting: Installation fails or nothing happens

If "Install from zip" shows no error but nothing happens, or fails:

- **SSL certificate** – Kodi (e.g. on LibreELEC, Android) may not trust your server’s certificate. Workaround: download the ZIP on a PC from [GitHub](https://raw.githubusercontent.com/benjarogit/dk-backup-sync/main/dist/repository.dokukanal/repository.dokukanal-1.0.0.zip), copy to a USB stick or SMB share, add that path as a source in Kodi, then install from there.
- **Try local file** – Add a source pointing to a folder where you saved the ZIP (e.g. Downloads, USB, SMB). Browse to the file and select it – avoids HTTPS/SSL issues.
- **Kodi log** – Enable debug logging (Settings → System → Logging), reproduce the issue, then check `kodi.log` for the exact error (e.g. `SSL peer certificate`, `Failed to install`).

---

### Requirements

- **Kodi 21** (Omega) or newer
- SFTP: Kodi with vfs.sftp support
- Skin: script.skinshortcuts, script.embuary.helper, plugin.video.themoviedb.helper, etc. (see skin addon)

---

### Links

- **Repository ZIP:** https://raw.githubusercontent.com/benjarogit/dk-backup-sync/main/dist/repository.dokukanal/repository.dokukanal-1.0.0.zip
- **dist/** (all ZIPs): https://github.com/benjarogit/dk-backup-sync/tree/main/dist
- **Changelog:** https://raw.githubusercontent.com/benjarogit/dk-backup-sync/main/changelog.txt

---

### Versioning

[Semantic Versioning 2.0.0](https://semver.org/). Current: **1.0.0**.

---

### Credits

- **Doku-Kanal (Build and Sync):** Doku-Kanal
- **Doku-Kanal (Skin):** Based on Arctic Zephyr (jurialmunkey, beatmasterrs). Creative Commons Non-Commercial 3.0.

---

<a name="deutsch"></a>
## Deutsch

### Übersicht

Das **Doku-Kanal**-Projekt stellt ein Kodi-Repository, das Plugin **Doku-Kanal (Build and Sync)** und den Skin **Doku-Kanal (Skin)** für Kodi 21 (Omega) und neuer bereit.

| Komponente | Beschreibung |
|------------|--------------|
| **Repository** | `repository.dokukanal` – Liefert Plugin und Skin. Einmal per ZIP installieren, danach Updates über den Addon-Manager. |
| **Plugin** | `plugin.program.dokukanal.buildsync` – Favoriten- und addon_data-Sync (FTP/SFTP/SMB), Backup/Wiederherstellung, Bildrotation, AutoClean, Autostop. |
| **Skin** | `skin.dokukanal` – Arctic-Zephyr-basierter Skin, für das Plugin optimiert. |

---

### Plugin: Doku-Kanal (Build and Sync)

Synchronisiert Favoriten und addon_data zwischen Geräten, erstellt Backups, rotiert Menü-Hintergründe und räumt Cache/Thumbnails nach Zeitplan auf. **Keine externen Addons nötig** – kein Super Favourites, kein xstream, kein inputstreamhelper.

#### Funktionen

| Bereich | Beschreibung |
|---------|--------------|
| **Sync** | Synchronisiert `favourites.xml` und optional addon_data (ZIP) mit einem Server. Was synchronisiert wird, stellst du in den Einstellungen ein. |
| **Protokolle** | **FTP**, **SFTP** (Kodi xbmcvfs), **SMB**. Keine Zusatz-Addons für SFTP/SMB auf unterstützten Kodi-Versionen. |
| **Verbindungsprofile** | Bis zu 3 Profile (z. B. Zuhause, Büro, NAS). Aktives Profil unter **Einstellungen → Verbindung** wählen. |
| **Statische Favoritenordner** | Integrierte Ordner (Anime, Horror usw.) – kein Super Favourites. Speicherort: `addon_data/plugin.program.dokukanal.buildsync/Static Favourites/`. In den Einstellungen anpassbar. |
| **Sync-Modus** | Merge (Vereinigung) oder Überschreiben. Favoriten-Sync-Intervall konfigurierbar (5–60 Min oder aus). |
| **Ersteinrichtungs-Assistent** | Führt durch Sync-Aktivierung, Hauptsystem, Verbindungstyp, Host, Zugangsdaten, Ordner. Erneut ausführbar über „Ersteinrichtung erneut ausführen“ im Plugin-Menü. |
| **Bildrotation** | Menü-Hintergrund aus URL-Liste, lokalem Ordner, Netzwerkpfad (SMB/NFS) oder Picsum. **Einstellungen → Bilder**. |
| **Backup** | Vollständiges Userdata-ZIP (lokal oder URL). Optional addon_data. **Wartung → Backup**. |
| **Wiederherstellung** | Von lokaler Datei oder URL (mit Validierung). Option: Cache vorher löschen. **Wartung → Wiederherstellung**. |
| **Auto-Clean** | Löscht Cache, Packages, Thumbnails, Logs nach Zeitplan. Intervall in den Einstellungen. |
| **Autostop** | Pausierte Wiedergabe nach X Minuten stoppen oder Schlaf-Timer für laufende Wiedergabe. Optional Bildschirmsparer beim Stopp. In **Einstellungen → Autostop** aktivierbar. Funktioniert mit allen Quellen. |
| **Changelog** | Changelog im Plugin-Menü. Nach Update einmalig angezeigt. |
| **Skin installieren** | Öffnet Addon-Browser zum Installieren des Doku-Kanal (Skin) aus dem Repository. |

#### Plugin-Menü (Programme → Doku-Kanal)

- Favoriten jetzt synchronisieren
- Verbindung testen
- Backup
- Wiederherstellen
- Bildquellen testen
- Auto-Clean
- Skin installieren
- Anleitungen
- Changelog
- Einstellungen

#### Einstellungsbereiche

- **Allgemein** – Sync aktivieren, addon_data-Sync, Hauptsystem-Flag
- **Favoriten** – Sync-Intervall, Modus (Merge/Überschreiben), statische Ordner, benutzerdefinierter Ordner
- **Verbindung** – Profil 1–3: Host, Port, Benutzer, Passwort, Basispfad (FTP/SFTP/SMB)
- **Bilder** – Quelle (URL-Liste, Ordner, Netzwerkpfad, Picsum), Rotations-Intervall
- **Backup** – Speicherpfad (lokal oder Netzwerk)
- **Auto-Clean** – Aktivieren, Häufigkeit, was gelöscht wird
- **Autostop** – Aktivieren, Pausen-Timeout, Schlaf-Timer, Bildschirmsparer

---

### Skin: Doku-Kanal

Basiert auf **Arctic Zephyr** (jurialmunkey, beatmasterrs). Klar, minimalistisch, elegant. Für das Build-and-Sync-Plugin optimiert.

- **Schrift:** Geist
- **GlobalFanart:** Dieselbe Quelle wie die Home-Slideshow (`home.slideshowpath`)
- **Doku-Kanal-Shortcut:** Skin-Shortcut öffnet das Plugin direkt (kein Addon-Info-Absturz). Icon und Beschriftung in den Skin-Einstellungen änderbar.
- **Menüstruktur:** Wartung, Backup, Einstellungen – abgestimmt auf das Plugin.

**Benötigt:** script.skinshortcuts, script.globalsearch, script.image.resource.select, resource.images.weathericons.white, script.embuary.info, script.embuary.helper, plugin.video.themoviedb.helper.

---

### Repository: Doku-Kanal

- **info:** `https://dkrepo.sunnyc.de/addons.xml` (oder deine Repo-URL)
- **checksum:** `https://dkrepo.sunnyc.de/addons.xml.md5`
- **datadir:** `https://raw.githubusercontent.com/benjarogit/dk-backup-sync/main/dist/` – Addon-ZIPs werden von GitHub bereitgestellt.

Bei eigenem Repo-Server: `addons.xml`, `addons.xml.md5` und `repository.dokukanal/repository.dokukanal-1.0.0.zip` ins Web-Root hochladen. Damit **„Von ZIP installieren“** direkt über die URL funktioniert, Apache-Konfiguration aus `repo/htaccess-for-dkrepo.txt` verwenden (kein gzip für .zip, `Accept-Ranges: bytes`). Verzeichnislisten (`Options +Indexes`) aktivieren, damit Nutzer zur ZIP navigieren können.

---

### Installation

**So klappt die Repository-Installation zuverlässig (wenn „Von ZIP installieren“ sonst nichts macht):**

1. **ZIP lokal haben** – Auf dem PC [repository.dokukanal-1.0.0.zip](https://github.com/benjarogit/dk-backup-sync/raw/main/dist/repository.dokukanal/repository.dokukanal-1.0.0.zip) herunterladen und z.B. auf USB-Stick oder in einen Ordner kopieren, den Kodi als Quelle sehen kann (z.B. SMB-Freigabe, lokaler Speicher).
2. **In Kodi eine Quelle hinzufügen**, die auf diesen Ordner (oder USB) zeigt – **kein** HTTPS, keine Web-URL.
3. **Add-ons** → **Addon-Browser** → **Von ZIP-Datei installieren** → zu dieser Quelle wechseln → **repository.dokukanal-1.0.0.zip** auswählen.
4. **Unbekannte Quellen** erlauben (Einstellungen → Add-ons), falls Kodi danach fragt.
5. Danach: **Add-ons** → **Aus Repository installieren** → **Doku-Kanal Repository** → Plugin und ggf. Skin installieren.

**Option A – Über Repository (empfohlen)**

1. **repository.dokukanal-1.0.0.zip** von [GitHub dist](https://github.com/benjarogit/dk-backup-sync/tree/main/dist/repository.dokukanal) oder [dkrepo.sunnyc.de](https://dkrepo.sunnyc.de/) (falls eingerichtet) herunterladen.
2. In Kodi: **Add-ons** → **Addon-Browser** → **Von ZIP-Datei installieren** → ZIP auswählen.
3. **Add-ons** → **Addons aus Repository installieren** → **Doku-Kanal Repository** → **Doku-Kanal (Build and Sync)** und optional **Doku-Kanal (Skin)** installieren.
4. **Unbekannte Quellen** erlauben, falls erforderlich (Einstellungen → Add-ons).

**Option B – Direkte ZIP-Installation**

Plugin- und Skin-ZIPs aus [dist](https://github.com/benjarogit/dk-backup-sync/tree/main/dist) herunterladen und über **Von ZIP-Datei installieren** einspielen. Kein Repository, aber keine automatischen Updates.

#### Fehlerbehebung: Installation schlägt fehl oder „nichts passiert“

Wenn „Von ZIP-Datei installieren“ keine Fehlermeldung zeigt, aber nichts passiert:

- **Kodi neu starten** – Kodi speichert fehlgeschlagene Installationen. Nach einem Fehlversuch startet es oft erst nach Neustart neu. Kodi vollständig beenden, neu starten, Installation erneut versuchen.
- **Unbekannte Quellen** – Muss erlaubt sein: Einstellungen → Add-ons → Unbekannte Quellen.
- **Kodi 18.2–18.9 Bug** – Bekanntes Problem: ZIP-Installation kann still fehlschlagen. Auf Kodi 18.1 downgraden oder auf Kodi 19+ updaten (wir benötigen Kodi 21).
- **SSL-Zertifikat** – Kodi (z. B. LibreELEC, Android) vertraut dem Server evtl. nicht. **Lösung:** ZIP auf dem PC von [GitHub dist](https://raw.githubusercontent.com/benjarogit/dk-backup-sync/main/dist/repository.dokukanal/repository.dokukanal-1.0.0.zip) oder [dkrepo](https://dkrepo.sunnyc.de/repository.dokukanal/) herunterladen, auf USB oder SMB kopieren, diesen Pfad als Quelle in Kodi hinzufügen, von dort installieren.
- **Lokale Datei** – Quelle auf einen Ordner setzen, in dem die ZIP liegt (z. B. Downloads, USB, SMB). Dann zur Datei navigieren und auswählen – umgeht HTTPS/SSL-Probleme.
- **Kodi-Log** – Debug-Log aktivieren (Einstellungen → System → Protokollierung), Fehler reproduzieren, in `kodi.log` die genaue Meldung prüfen.

---

### Voraussetzungen

- **Kodi 21** (Omega) oder neuer
- SFTP: Kodi mit vfs.sftp-Unterstützung
- Skin: script.skinshortcuts, script.embuary.helper, plugin.video.themoviedb.helper usw. (siehe Skin-Addon)

---

### Links

- **Repository-ZIP:** https://raw.githubusercontent.com/benjarogit/dk-backup-sync/main/dist/repository.dokukanal/repository.dokukanal-1.0.0.zip
- **dist/** (alle ZIPs): https://github.com/benjarogit/dk-backup-sync/tree/main/dist
- **Changelog:** https://raw.githubusercontent.com/benjarogit/dk-backup-sync/main/changelog.txt

---

### Versionierung

[Semantic Versioning 2.0.0](https://semver.org/). Aktuell: **1.0.0**.

---

### Credits

- **Doku-Kanal (Build and Sync):** Doku-Kanal
- **Doku-Kanal (Skin):** Basiert auf Arctic Zephyr (jurialmunkey, beatmasterrs). Creative Commons Non-Commercial 3.0.
