# Dateistruktur, Benennung und Dokumentation – Kodi-Addon (Python)

Orientierung: PEP 8 (Code Style), PEP 257 (Docstrings). Klare Trennung von Routing, Fachlogik (Services), UI, Core und Utilities. Kodi-API gekapselt.

---

## 1. Dateistruktur

```
addon.py                      # Entry-Point + Routing
service.py                    # Service-Entry (Startup)
run_wizard.py                 # Script-Entry (Wizard)

core/
  __init__.py
  config.py                   # Addon, Pfade, Konstanten
  logging_utils.py            # Logging
  settings.py                 # Einstellungen, Lokalisierung
  kodi_api.py                 # Kapselung xbmc, xbmcgui, xbmcplugin, xbmcvfs

ui/
  __init__.py
  dialogs.py                  # Dialoge (confirm, progress, text, result)
  list_builder.py             # Plugin-Listen (add_item, end_of_directory)

utils/
  __init__.py
  params.py                   # URL-Parameter parsen
  paths.py                    # Pfad-Hilfen
  favourites_merge.py         # Favoriten-Merge-Logik
  static_favourites.py        # Statische Favoriten

services/
  __init__.py
  backup_service.py           # backup_create, backup_restore
  favorites_service.py        # save_favorites
  network_service.py         # test_connection, test_image_sources
  autoclean_service.py        # run_autoclean
  wizard_service.py           # run_wizard_once, reset_and_run_wizard
  skin_install_service.py     # install_skin_or_show_info
  sync_addon_data_service.py # sync_addon_data (Service-Start)
  sync_remote_service.py      # ensure_remote_structure (Service-Start)
  image_rotation_service.py  # download_random_image (Service-Start)

resources/
  settings.xml
  language/
  images/
docs/
  NAMING_AND_DOCUMENTATION.md # Dieses Dokument
```

- **Nur Kleinbuchstaben**, **snake_case**, **keine Bindestriche**, **kein CamelCase** in Dateinamen.
- Fachmodule mit Suffix: `*_service.py`, `*_utils.py`, `*_manager.py`, `*_handler.py` wie oben.

---

## 2. Dateibenennung

| Regel | Beispiel |
|-------|----------|
| Nur Kleinbuchstaben | `config.py`, `backup_service.py` |
| snake_case | `list_builder.py`, `favourites_merge.py` |
| Keine Bindestriche | `kodi_api.py` statt `kodi-api.py` |
| Keine CamelCase | `dialogs.py` statt `Dialogs.py` |
| Semantisch, eindeutig | `favorites_service.py` (Fachlogik Favoriten) |
| Suffix für Fachmodule | `*_service.py`, `*_utils.py`, `*_manager.py`, `*_handler.py` |

---

## 3. Modulbenennung (Import-Pfade)

- Verzeichnis = Paket: `core`, `ui`, `utils`, `services`.
- Dateiname = Modulname: `from core.config import ADDON_ID`.
- Keine Abkürzungen in Modulnamen: `logging_utils.py` statt `log_util.py`.

---

## 4. Funktionsbenennung

| Regel | Beispiel | Vermeiden |
|-------|----------|-----------|
| snake_case | `create_backup`, `test_connection` | `createBackup`, `TestConnection` |
| Verb + Objekt | `save_favorites`, `run_autoclean` | `do_action`, `run` |
| Eindeutig, nicht generisch | `test_connection(connection_number)` | `do_stuff`, `handle_click` |
| Keine unnötigen Abkürzungen | `connection_number` | `conn_num` (nur bei etablierter Abkürzung ok) |
| Öffentliche API: kein führender Unterstrich | `save_favorites()` | `_internal_helper()` (intern) |

**Beispiele aus dem Addon:**

- `create_backup()` – Backup erstellen
- `restore_backup()` – Backup wiederherstellen
- `save_favorites()` – Favoriten sichern (Merge/Backup)
- `test_connection(connection_number=None)` – Verbindung testen
- `test_image_sources()` – Bildquellen-URL testen
- `run_autoclean()` – AutoClean ausführen
- `run_wizard_once()` – Wizard einmalig (z. B. beim Start)
- `reset_and_run_wizard()` – Wizard zurücksetzen und starten
- `install_skin_or_show_info()` – Skin installieren oder „bereits installiert“ anzeigen

---

## 5. Modul-Dokumentation (PEP 257)

Jede Datei beginnt mit einem Modul-Docstring.

**Inhalt:**

- Kurzbeschreibung der **Verantwortlichkeit** des Moduls.
- Optional: Einordnung im System (z. B. „Wird nur von addon.py / Service verwendet“).

**Beispiel:**

```python
# -*- coding: utf-8 -*-
"""
Konfiguration und Pfade des Addons.

Stellt ADDON, ADDON_ID, ADDON_PATH, ADDON_DATA, USERDATA, HOME, TEMP
sowie ICON_PATH bereit. Keine Kodi-API-Aufrufe außer über das Addon-Objekt.
Gehört zur Core-Schicht; wird von allen anderen Schichten referenziert.
"""
```

---

## 6. Funktions-Dokumentation (PEP 257)

Jede öffentliche Funktion hat einen Docstring direkt unter der Signatur.

**Empfohlene Struktur:**

- Erste Zeile: Kurzbeschreibung (Imperativ, z. B. „Erstellt ein Backup …“).
- Leerzeile.
- `Args:` mit Parametern (Name, Typ, Bedeutung).
- `Returns:` (Typ und Bedeutung).
- `Raises:` nur falls relevant.

**Beispiel:**

```python
def create_backup() -> Tuple[bool, str]:
    """
    Erstellt ein ZIP-Backup der konfigurierten Pfade (userdata/addon_data).

    Returns:
        Tuple[bool, str]: (Erfolg, Meldungstext für UI).

    Raises:
        Keine; Fehler werden abgefangen und als (False, Fehlermeldung) zurückgegeben.
    """
```

```python
def test_connection(connection_number: Optional[int] = None) -> Tuple[bool, str]:
    """
    Testet die konfigurierte FTP/SFTP/SMB-Verbindung.

    Args:
        connection_number: 1, 2 oder 3 für Profil; None für aktives Profil.

    Returns:
        Tuple[bool, str]: (Erfolg, Meldungstext für UI).
    """
```

- **Typannotationen** wo sinnvoll: `Optional[int]`, `Tuple[bool, str]`, `Dict[str, Any]`.
- Keine redundanten Beschreibungen (z. B. nicht „connection_number: die Verbindungsnummer“).

---

## 7. Kommentare im Code

- **Warum** kommentieren, nicht **Was** (der Code soll selbsterklärend sein).
- Keine offensichtlichen Kommentare (`i += 1  # erhöhe i`).
- Komplexe Logik oder Architekturentscheidungen kurz begründen.

**Beispiel:**

```python
# Handle -1: Kodi ruft aus Einstellungen ohne gültigen Container auf;
# Listen-APIs (addDirectoryItem, endOfDirectory) würden abstürzen.
if handle < 0:
    return
```

---

## 8. Architekturprinzip (Kurz)

- **Routing (addon.py):** Nur argv/Params auswerten und **genau eine** Service- oder UI-Funktion pro `action` aufrufen. Keine Business-Logik.
- **Services:** Eine Funktion = eine fachliche Aufgabe. Rückgabe (z. B. `Tuple[bool, str]`). Keine Dialoge, keine anderen Services aufrufen.
- **UI:** Nur Darstellung (Dialoge, Listen). Ruft ggf. Services auf, enthält aber keine Fachlogik.
- **Core:** Config, Logging, Settings, gekapselte Kodi-API. Keine Fachlogik.
- **Utils:** Wiederverwendbare Hilfen (Params, Pfade, Merge). Keine Kodi-UI.
- **Kodi-API:** Nur in `core/kodi_api.py` (und über diese Kapselung in UI). Nicht verteilt in Services/Utils.

---

## 9. Checkliste vor Commit

- [ ] Alle Module mit Modul-Docstring.
- [ ] Öffentliche Funktionen mit Args/Returns (und ggf. Raises).
- [ ] Dateinamen: nur Kleinbuchstaben, snake_case, sinnvolle Suffixe.
- [ ] Funktionsnamen: snake_case, Verb + Objekt, keine generischen Namen.
- [ ] Typannotationen bei neuen/geänderten Funktionen.
- [ ] Kommentare nur für „Warum“ oder nicht-triviale Logik.
- [ ] Keine Vermischung von UI und Fachlogik; Kodi-API nur über core.
