# Veröffentlichung und künftige Pflege

Repository: **[Lorilonlon/camper-heater-bridge](https://github.com/Lorilonlon/camper-heater-bridge)**. Das Repository ist öffentlich. Der erste Quellstand wurde zunächst privat hochgeladen und in GitHub CI geprüft. Private Sicherheitsmeldungen, Secret Scanning und Push Protection sind aktiviert (03.10.2026).

## Auffindbarkeit

GitHub-Beschreibung:

> Unofficial Truma iNet Box integration for Home Assistant: local Bluetooth/MQTT control of Combi heating and hot water, sensors, dashboard and diagnostics.

Topics:

`truma`, `truma-inet`, `inet-box`, `home-assistant`, `homeassistant`, `home-assistant-addon`, `mqtt`, `bluetooth`, `camper`, `motorhome`, `combi`

README-Titel: **Camper Heater Bridge — Truma iNet-Box mit Home Assistant**.

In README und jedem Release bleibt die wesentliche KI-Mitwirkung sichtbar (AI_DISCLOSURE.md).

Die Begriffe benennen die tatsächliche Kompatibilität. Keine Logos, kein „official“, kein Herstellerkonto vortäuschen. Ranking oder Aufnahme in Suchmaschinen sind nicht garantiert.

## Ablauf für Veröffentlichungen

1. Offene Rechte-/Testpunkte in RELEASE_CHECKLIST.md bewerten. Bei ungeklärter Nutzungsberechtigung oder Drittinhalten nicht öffentlich hochladen.
2. Mit bestehender GitHub-Anmeldung oder offiziellem OAuth-/SSH-Verfahren anmelden; kein Konto-Passwort in Dateien oder Befehle schreiben. Für Commits bei Bedarf die im eigenen GitHub-Konto angezeigte noreply-Adresse verwenden, keine erfundene Adresse.
3. Neues Repository zunächst privat erstellen. Nur diesen bereinigten Ordner als neuen initialen Stand hochladen, nicht das Entwicklungsverzeichnis oder dessen Historie. `.gitignore` ersetzt keine Prüfung bereits getrackter Dateien.
4. CI ausführen und fehlerfreie Ergebnisse prüfen. Private vulnerability reporting, verfügbare Secret-/Push-Protection und geeignete Branch-Regeln aktivieren. Verfügbarkeit hängt von Repository-/Kontoeinstellungen ab.
5. Endgültige Sichtbarkeit bewusst auf öffentlich ändern, die obige Beschreibung/Topics setzen und `v0.1.8` als **Pre-release** veröffentlichen. Kein Container-Push und keine selbst gebauten Binaries als Assets.
6. Die tatsächliche Installation über die Repository-Adresse testen; erst bestätigte Prüfungen abhaken. Die bestehende Betreiberinstallation nicht nebenbei migrieren.

Die Repository-Adresse ist in README und repository.yaml hinterlegt. Für zukünftige Änderungen das bestehende Repository und die reguläre GitHub-Anmeldung verwenden. Funktionsänderungen nachvollziehbar dokumentieren und vor einem Release prüfen. GitHub-Passwörter, Tokens und private Hardwaredaten gehören weder in Commits noch in Release-Assets.
