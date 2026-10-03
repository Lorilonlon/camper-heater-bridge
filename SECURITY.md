# Sicherheit und vertrauliche Meldungen

Dieses Projekt steuert reale Geräte. Bei unerwartetem Verhalten die Bridge stoppen und die Anlage lokal nach Herstelleranleitung bedienen. Ein Softwarestatus ersetzt keine physische Kontrolle.

## Meldung einer Sicherheitslücke

Keine Passwörter, Tokens, Bluetooth-Schlüssel, vollständigen Bugreports oder privaten Mitschnitte in öffentliche Issues oder Pull Requests laden. Für Sicherheitslücken die private GitHub-Funktion **Security → Report a vulnerability** verwenden, sofern sie im Repository aktiviert ist. Ist sie noch nicht verfügbar, zunächst ein inhaltsarmes Issue mit der Bitte um einen privaten Meldeweg eröffnen; keine ausnutzbaren Details oder Zugangsdaten veröffentlichen. Ein privater Meldeweg und die GitHub-Schutzfunktionen müssen beim Erstellen des Repositorys aktiviert werden; diese Dateien erledigen das nicht automatisch.

Bereits veröffentlichte Zugangsdaten widerrufen bzw. ändern. Löschen aus einem aktuellen Commit beseitigt Kopien in Git-Historie, Forks und Caches nicht zuverlässig.

## Daten und Vertrauensgrenzen

- MQTT-Zugangsdaten und Geräteadresse nur in privaten App-Optionen speichern. MQTT-Broker und Home-Assistant-Zugang absichern.
- Der optionale Kompatibilitätsdienst erhält weitreichenden Host-D-Bus-/Share-Zugriff und verändert den gemeinsamen Bluetooth-Dienst. Nur bei Bedarf aktivieren.
- Diagnose-ZIPs enthalten Zeitpunkte und Betriebszustände. App-/Supervisor-Logs können zusätzlich Geräteadressen, Messwerte und Fehlermeldungen enthalten. Auch die reduzierte Historie kann in Status-Fehlertexten lokale Details enthalten. Vor jedem Teilen prüfen und auf einen kurzen relevanten Ausschnitt reduzieren.
- Vollständige Bluetooth-HCI-Mitschnitte können Schlüssel und Daten anderer Geräte enthalten; sie gehören nicht in dieses Repository.
- Keine Sicherheitsgarantie und keine zugesagte Reaktionszeit. Experimenteller Community-Support für den aktuellen Quellstand.
