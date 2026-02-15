# Entwicklung & Workspace

## Eine Quelle, kein Doppel

**Die einzige Quelle für Plugin, Skin und Repo-Build ist dieses Projekt: Auto-FTP-Sync-Plus (das GitHub-Repo).** Alles, was du entwickelst und was auf GitHub landet, gehört hierher. Es gibt keine zweite „Entwicklungs-Kopie“ – nur diese.

Unter deiner Kodi-Installation („Kodi (lokal)“) siehst du trotzdem Ordner wie `addons/plugin.program.auto.ftp.sync` oder `repo/`. Das ist so:

- **`Kodi (lokal)/addons/plugin.program.auto.ftp.sync`** (und Skin) = **Test-Kopie.** Kodi lädt Addons nur aus seinem eigenen `addons/`-Ordner. Zum Testen kopierst oder verlinkst du dorthin aus dem Projekt – das ist kein zweites Repository, sondern das Laufzeit-Ziel.
- **`Kodi (lokal)/repo/`** = **redundant.** Build-Script und Repo-Inhalt leben nur in **Auto-FTP-Sync-Plus/repo**. Den Ordner **Kodi (lokal)/repo** kannst du ignorieren oder löschen; gebaut wird ausschließlich im Projektordner mit `./gitpush.sh`.

Kurz: **Entwickeln nur hier im Projekt.** Was unter Kodi liegt, ist entweder Test-Ablage (addons) oder überflüssig (repo).

---

## Was du siehst, wenn du die Workspace-Datei öffnest

Das Projekt liegt in **`~/Projekte/Auto-FTP-Sync-Plus`** (nicht mehr unter .kodi). Die Workspace-Datei lädt **zwei Ordner** in die Seitenleiste:

1. **Auto-FTP-Sync-Plus (Quellcode / GitHub)**  
   **`~/Projekte/Auto-FTP-Sync-Plus`** = das **geklonte GitHub-Repo**. Plugin, Skin, Repo-Build – alles. **Hier editierst du.**

2. **Kodi (lokal)**  
   Deine **lokale Kodi-Installation** (addons, userdata, …). Du siehst sie, um Addons zum Testen zu kopieren oder Einstellungen zu prüfen. **Nicht** hier entwickeln – nur zum Testen/Anschauen.

So hast du beides in einem Fenster: Quellcode und Kodi-Installation, ohne doppelten Projektordner.

---

## Was ist was?

### Im Projektordner „Auto-FTP-Sync-Plus“ ( = GitHub)

- **`addons/`** – Quellcode von Plugin und Skin. Wird gebaut und als ZIP ins Repo gepackt.
- **`repo/`** – Build-System für dein Kodi-Repository (`build_repo.py`, Repo-Addon, `output/` mit addons.xml und ZIPs). Das ist **die** Quelle; von GitHub aus beziehen Nutzer dein Repo.
- `README.md`, `CHANGELOG.md`, `gitpush.sh`, `.gitignore` – Projekt-Dateien.

### Unter „Kodi (lokal)“

- **`addons/`** – Hier installiert Kodi Addons. Zum Testen: Inhalt von **Auto-FTP-Sync-Plus/addons/plugin.program.auto.ftp.sync** (und ggf. Skin) hierher kopieren oder verlinken.
- **`repo/`** – Falls vorhanden: Duplikat. Ignorieren oder löschen; gebaut wird nur im Projektordner.

---

## So öffnest du den Workspace

**Datei → Workspace aus Datei öffnen** → **`auto-ftp-sync-plus.code-workspace`** wählen. Die Datei liegt unter **`~/.kodi/`**. Du siehst dann: **Kodi (lokal)** (= deine Kodi-Installation) und **Auto-FTP-Sync-Plus (Quellcode / GitHub)** (= dieses Projekt in **`~/Projekte/Auto-FTP-Sync-Plus`**) in einem Fenster – ohne doppelten Ordner in der Ansicht.

---

## Lokale Kodi-Tests

- Inhalte von **Auto-FTP-Sync-Plus/addons/plugin.program.auto.ftp.sync** nach **Kodi (lokal)/addons/plugin.program.auto.ftp.sync** kopieren (oder dort verlinken).
- Skin ggf. ebenso nach **Kodi (lokal)/addons/skin.arctic.zephyr.doku**.

Änderungen immer **im Projektordner** machen; danach für den Test nach **Kodi (lokal)/addons/** übernehmen.

## Push, Tag, Release

```bash
# Nur committen und pushen
./gitpush.sh "Deine Commit-Nachricht"

# Release inkl. Tag (und bei installierter GitHub-CLI automatisch Release mit EN-Notizen)
./gitpush.sh "Release 1.0.0" v1.0.0
```

Das Script baut das Repo (`repo/build_repo.py`), staged nur die gewünschten Dateien (addons/, repo/, README, CHANGELOG, .gitignore, ENTWICKLUNG), committet, pusht. Bei zweitem Argument (Tag) werden Tag erstellt und gepusht; ist die **GitHub CLI** (`gh`) installiert, wird das Release inkl. Beschreibung automatisch erstellt (englischer Abschnitt aus CHANGELOG + Neuinstallations-Hinweis). Ohne `gh` gibt das Script eine manuelle Anleitung aus.

## Contributors / Git-Author

Auf GitHub erscheinen nur Nutzer als Contributors, deren **Commit-Author** (Name + E-Mail) in den Commits steht. Wenn z. B. „Cursor“ oder ein Bot in den Contributors auftaucht, wurden Commits mit dessen Identity gemacht.

**Lösung:** Setze in diesem Repo (oder global) deinen Git-Author auf **deinen** Namen und deine E-Mail (die du bei GitHub nutzt):

```bash
cd ~/Projekte/Auto-FTP-Sync-Plus
git config user.name "Dein Name"
git config user.email "deine@email.com"
```

Cursor übernimmt beim Committen diese Konfiguration. Dann gehen alle Commits (aus Cursor oder Terminal) unter **deinem** Namen – du erscheinst als Contributor, Pushen funktioniert wie gewohnt. Cursor musst du nicht blockieren; wichtig ist nur, dass die Author-Daten stimmen.

## Was nicht auf GitHub geht

- `.gitignore` sorgt dafür, dass z. B. `__pycache__/`, `*.pyc`, `.DS_Store`, `*.log` nicht committed werden.
- `repo/output/` **wird** committed (addons.xml, Addon-ZIPs), damit GitHub Raw die Dateien für Kodi bereitstellen kann.
