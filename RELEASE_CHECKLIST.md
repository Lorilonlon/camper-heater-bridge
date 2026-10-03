# Veröffentlichungsstand — 03.10.2026

Vorbereitet als experimenteller Quellcode-Pre-Release, noch nicht online veröffentlicht. Bridge 0.1.8, optionale Kompatibilität 0.1.2. Kein Update der laufenden Betreiberanlage im Rahmen dieser Vorbereitung.

## Erledigt

- [x] Eigenständiger Projektname; Truma/Home Assistant beschreibend in Titel, Beschreibung und vorgeschlagenen Topics.
- [x] Wesentliche KI-Mitwirkung sichtbar in README, Release-Hinweisen und Beitragsregeln.
- [x] Bestehende MIT-Lizenz des eigenen Codes erhalten; Fremdlizenzen und BlueZ-Header-Risiko für Binärverteilung dokumentiert.
- [x] Reine Quellcode-Veröffentlichung; keine Images, Shared Libraries oder Original-Herstellerdateien.
- [x] Dokumentierter Umfang der App-Untersuchung, kein falscher Clean-Room-Anspruch.
- [x] Betreiber erklärt: keine besondere Geheimhaltungs-/Entwicklervereinbarung mit Truma.
- [x] Betreiber meldet am 03.10.2026 problemlosen Alltagsbetrieb. Keine Behauptung eines vollständig ausgewerteten Langzeitlogs.
- [x] Private Arbeitsverzeichnisse, Mitschnitte und deren Historie nicht übernommen; separates Quellpaket ohne alte Git-Historie.
- [x] Geplante Repository-Adresse, Installationshinweise, Issue-/PR-Vorlagen und Sicherheitsmeldung vorbereitet.

## Vor dem öffentlichen Upload zu klären

- [ ] Herausgeber bestätigt seine Berechtigung zur Nutzung der untersuchten Original-App und bewertet etwaige weitere Vertragsbedingungen. Keine anwaltliche Einzelfallprüfung durchgeführt.
- [ ] Sichere GitHub-Anmeldung, private Sicherheitsmeldungen und verfügbare Secret-/Push-Schutzfunktionen tatsächlich aktivieren.
- [ ] Erstes privates Repository und GitHub-CI ausführen; lokale Tests ersetzen keine erfolgreichen GitHub-Läufe.
- [ ] Vor endgültigem Upload `python scripts/check_release.py` ausführen; Änderungen und ggf. neu erzeugte Git-Historie erneut prüfen.

## Technisch weiter offen / im Pre-Release sichtbar

- [ ] Frische Installation aus dem GitHub-App-Repository und kontrollierter vollständiger Host-Neustart.
- [ ] Physische Bestätigung Warmwasser Aus/Boost unter geeigneten Bedingungen.
- [ ] Weitere Hardwarekombinationen und unabhängige technische Prüfung.
- [ ] Bei künftigen Binär-/Container-Releases: tatsächliche SBOM, Original-Lizenztexte, korrespondierender Quellcode und Lizenzkompatibilität vollständig bearbeiten.

Aktuelle lokale Prüfergebnisse stehen in VALIDATION.md. Der fehlende Haken bei einem realen Gerätetest darf nicht durch einen Unit-Test ersetzt werden.
