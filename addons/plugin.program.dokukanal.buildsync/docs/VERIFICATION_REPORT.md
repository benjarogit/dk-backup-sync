# Kodi-Addon – Vollständige Verifikationsausgabe

**Kurz-Übersicht:** Dieses Dokument ist die systematische Prüf- und Verifikationsausgabe für das Kodi-Python-Addon „Doku-Kanal BuildSync“ (Architektur addon.py / core / ui / utils / services); es listet Annahmen, Vollständigkeit, Testanforderungen, Linting, Integration und offene Punkte explizit auf.

---

## A. Annahmen

1. **Addon-Pfad:** Alle Pfade beziehen sich auf `/home/benny/.kodi/addons/plugin.program.dokukanal.buildsync/` (laut Workspace/Regel: Entwicklung nur im Kodi-Ordner).
2. **Kodi-Version:** Ziel ist Kodi v21 (Omega); addon.xml erfordert `xbmc.python` 3.0.0 und `xbmc.addon` 21.0.0.
3. **Keine Laufzeit in dieser Umgebung:** `xbmc`, `xbmcgui`, `xbmcaddon`, `xbmcplugin`, `xbmcvfs` sind in der Prüfumgebung nicht installierbar; alle Befehle, die diese Module importieren (pytest ohne Mock, mypy über Addon-Root), schlagen außerhalb von Kodi fehl oder liefern erwartete Import-Fehler.
4. **Unit-Tests:** Im Addon existieren derzeit **keine** Testdateien (`tests/`, `test_*.py`); die in Abschnitt C genannten Tests sind **synthetisch** und müssen vom Nutzer angelegt und mit Mocks (z. B. `xbmc`/`xbmcgui` gemockt) ausgeführt werden.
5. **Linting:** „Lint (OK/Issues)“ bezieht sich auf die IDE-/Linter-Diagnosen im Workspace; ein vollständiger pylint/mypy-Lauf über das gesamte Addon wurde **nicht** ausgeführt (weil Kodi-Module fehlen und viele Dateien dann Fehler melden).
6. **resources/lib:** Wird als Legacy/Parallelstruktur behandelt; die Plan-Zielstruktur priorisiert core/ui/utils/services; einige addon.py-Aktionen rufen noch `resources.lib.backup_restore` direkt auf (z. B. restore).
7. **Einstellungs-Buttons:** Es wird angenommen, dass settings.xml RunScript(Addon-ID, action) mit `action=...` nutzt und addon.py bei Handle -1 die Marker-Logik anwendet (laut Projektregel).

---

## B. Vollständigkeits-Checkliste (Datei / Funktion / Erwartung / Status)

| Datei | Funktion | Erwartete Aufgabe | Existiert | Docstring | Typannotationen | Unit-Test | Lint |
|-------|----------|-------------------|-----------|-----------|-----------------|-----------|------|
| addon.py | _format_sync_result | Sync-Ergebnis in lokalisierte Nachricht | ja | teil (1 Zeile) | fehlend | nein | OK |
| addon.py | _run_action | Dispatcher action → Service + UI | ja | teil | fehlend | nein | OK |
| addon.py | _show_info_dialog | Infotext anzeigen | ja | fehlend | fehlend | nein | OK |
| addon.py | _show_about_dialog | About-Dialog | ja | fehlend | fehlend | nein | OK |
| addon.py | _maybe_show_changelog_once | Changelog einmal anzeigen | ja | fehlend | fehlend | nein | OK |
| addon.py | route_main | Hauptmenü-Liste füllen | ja | fehlend | fehlend | nein | OK |
| addon.py | _add_settings_actions_items | Einstellungs-Aktionen-Liste | ja | fehlend | fehlend | nein | OK |
| addon.py | route_category | Kategorie-Untermenü | ja | fehlend | fehlend | nein | OK |
| addon.py | route_static | Statische Favoriten-Liste | ja | fehlend | fehlend | nein | OK |
| addon.py | route_execute | Favoriten-Befehl ausführen | ja | fehlend | fehlend | nein | OK |
| core/config.py | (Modul) | ADDON, Pfade, Konstanten | ja | voll | – | nein | OK |
| core/logging_utils.py | log | Log mit Präfix | ja | voll | fehlend | nein | OK |
| core/settings.py | get_string, get_bool, set_string, set_bool | Settings lesen/schreiben | ja | voll/teil | fehlend | nein | OK |
| core/settings.py | L | Lokalisierung | ja | voll | fehlend | nein | OK |
| core/settings.py | ensure_settings_initialized | Schema/Init | ja | voll | fehlend | nein | OK |
| core/kodi_api.py | raw_log, sleep, executebuiltin, translate_path, get_addon, get_info_label | Kodi-Wrapper | ja | teil | fehlend | nein | OK |
| core/kodi_api.py | Dialog, DialogProgress, ListItem | UI-Wrapper | ja | teil | fehlend | nein | OK |
| core/kodi_api.py | add_directory_item, end_of_directory, set_plugin_category, set_content | Plugin-API | ja | teil | fehlend | nein | OK |
| ui/dialogs.py | show_confirm, show_result, show_text, show_ok | Einfache Dialoge | ja | teil | fehlend | nein | OK |
| ui/dialogs.py | run_with_info_and_confirm, confirm_then_run | Bestätigung + Aktion | ja | teil | fehlend | nein | OK |
| ui/list_builder.py | add_item, add_category_item, end_of_directory, set_plugin_category | Listenaufbau | ja | teil | fehlend | nein | OK |
| utils/params.py | parse_param_string | Query parsen | ja | teil | fehlend | nein | OK |
| utils/params.py | Params (get, get_action, get_mode, get_name, get_folder, get_path, get_cmd) | Parameter-Zugriff | ja | teil | fehlend | nein | OK |
| utils/favourites_merge.py | parse_favourites, write_favourites, merge_union | Favoriten-Merge | ja | voll/teil | fehlend | nein | OK |
| utils/static_favourites.py | get_static_favourites_path, get_folder_path, get_favourites_xml_path, read_favourites | Statische Favoriten | ja | teil | fehlend | nein | OK |
| utils/paths.py | join_userdata, join_addon_data | Pfad-Hilfen | ja | teil | fehlend | nein | OK |
| services/backup_service.py | create_backup | Backup-ZIP erstellen | ja | voll | fehlend (progress_callback) | nein | OK |
| services/backup_service.py | restore_backup | Aus ZIP wiederherstellen | ja | voll | fehlend | nein | OK |
| services/favorites_service.py | save_favorites | Favoriten sync (Merge/Backup) | ja | voll | fehlend | nein | OK |
| services/network_service.py | test_connection | FTP/SFTP/SMB testen | ja | teil | fehlend | nein | OK |
| services/network_service.py | test_image_sources | Bildquellen-URL testen | ja | teil | fehlend | nein | OK |
| services/network_service.py | get_connection_summary | Verbindungszusammenfassung | ja | teil | fehlend | nein | OK |
| services/autoclean_service.py | run_autoclean | Cache/Thumbs aufräumen | ja | teil | fehlend | nein | OK |
| services/autoclean_service.py | set_next_run | Nächsten Lauf setzen | ja | teil | fehlend | nein | OK |
| services/wizard_service.py | run_wizard_once, reset_and_run_wizard | Wizard einmal / manuell | ja | fehlend | fehlend | nein | OK |
| services/skin_install_service.py | install_skin_or_show_info | Skin prüfen/installieren | ja | voll | fehlend | nein | OK |
| services/sync_remote_service.py | ensure_remote_structure | Remote-Ordner anlegen | ja | teil | fehlend | nein | OK |
| services/sync_addon_data_service.py | sync_addon_data | addon_data per ZIP sync | ja | teil | fehlend | nein | OK |
| services/image_rotation_service.py | download_random_image | Hintergrundbild laden | ja | teil | fehlend | nein | OK |
| service.py | (Script) | Service-Start → auto_ftp_sync.run_startup | ja | teil | – | nein | OK |
| run_wizard.py | (Script) | Wizard oder RunPlugin-Dispatch | ja | teil | – | nein | OK |
| auto_ftp_sync.py | run_startup | Startup-Sequenz (Wizard, Sync, …) | ja | voll | fehlend | nein | OK |
| auto_ftp_sync.py | sync_favourites, test_connection, test_image_sources, … | Fachlogik (noch zentral) | ja | voll/teil | fehlend | nein | OK |
| resources/lib/backup_restore.py | create_backup_core, restore_from_zip_core, run_backup, run_restore | Backup-Kernlogik | ja | voll/teil | fehlend | nein | OK |

**Zusammenfassung B:** Existenz aller genannten Module/Funktionen: **ja**. Docstrings: überwiegend **teil** (kurz, oft ohne Args/Returns); Typannotationen: **fehlend** in fast allen Dateien. Unit-Tests: **keine** vorhanden. Lint: an geprüften Dateien **OK** (IDE meldet nur xbmc*-Unresolved, was erwartet ist).

---

## C. Unit-Tests (synthetisch – müssen mit Kodi-Mocks ausgeführt werden)

**UNVOLLSTÄNDIG:** Es existieren keine echten Testdateien im Addon. Die folgenden Testfälle sind **Beispiel-Tests**, die nur laufen, wenn `xbmc`/`xbmcgui`/`xbmcaddon`/`xbmcvfs` gemockt werden (z. B. via `sys.modules` oder pytest-Plugins). Sofern keine Runtime mit Kodi-Modulen oder konsistenten Mocks bereitgestellt wird, können diese Tests **nicht** verifiziert werden.

**How to run (nach Anlegen der Datei):** `pytest -q tests/test_utils_params.py` (aus Addon-Root, mit gemockten Kodi-Modulen).

### Beispiel: tests/test_utils_params.py (nur Utils – keine Kodi-Imports in get_action/get)

```python
# How to run: pytest -q tests/test_utils_params.py
# Voraussetzung: Kein Import von Modulen, die xbmc nutzen; Params/parse_param_string sind rein.
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_parse_param_string_empty():
    from utils.params import parse_param_string
    assert parse_param_string('') == {}
    assert parse_param_string(None) == {}

def test_parse_param_string_action():
    from utils.params import parse_param_string
    out = parse_param_string('action=backup')
    assert out.get('action') == 'backup'

def test_params_get_action():
    from utils.params import Params
    p = Params('action=test_connection&connection=1')
    assert p.get_action() == 'test_connection'
    assert p.get('connection') == '1'

def test_params_get_mode_fallback():
    from utils.params import Params
    p = Params('mode=backup')
    assert p.get_action() == 'backup'
```

### Beispiel: tests/test_utils_favourites_merge.py (reine Logik, keine Kodi-Pfade)

```python
# How to run: pytest -q tests/test_utils_favourites_merge.py
# Nutzt nur parse_favourites/write_favourites/merge_union mit lokalen Dateien oder Temp.
import sys
import os
import tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_merge_union_empty():
    from utils.favourites_merge import merge_union
    assert merge_union([], []) == []
    assert merge_union([], ['a']) == ['a']
    assert merge_union(['a'], []) == ['a']

def test_merge_union_dedup():
    from utils.favourites_merge import merge_union
    got = merge_union(['a', 'b'], ['b', 'c'])
    assert got == ['a', 'b', 'c']
```

### Beispiel-Input/Output (konkret)

- **parse_param_string('action=backup')** → Erwartung: `{'action': 'backup'}` (Dict).
- **Params('action=sync_favourites_now').get_action()** → Erwartung: `'sync_favourites_now'` (str).
- **merge_union(['x'], ['y'])** → Erwartung: `['x', 'y']` (list).

Tests für **services/backup_service**, **network_service**, **favorites_service** usw. erfordern durchgängig Mocks für `xbmc`, `xbmcvfs`, `ADDON`, `resources.lib.backup_restore` bzw. `auto_ftp_sync`; sie wurden nicht ausgeführt und sind hier nur als „synthetisch“ referenziert.

---

## D. Linting & Typprüfung

**Befehle (aus Addon-Root):**

- **pylint:**  
  `pylint addon.py core/ ui/ utils/ services/ --disable=import-error,no-name-in-module`  
  (import-error/no-name-in-module deaktivieren, weil xbmc* außerhalb von Kodi nicht existiert.)  
  Erwartung: Score möglichst ≥ 8,5; keine fatalen Fehler. Ohne Disable: viele „Import xbmc“ Fehler.

- **flake8:**  
  `flake8 addon.py core/ ui/ utils/ services/ --max-line-length=120 --extend-ignore=E501,W503`  
  Erwartung: Exit 0 bei sauberem Stil.

- **mypy:**  
  `mypy addon.py core/ ui/ utils/ services/ --ignore-missing-imports --no-error-summary 2>&1 || true`  
  Erwartung: Mit `--ignore-missing-imports` bleiben nur echte Typfehler; ohne Kodi-Stubs sind viele „module has no attribute“ Meldungen möglich.

**Konkrete Beispiel-Ausgabe bei Fehler (pylint):**

```
************* Module addon
addon.py:11:0: E0401: Import error: No module named 'xbmcvfs'
```

**Toleranz:** Import-Fehler für `xbmc`, `xbmcgui`, `xbmcaddon`, `xbmcplugin`, `xbmcvfs` werden als Umgebungsproblem akzeptiert; alle anderen Lint-/Typ-Fehler sollten behoben werden.

**Hinweis:** Ein vollständiger Lauf von pylint/flake8/mypy über das gesamte Addon wurde in dieser Verifikation **nicht** ausgeführt; die Angaben basieren auf typischer Kodi-Addon-Struktur und den gelesenen Dateien.

---

## E. Integrationstest (Kodi)

**Schritt-für-Schritt Prüfprotokoll (manuell im Kodi-Environment):**

1. **Installation:** Addon aus ZIP oder Repo installieren; in addon.xml muss `library="addon.py"` (pluginsource) und `library="service.py"` (service) stehen.
2. **Plugin-URL ohne Parameter (Hauptmenü):**  
   - Aufruf: `plugin://plugin.program.dokukanal.buildsync/`  
   - Erwartung: Liste mit Einträgen (Einstellungen, Favoriten sichern, Verbindung testen, Backup erstellen, …); keine leere Liste, keine 0,00 B als Label.
3. **Action backup:**  
   - Aufruf: `plugin://plugin.program.dokukanal.buildsync/?action=backup`  
   - Erwartung: Bestätigungsdialog → nach „Erstellen“ Progress → am Ende Ergebnis-Dialog (Pfad/Größe oder Fehler).
4. **Action sync_favourites_now:**  
   - Aufruf: `plugin://plugin.program.dokukanal.buildsync/?action=sync_favourites_now`  
   - Erwartung: Bestätigungsdialog (Sichern/Abbrechen) → nach Sichern Progress oder kurze Verarbeitung → Ergebnis-Dialog (lokale Sicherung oder Sync-Ergebnis); **nicht** sofort schließen und leere Liste mit 0,00 B.
5. **Action test_connection:**  
   - Aufruf: `plugin://plugin.program.dokukanal.buildsync/?action=test_connection`  
   - Erwartung: Dialog mit Verbindungszusammenfassung → Testen/Abbrechen → Progress → OK-Dialog mit Erfolg oder Fehlermeldung.
6. **Action test_image_sources:**  
   - Aufruf: `plugin://plugin.program.dokukanal.buildsync/?action=test_image_sources`  
   - Erwartung: Bestätigung → Progress → OK-Dialog; **kein** Kodi-Absturz.
7. **Aufruf aus Einstellungen (Handle -1):**  
   - Einstellungen öffnen → Add-on → Doku-Kanal BuildSync → „Favoriten jetzt sichern“ (bzw. 12. Radiobutton).  
   - Erwartung: Dialog erscheint; nach Klick „Sichern“ läuft die Aktion; am Ende Ergebnis-Dialog; **nicht** nur Liste mit 0,00 B.

**Erfolgskriterium:** Alle genannten Aufrufe zeigen die erwarteten Dialoge und führen nicht zu leerer Liste oder Absturz. Kodi-Log (`~/.kodi/temp/kodi.log` bzw. `special://temp/kodi.log`) enthält bei Erfolg keine Python-Tracebacks.

**Einschränkung:** Die tatsächliche Ausführung der Integrationstests erfolgte **nicht** in dieser Verifikation (kein Kodi-Runtime); die Schritte sind reproduzierbare Anweisungen für Sie zur manuellen Verifikation.

---

## F. Edge-Cases & Fehlerfälle

| Fall | Erwartete Handhabung | Wo umgesetzt / Anmerkung |
|------|----------------------|---------------------------|
| Keine Verbindung konfiguriert (Favoriten sichern) | Nur lokales .bak; Rückgabe (True, msg_id) mit Hinweis „nur lokal“ | auto_ftp_sync.sync_favourites / _favourites_local_backup_only |
| FTP/SFTP/SMB nicht erreichbar | test_connection gibt (False, Fehlermeldung) zurück; Dialog zeigt Fehler | network_service → auto_ftp_sync.test_connection |
| Bildquellen-URL ungültig / Timeout | test_image_sources → (False, Fehlermeldung) | auto_ftp_sync.test_image_sources |
| Backup-Ziel nicht beschreibbar | create_backup_core → (False, Fehlermeldung) | backup_restore.create_backup_core |
| ZIP korrupt bei Restore | restore_from_zip_core → (False, Fehlermeldung); BadZipFile abgefangen | backup_restore.restore_from_zip_core |
| Kein Speicherplatz | Schreibfehler beim ZIP/Datei; Exception → (False, str(e)) bzw. dialog.ok | backup_restore / addon Wrapper |
| Handle -1 (Einstellungen) | Keine Listen-APIs (setPluginCategory/addDirectoryItem); nur Aktion + Dialoge | addon.py: HANDLE == -1 → Marker; Listen nur bei HANDLE >= 0 |
| Ungültige action | Router führt keine Aktion aus oder fallback; ggf. route_main | addon.py: action in DIRECT_ACTIONS |
| settings_schema_version / Invalid setting type | safe_get_* Reparatur in core/settings; ensure_settings_initialized | core/settings.py |

Nicht für alle Fälle (z. B. exakter Timeout-Wert bei URLs, „disk full“) wurde der Code zeilenweise verifiziert; die Tabelle gibt die **erwartete** Handhabung und die zugehörigen Stellen an.

---

## G. Sicherheits- & Robustheits-Check

| Risiko | Gegenmaßnahme / Status |
|--------|------------------------|
| Pfad-Injection (z. B. ../ in Parametern) | Params liefert unquote_plus; Pfade für Backup/Restore aus Einstellungen oder Dateiauswahl; keine ungeprüfte User-Eingabe direkt als Dateipfad. |
| Unsichere Dateioperationen | backup_restore nutzt os.path.join, feste Excludes; ZIP-Extract in HOME – Risiko Zip-Slip möglich, wenn Namelist nicht geprüft wird (sollte in restore_from_zip_core geprüft werden). |
| Exception-Handling | addon._run_action in try/except mit log und dialog.ok; run_actions/auto_ftp_sync haben try/except; vereinzelt breites `except Exception`. |
| Passwörter in Logs | get_connection_summary und Logs dürfen keine Passwörter ausgeben; in get_connection_summary werden nur Host/User/BasePath ausgegeben. |

**Empfehlung:** In `restore_from_zip_core` jeden Eintrag aus `zf.namelist()` auf path traversal prüfen (z. B. `os.path.normpath` und prüfen, dass unter `extract_root` bleibend).

---

## H. Unvollständige Punkte / ToDo

1. **Unit-Tests ausführen:** Keine Tests vorhanden; synthetische Tests (Abschnitt C) wurden **nicht** ausgeführt. Beschaffung: Tests anlegen, `xbmc`/`xbmcgui`/`xbmcaddon`/`xbmcvfs` mocken (z. B. in `conftest.py` oder `tests/mocks/`), dann `pytest tests/` aus Addon-Root ausführen.
2. **Linting vollständig:** pylint/flake8/mypy wurden **nicht** über alle Dateien ausgeführt. Beschaffung: In der Umgebung (mit `--disable=import-error` bzw. `--ignore-missing-imports`) die Befehle aus Abschnitt D ausführen und Ausgabe prüfen.
3. **Integration in Kodi:** Kein Zugriff auf Kodi-Runtime; Integrationstest (Abschnitt E) nur als Anleitung formuliert. Beschaffung: Addon in Kodi starten und jeden Aufruf (plugin:// URLs + Einstellungs-Buttons) manuell durchspielen; Kodi-Log prüfen.
4. **Typannotationen flächendeckend:** Viele Funktionen haben keine Typannotationen; Plan fordert Tuple[bool, str] etc. Beschaffung: Schrittweise in services/core/ui/utils Args/Returns annotieren und mypy erneut laufen lassen.
5. **Docstrings PEP 257:** Viele Docstrings ohne Args/Returns. Beschaffung: Pro Modul Args/Returns/Raises ergänzen gemäß docs/NAMING_AND_DOCUMENTATION.md.
6. **Coverage-Schwelle:** Nicht gemessen. Beschaffung: `coverage run -m pytest tests/` (nach Anlegen der Tests und Mocks), `coverage report`; akzeptable Schwelle z. B. 85 % für services/utils (core/ui können niedriger sein wegen Kodi-API).

---

## Final Verification Statement

**NICHT VERIFIZIERT: 6 offene Punkte**

- Unit-Tests fehlen; synthetische Tests nicht ausgeführt.
- Linting (pylint/flake8/mypy) nicht vollständig über alle Dateien gelaufen.
- Integrationstest in Kodi nicht ausgeführt (keine Kodi-Runtime).
- Typannotationen und PEP-257-Docstrings nicht flächendeckend geprüft/umgesetzt.
- Coverage nicht gemessen.
- Zip-Slip-Prüfung in restore_from_zip_core nicht im Code verifiziert.

---

## JSON-Zusammenfassung

```json
{
  "summary": "Verifikation des Kodi-Addons Doku-Kanal BuildSync; Architektur und Dateien erfasst, keine Tests vorhanden, Linting/Integration nicht ausgeführt.",
  "assumptions": [
    "Addon-Pfad: .kodi/addons/plugin.program.dokukanal.buildsync",
    "Kodi v21; keine xbmc*-Runtime in Prüfumgebung",
    "Unit-Tests synthetisch; Ausführung nur mit Mocks möglich",
    "resources/lib als Legacy/Parallelstruktur",
    "Einstellungs-Buttons nutzen RunScript und Handle -1"
  ],
  "files": [
    { "path": "addon.py", "functions": [{ "name": "_run_action", "status": "ok", "tests": "missing" }, { "name": "route_main", "status": "ok", "tests": "missing" }] },
    { "path": "core/config.py", "functions": [], "status": "ok", "tests": "missing" },
    { "path": "core/kodi_api.py", "functions": [{ "name": "raw_log", "status": "ok", "tests": "missing" }, { "name": "Dialog", "status": "ok", "tests": "missing" }] },
    { "path": "services/backup_service.py", "functions": [{ "name": "create_backup", "status": "ok", "tests": "missing" }, { "name": "restore_backup", "status": "ok", "tests": "missing" }] },
    { "path": "services/favorites_service.py", "functions": [{ "name": "save_favorites", "status": "ok", "tests": "missing" }] },
    { "path": "services/network_service.py", "functions": [{ "name": "test_connection", "status": "ok", "tests": "missing" }, { "name": "test_image_sources", "status": "ok", "tests": "missing" }] }
  ],
  "tests_created": ["test_utils_params.py (synthetisch)", "test_utils_favourites_merge.py (synthetisch)"],
  "lint_issues": ["Import-error für xbmc* außerhalb Kodi erwartet; sonst keine Linter-Fehler in Stichprobe"],
  "integration_steps": ["plugin://... ohne Parameter", "?action=backup", "?action=sync_favourites_now", "?action=test_connection", "?action=test_image_sources", "Einstellungs-Button Favoriten sichern"],
  "open_items": ["Unit-Tests anlegen und mit Mocks ausführen", "pylint/flake8/mypy vollständig laufen lassen", "Integration in Kodi manuell prüfen", "Typannotationen und PEP-257 Docstrings ergänzen", "Coverage messen", "Zip-Slip in restore_from_zip_core prüfen"]
}
```
