# Strings und Lokalisierung

## Vollständigkeit

- **Neue String-IDs** (z. B. `L(30xxx)` im Code oder `label="30xxx"` in settings.xml) **immer in beide .po-Dateien eintragen:**
  - `resources/language/resource.language.de_de/strings.po`
  - `resources/language/resource.language.en_gb/strings.po`
- Jeder Eintrag: `msgctxt "#30xxx"`, `msgid "…"`, `msgstr "…"` (jeweils eigene Zeile; keine zusammengeklebten Zeilen).

## Richtlinien für Texte (informativ, anfängerfreundlich)

- **Einstellungen:** Kurzes, klares Label; wo nötig kurzer Hilfstext (was die Option bewirkt, wann man sie braucht).
- **Dialoge:** Vor Aktion: Was passiert konkret, welche Quelle/Verbindung/Speicherort betroffen ist. Nach Aktion: Erfolg/Fehler klar, bei Erfolg z. B. „Wo?“ / „Was wurde getestet?“.
- **Fehlermeldungen:** Nicht nur „Fehler“, sondern kurz **was** schiefging und **was der Nutzer tun kann** (z. B. „Verbindung fehlgeschlagen. Bitte Host, Benutzer und Passwort in den Einstellungen unter Verbindung prüfen.“).
- **Info-Seiten:** Pro Thema 1–3 Sätze Kontext, dann Schritte oder Optionen; für Laien ohne Fachbegriffe oder mit kurzer Erklärung.
- **Menü-Einträge:** Kurz und eindeutig (z. B. „Favoriten jetzt sichern“, „Verbindung testen“).

## Platzhalter

- Platzhalter (`%s`, `%d`, `{connection}`, `{path}` usw.) in **beiden Sprachen identisch** lassen; nur den umgebenden Text übersetzen.

## Nach Änderungen im Plugin

- Neue `L(30xxx)` oder `label="30xxx"` → sofort in beide .po eintragen.
- Beide .po-Dateien parallel anpassen (DE und EN).
- Bei neuen Aktionen/Dialogen: Vor-Dialog = Kontext + was passiert; Nach-Dialog = Ergebnis + ggf. „Getestet/Erstellt: …“.
