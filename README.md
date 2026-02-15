# Auto FTP Sync Plus

**[English](#english)** | **[Deutsch](#deutsch)**

---

<a name="english"></a>
## English

Kodi addon to sync favourites and addon_data via FTP, SFTP or SMB, with optional image rotation, backup/restore and auto-clean. Includes the **Arctic Zephyr – Doku-Kanal** skin, aligned with the addon.

### Features

- **Sync:** Favourites (favourites.xml) and optional addon_data (as ZIP) with a server
- **Protocols:** FTP, SFTP (xbmcvfs), SMB (xbmcvfs)
- **Connection profiles:** Up to 3 profiles (e.g. Home/Office/NAS); active profile in **Settings → Connection**
- **First-run wizard:** Guided setup on first start
- **Image sources:** URL list, local folder or network path (SMB/NFS) for background rotation
- **Backup/Restore:** Userdata as ZIP (local or from URL); option to include addon_data in Settings; Backup and Restore in addon menu under **Maintenance**
- **Auto-Clean:** Cache, packages, thumbnails, logs on a schedule
- **Repository:** Install and update via the Doku-Kanal repository (GitHub)

### Requirements

- **Kodi 21** (Omega) or newer
- Static favourite folders (Anime, Horror, …) are managed by the addon; no external addon required. Location: `addon_data/plugin.program.auto.ftp.sync/Static Favourites/`
- For SFTP: Kodi with vfs.sftp support (or addon)
- Other addons’ data (e.g. Shortlist) in addon_data is synced when “sync addon_data” is enabled

### Installation (Kodi standard)

1. **Install repo addon**  
   Download `repository.dokukanal-1.0.0.zip` from [Releases](https://github.com/benjarogit/Auto-FTP-Sync-Plus-2026/releases) or from `repo/output/` and install in Kodi via **Add-ons → Add-on browser → Install from zip file**.

2. **Unknown sources**  
   In Kodi: **Settings → Add-ons → Unknown sources** allow (if not already).

3. **Install addons from repo**  
   **Add-ons → Add-on browser → Install from repository** → choose repository **Doku-Kanal** → install **Auto FTP Sync** and optionally the skin **Arctic Zephyr – Doku-Kanal**.

4. **Updates**  
   Once the repo addon is installed, Kodi checks for updates; repo URLs point to this GitHub repository.

### Repo URLs (GitHub)

- **addons.xml:** `https://raw.githubusercontent.com/benjarogit/Auto-FTP-Sync-Plus-2026/main/repo/output/addons.xml`
- **addons.xml.md5:** `https://raw.githubusercontent.com/benjarogit/Auto-FTP-Sync-Plus-2026/main/repo/output/addons.xml.md5`
- **ZIP downloads:** `https://raw.githubusercontent.com/benjarogit/Auto-FTP-Sync-Plus-2026/main/repo/output/`

### Project structure

- **addons/** – Plugin and skin source code (`plugin.program.auto.ftp.sync`, `skin.arctic.zephyr.doku`)
- **repo/** – Build script and repo addon (`build_repo.py`, `repository.dokukanal/`, `output/`)
- **CHANGELOG.md** – Version history
- **README.md** – This file

Addon sources for build and GitHub are in `addons/`. For local Kodi testing, copy contents of `addons/plugin.program.auto.ftp.sync` (and optionally the skin) to `.kodi/addons/`.

### Build (for developers)

From the repo root (where `addons/` and `repo/` are):

```bash
python3 repo/build_repo.py
```

Output is in `repo/output/`. Commit that folder after a release so Kodi can fetch new versions from GitHub.

### Versioning

[Semantic Versioning 2.0.0](https://semver.org/) (MAJOR.MINOR.PATCH). First release: **1.0.0**.

### License / Credits

- **Auto FTP Sync:** Doku-Kanal
- **Skin Arctic Zephyr – Doku-Kanal:** Based on Arctic Zephyr (jurialmunkey, beatmasterrs). See skin addon for license.

---

<a name="deutsch"></a>
## Deutsch

Kodi-Addon zum automatischen Synchronisieren von Favoriten und addon_data über FTP, SFTP oder SMB – inkl. optionaler Bildrotation, Backup/Restore und Auto-Clean. Dazu der Skin **Arctic Zephyr – Doku-Kanal**, auf die Nutzung mit dem Addon abgestimmt.

### Features

- **Sync:** Favoriten (favourites.xml) und optional addon_data (als ZIP) mit einem Server
- **Protokolle:** FTP, SFTP (xbmcvfs), SMB (xbmcvfs)
- **Verbindungsprofile:** Bis zu 3 Profile (z. B. Zuhause/Büro/NAS); aktives Profil in **Einstellungen → Verbindung**
- **Ersteinrichtungs-Assistent:** Geführter Dialog beim ersten Start
- **Bildquellen:** URL-Liste, lokaler Ordner oder Netzwerkpfad (SMB/NFS) für Hintergrundrotation
- **Backup/Restore:** Userdata als ZIP (lokal oder von URL); Option „addon_data einbeziehen“ in den Einstellungen; Backup und Wiederherstellung im Addon-Menü unter **Wartung**
- **Auto-Clean:** Cache, Packages, Thumbnails, Logs nach Zeitplan
- **Repository:** Installation und Updates über das Doku-Kanal-Repository (GitHub)

### Voraussetzungen

- **Kodi 21** (Omega) oder neuer
- Statische Favoritenordner (Anime, Horror, …) werden vom Addon verwaltet; kein externes Addon nötig. Speicherort: `addon_data/plugin.program.auto.ftp.sync/Static Favourites/`
- Für SFTP: Kodi mit vfs.sftp-Unterstützung (bzw. Addon)
- Daten anderer Addons (z. B. Shortlist) im addon_data werden mit synchronisiert, wenn die Option „addon_data synchronisieren“ aktiviert ist

### Installation (Kodi-Standard)

1. **Repo-Addon installieren**  
   `repository.dokukanal-1.0.0.zip` von den [Releases](https://github.com/benjarogit/Auto-FTP-Sync-Plus-2026/releases) oder aus `repo/output/` laden und in Kodi unter **Add-ons → Addon-Browser → Von ZIP-Datei installieren** installieren.

2. **Unbekannte Quellen**  
   In Kodi: **Einstellungen → Add-ons → Unbekannte Quellen** erlauben (falls noch nicht geschehen).

3. **Addons aus dem Repo**  
   **Add-ons → Addon-Browser → Addons aus Repository installieren** → Repository **Doku-Kanal** wählen → **Auto FTP Sync** und ggf. Skin **Arctic Zephyr – Doku-Kanal** installieren.

4. **Updates**  
   Sobald das Repo-Addon installiert ist, prüft Kodi auf Updates; die Repo-URLs zeigen auf dieses GitHub-Repository.

### Repo-URLs (GitHub)

- **addons.xml:** `https://raw.githubusercontent.com/benjarogit/Auto-FTP-Sync-Plus-2026/main/repo/output/addons.xml`
- **addons.xml.md5:** `https://raw.githubusercontent.com/benjarogit/Auto-FTP-Sync-Plus-2026/main/repo/output/addons.xml.md5`
- **ZIP-Downloads:** `https://raw.githubusercontent.com/benjarogit/Auto-FTP-Sync-Plus-2026/main/repo/output/`

### Projektstruktur

- **addons/** – Quellcode von Plugin und Skin (`plugin.program.auto.ftp.sync`, `skin.arctic.zephyr.doku`)
- **repo/** – Build-Skript und Repo-Addon (`build_repo.py`, `repository.dokukanal/`, `output/`)
- **CHANGELOG.md** – Versionshistorie
- **README.md** – diese Datei

Die Addon-Quellen für Build und GitHub liegen in `addons/`. Für lokale Kodi-Tests kannst du die Inhalte von `addons/plugin.program.auto.ftp.sync` und ggf. den Skin nach `.kodi/addons/` kopieren.

### Build (für Entwickler)

Aus dem Repo-Root (dort, wo `addons/` und `repo/` liegen):

```bash
python3 repo/build_repo.py
```

Die Ausgabe liegt in `repo/output/`. Nach einem Release diesen Ordner committen, damit Kodi die neuen Versionen von GitHub laden kann.

### Versionierung

[Semantic Versioning 2.0.0](https://semver.org/) (MAJOR.MINOR.PATCH). Erstes Release: **1.0.0**.

### Lizenz / Credits

- **Auto FTP Sync:** Doku-Kanal
- **Skin Arctic Zephyr – Doku-Kanal:** Basiert auf Arctic Zephyr (jurialmunkey, beatmasterrs). Lizenz siehe Skin-Addon.
