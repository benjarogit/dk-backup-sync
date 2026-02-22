# Auto FTP Sync Plus

**[English](#english)** | **[Deutsch](#deutsch)**

---

<a name="english"></a>
## English

**Auto FTP Sync Plus** is a Kodi addon that keeps your favourites and addon data in sync across devices (FTP, SFTP, SMB), runs backups and restores, rotates menu backgrounds from URLs or network paths, and cleans cache and thumbnails on a schedule. It is used together with the **Doku-Kanal (Skin)** skin, which is offered in the same repository.

### Features

| Area | Description |
|------|-------------|
| **Sync** | Syncs your favourites (`favourites.xml`) and, optionally, addon_data (packed as ZIP) with a remote server. Choose what to sync in the addon settings. |
| **Protocols** | FTP, SFTP (Kodi xbmcvfs), and SMB. No extra addons needed for SFTP/SMB on supported Kodi builds. |
| **Connection profiles** | Up to 3 saved profiles (e.g. Home, Office, NAS). The **active profile** is selected under **Settings → Connection**. |
| **First-run wizard** | Guides you through enabling sync, main system, connection type, host, credentials and folder. Run again from the addon menu: “Run first-time setup again”. |
| **Image sources** | Menu background images rotate from URLs, a local folder, or a network path (SMB/NFS). **Settings → Images**. |
| **Backup / Restore** | **Maintenance → Backup** creates a full userdata ZIP (local or URL); you can include **addon_data**. **Maintenance → Restore** lets you restore from a local file or URL (with validation); optionally clear userdata before restore. |
| **Auto-Clean** | Deletes cache, packages, thumbnails and logs on a schedule. Configure interval in addon settings. |
| **Repository** | Install and update the addon and skin from the **Doku-Kanal** repository (GitHub). One-time repo ZIP install, then all updates via Kodi’s repository. |

#### Plugin menu and settings

- **Doku-Kanal shortcut:** In the skin, a shortcut (e.g. under Programs) opens the plugin window directly (no addon-info crash). Description and icon (dksync.png) can be set in skin settings.
- **Settings:** Clear labels for Sync, Add-on data, and Favourite folders; categories and an “Open plugin” button; optional “Show instructions” per section. Open the plugin from **Add-on settings** to see the full menu and instructions.
- **Instructions:** Available in the plugin menu and per settings section. System-wide background image support.

#### Skin (Doku-Kanal)

- **Font:** Geist. **DialogTextViewer** and addon settings dialogs styled (border radius, highlight colour).
- **GlobalFanart:** Uses the same background source as the home slideshow (`home.slideshowpath`).

### Requirements

- **Kodi 21** (Omega) or newer
- Static favourite folders (Anime, Horror, …) are managed by the addon; no external addon required. Location: `addon_data/plugin.program.dokukanal.buildsync/Static Favourites/`
- For SFTP: Kodi with vfs.sftp support (or addon)
- Other addons’ data (e.g. Shortlist) in addon_data is synced when “sync addon_data” is enabled

### Installation (Kodi standard)

Installation order: (1) install the repo addon from ZIP once, (2) enable unknown sources if required, (3) install the addon (and optionally the skin) from the repo. After that, updates are delivered through the repo.

**Where to download:** Use the [Releases](https://github.com/benjarogit/Auto-FTP-Sync-Plus-2026/releases) page. Under **Assets** you will find the ready-to-use Kodi ZIPs (repository, plugin, skin). Do **not** use “Source code (zip)” – that is the full development source; use the files listed under **Assets** instead.

1. **Install the repo addon (one-time)**  
   On the [Releases](https://github.com/benjarogit/Auto-FTP-Sync-Plus-2026/releases) page, open the latest release and under **Assets** download the repository ZIP (e.g. **repository.dokukanal-1.0.zip**). In Kodi go to **Add-ons** → **Add-on browser** → **Install from zip file** and select that ZIP. This installs the Doku-Kanal repository; all future updates come from the repo.

2. **Unknown sources**  
   If Kodi asks to allow unknown sources, go to **Settings** → **Add-ons** → **Unknown sources** and enable it. This is only needed for the first install from ZIP.

3. **Install addon and skin from the repo**  
   **Add-ons** → **Add-on browser** → **Install from repository** → select **Doku-Kanal** → install **Doku-Kanal (Build and Sync)**. Optionally install the skin **Doku-Kanal (Skin)** from the same repository. Alternatively, install from ZIP using the plugin and skin ZIPs under **Assets** (e.g. **plugin.program.dokukanal.buildsync-*.zip**, **skin.dokukanal-*.zip**).

4. **Updates**  
   Once the repo is installed, Kodi will check for updates automatically. The repo points to this GitHub repository; you get new addon and skin versions through **Add-ons** → **My add-ons** → **Check for updates** or when Kodi updates on its own.

### Repo URLs (GitHub)

- **addons.xml:** `https://raw.githubusercontent.com/benjarogit/Auto-FTP-Sync-Plus-2026/main/repo/output/addons.xml`
- **addons.xml.md5:** `https://raw.githubusercontent.com/benjarogit/Auto-FTP-Sync-Plus-2026/main/repo/output/addons.xml.md5`
- **ZIP downloads:** `https://raw.githubusercontent.com/benjarogit/Auto-FTP-Sync-Plus-2026/main/repo/output/`

### Versioning

[Semantic Versioning 2.0.0](https://semver.org/) (MAJOR.MINOR.PATCH). First release: **1.0.0**.

### License / Credits

- **Doku-Kanal (Build and Sync):** Doku-Kanal
- **Doku-Kanal (Skin):** Based on Arctic Zephyr (jurialmunkey, beatmasterrs). See skin addon for license.

---

<a name="deutsch"></a>
## Deutsch

**Auto FTP Sync Plus** ist ein Kodi-Addon, das Favoriten und Addon-Daten zwischen Geräten synchron hält (FTP, SFTP, SMB), Backups erstellt und wiederherstellt, Menü-Hintergründe aus URLs oder Netzwerkpfaden rotieren lässt und Cache sowie Thumbnails nach Zeitplan aufräumt. Es wird zusammen mit dem Skin **Doku-Kanal (Skin)** genutzt, der im gleichen Repository angeboten wird.

### Features

| Bereich | Beschreibung |
|--------|--------------|
| **Sync** | Synchronisiert Favoriten (`favourites.xml`) und optional addon_data (als ZIP) mit einem Server. Was synchronisiert wird, stellst du in den Addon-Einstellungen ein. |
| **Protokolle** | FTP, SFTP (Kodi xbmcvfs) und SMB. Für SFTP/SMB sind auf unterstützten Kodi-Versionen keine Zusatz-Addons nötig. |
| **Verbindungsprofile** | Bis zu 3 gespeicherte Profile (z. B. Zuhause, Büro, NAS). Das **aktive Profil** wählst du unter **Einstellungen → Verbindung**. |
| **Ersteinrichtungs-Assistent** | Führt durch Aktivierung des Syncs, Hauptsystem, Verbindungstyp, Host, Zugangsdaten und Ordner. Im Addon-Menü: „Ersteinrichtung erneut ausführen“. |
| **Bildquellen** | Menü-Hintergrundbilder aus URL-Liste, lokalem Ordner oder Netzwerkpfad (SMB/NFS). **Einstellungen → Bilder**. |
| **Backup / Wiederherstellung** | **Wartung → Backup** erstellt ein Userdata-ZIP (lokal oder URL); **addon_data** optional. **Wartung → Wiederherstellung**: von lokaler Datei oder URL (mit Validierung); optional userdata vorher bereinigen. |
| **Auto-Clean** | Löscht Cache, Packages, Thumbnails und Logs nach Zeitplan. Intervall in den Addon-Einstellungen. |
| **Repository** | Addon und Skin aus dem **Doku-Kanal**-Repository (GitHub) installieren und aktualisieren. Repo-ZIP einmal installieren, danach alle Updates über das Repository. |

#### Plugin-Menü und Einstellungen

- **Doku-Kanal-Shortcut:** Im Skin öffnet ein Shortcut (z. B. unter Programme) direkt das Plugin-Fenster (kein Addon-Info-Crash). Beschreibung und Icon (dksync.png) in den Skin-Einstellungen.
- **Einstellungen:** Klare Labels für Sync, Add-on-Daten und Favoriten-Ordner; Kategorien und Button „Plugin öffnen“; optional „Anleitung anzeigen“ pro Bereich. Plugin unter **Addon-Einstellungen** öffnen für volles Menü und Anleitungen.
- **Anleitungen:** Im Plugin-Menü und pro Einstellungsbereich. Hintergrundbild systemweit.

#### Skin (Doku-Kanal)

- **Schrift:** Geist. **DialogTextViewer** und Addon-Einstellungsdialoge mit Rahmen (Border-Radius, Highlight-Farbe).
- **GlobalFanart:** Nutzt dieselbe Quelle wie der Home-Slideshow (`home.slideshowpath`).

### Voraussetzungen

- **Kodi 21** (Omega) oder neuer
- Statische Favoritenordner (Anime, Horror, …) werden vom Addon verwaltet; kein externes Addon nötig. Speicherort: `addon_data/plugin.program.dokukanal.buildsync/Static Favourites/`
- Für SFTP: Kodi mit vfs.sftp-Unterstützung (bzw. Addon)
- Daten anderer Addons (z. B. Shortlist) im addon_data werden mit synchronisiert, wenn die Option „addon_data synchronisieren“ aktiviert ist

### Installation (Kodi-Standard)

Reihenfolge: (1) Repo-Addon einmal per ZIP installieren, (2) bei Bedarf „Unbekannte Quellen“ erlauben, (3) Addon (und optional Skin) aus dem Repo installieren. Danach kommen Updates über das Repo.

**Wo herunterladen:** Auf der Seite [Releases](https://github.com/benjarogit/Auto-FTP-Sync-Plus-2026/releases) findest du unter **Assets** die fertigen Kodi-ZIPs (Repository, Plugin, Skin). **Nicht** „Source code (zip)“ verwenden – das ist der komplette Quellcode; nutze die Dateien unter **Assets**.

1. **Repo-Addon einmalig installieren**  
   Auf der Seite [Releases](https://github.com/benjarogit/Auto-FTP-Sync-Plus-2026/releases) das neueste Release öffnen und unter **Assets** **repository.dokukanal-1.0.0.zip** herunterladen. In Kodi **Add-ons** → **Addon-Browser** → **Von ZIP-Datei installieren** wählen und diese ZIP auswählen. Damit ist das Doku-Kanal-Repository installiert; alle weiteren Updates kommen über das Repo.

2. **Unbekannte Quellen**  
   Falls Kodi danach fragt: **Einstellungen** → **Add-ons** → **Unbekannte Quellen** erlauben. Nur für die erste Installation von einer ZIP nötig.

3. **Addon und Skin aus dem Repo installieren**  
   **Add-ons** → **Addon-Browser** → **Addons aus Repository installieren** → **Doku-Kanal** wählen → **Doku-Kanal (Build and Sync)** installieren. Optional den Skin **Doku-Kanal (Skin)** aus demselben Repository installieren. Alternativ Addon und Skin per ZIP aus den **Assets** installieren (z. B. **plugin.program.dokukanal.buildsync-*.zip**, **skin.dokukanal-*.zip**).

4. **Updates**  
   Sobald das Repo installiert ist, prüft Kodi automatisch auf Updates. Das Repo zeigt auf dieses GitHub-Repository; neue Addon- und Skin-Versionen erhältst du über **Add-ons** → **Meine Add-ons** → **Auf Updates prüfen** oder durch die automatische Update-Prüfung von Kodi.

### Repo-URLs (GitHub)

- **addons.xml:** `https://raw.githubusercontent.com/benjarogit/Auto-FTP-Sync-Plus-2026/main/repo/output/addons.xml`
- **addons.xml.md5:** `https://raw.githubusercontent.com/benjarogit/Auto-FTP-Sync-Plus-2026/main/repo/output/addons.xml.md5`
- **ZIP-Downloads:** `https://raw.githubusercontent.com/benjarogit/Auto-FTP-Sync-Plus-2026/main/repo/output/`

### Versionierung

[Semantic Versioning 2.0.0](https://semver.org/) (MAJOR.MINOR.PATCH). Erstes Release: **1.0.0**.

### Lizenz / Credits

- **Doku-Kanal (Build and Sync):** Doku-Kanal
- **Doku-Kanal (Skin):** Basiert auf Arctic Zephyr (jurialmunkey, beatmasterrs). Lizenz siehe Skin-Addon.
