# Änderungen

## Bridge 0.1.8

- Begrenzte lokale Verbindungshistorie mit Zustandswechseln, Fehlertypen, Systemdruck und Fünf-Minuten-Status.
- ZIP-Download der Diagnosehistorie ausschließlich über die geschützte Bridge-Weboberfläche.
- Zeitüberschreitungen werden als TimeoutError angezeigt, statt mit leerer Fehlermeldung.
- Keine Funkpakete, Schlüssel, Steuerbefehle oder automatischen Neustarts durch die Diagnose.

## Bridge 0.1.7

- Gemessene Wassertemperatur als eigener Sensor und in der Warmwasserkachel.
- Beschriftete Kacheln: Im Raum, Zieltemperatur, Wassertemperatur und Warmwasserstufe.
- Ausgeschaltete Heizung kennzeichnet den gespeicherten Zielwert als vorgemerkt.
- Sensorvorlagen verarbeiten auch ältere Statusmeldungen ohne neue Messfelder.

## Bridge 0.1.6 / Kompatibilität 0.1.2

- Raumtemperatur und Versorgungsspannung als optionale, reine Lesesensoren.
- Gemessene Temperatur auch als Klima-Istwert mit einer Nachkommastelle und in der Einrichtungsoberfläche.
- Regelmäßige Messwertabfragen werden durch häufige Steuerbefehle nicht verdrängt.
- Messwertausfall liefert unbekannt, ohne die Heizungssteuerung zu sperren.
- Persönliche Geräteadresse durch Konfiguration ersetzt, leere Erstinstallation startet nicht versehentlich gegen ein fremdes Gerät.
- MIT-Lizenz, eigene Protokollnotizen und Installationshinweise ergänzt.
- Tests für Sensoren und acht Linux-C-Fälle der konfigurierbaren Verzögerung.

## Bridge 0.1.4

- Befehle nach langsamem Auslesen erneut auf Aktualität prüfen.
- Fehlgeschlagene MQTT-Veröffentlichungen bleiben wiederholbar.
- aiohttp auf 3.14.3 aktualisiert.

## Bridge 0.1.3

- Sollwertwahl bei ausgeschalteter Heizung bleibt lokal vorgemerkt.

## Bridge 0.1.2

- Warmwasser Aus und Boost ergänzt; reale Betriebsprobe noch offen.
