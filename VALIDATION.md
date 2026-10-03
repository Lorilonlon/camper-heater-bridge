# Prüfung des Veröffentlichungsstands

Stand: 03.10.2026. Lokale Prüfung des bereinigten Quellpakets, keine unabhängige Auditierung.

| Prüfung | Ergebnis |
|---|---|
| Python-Tests in isolierter Python-3.14-Umgebung | 49 Tests bestanden |
| JavaScript-Syntax der Dashboard-Karte | bestanden |
| Explizite Datei-Allowlist und Musterprüfung | 47 geprüfte Textdateien, keine Treffer im Veröffentlichungspaket |
| Negativtests des Prüfers | unbekannte Datei, synthetischer Token, Nicht-Beispiel-MAC und privater Optionswert erkannt |
| Historienprüfung des Prüfers | synthetischer Token auch nach Löschung aus aktuellem Stand noch in Test-Git-Historie erkannt |
| Git-Historie des Veröffentlichungspakets | keine alte Git-Historie enthalten |
| Python-Paketmetadaten | direkte und aufgelöste transitive Pakete in DEPENDENCIES.json dokumentiert |
| GitHub-CI | Erster Lauf [37107264032](https://github.com/Lorilonlon/camper-heater-bridge/actions/runs/37107264032) erfolgreich: Python 3.13, Python 3.14 und Linux-C-Tests; Änderungen danach lösen erneut CI aus |
| C-Tests / Linux | Acht C-Fälle im GitHub-Linux-Job erfolgreich. Kein neuer vollständiger Container-/Hardwaretest behauptet |
| Reale Betreiberanlage | laut Betreiber am 03.10.2026 problemloser Betrieb; bei dieser Vorbereitung nicht verändert und keine neuen Steuerbefehle gesendet |
| Frische GitHub-Installation / vollständiger Host-Neustart | offen |
| Rechtsprüfung | Quellenrecherche und Umfangs-/Lizenzprüfung, keine anwaltliche Einzelfallfreigabe |

Musterprüfungen können unbekannte Geheimnisformate oder Rechte Dritter nicht vollständig ausschließen. Die Verteilung bleibt auf den explizit geprüften Quellumfang begrenzt. Eine spätere Git-Historie und jedes ergänzte Artefakt müssen erneut geprüft werden. Den Prüfer nicht durch automatisches Freigeben beliebiger neuer Dateien umgehen.

Die Funktionsimplementierung der laufenden Version wird in diesem Vorbereitungsschritt nicht ersetzt. Änderungen betreffen Veröffentlichung, öffentliche Bezeichnungen, Dokumentation und Prüfwerkzeuge. KI-Mitwirkung ist in AI_DISCLOSURE.md und den Release-Hinweisen offengelegt.
