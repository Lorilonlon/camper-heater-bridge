# Camper Heater Bridge – Truma iNet für Home Assistant

Unabhängiges Community-Projekt, nicht von Truma unterstützt.

Local Bluetooth/MQTT integration for the classic Truma iNet Box and Home Assistant. Independent community project, not affiliated with or endorsed by Truma or the Home Assistant project.

Inoffizielle lokale Home-Assistant-App für eine klassische **Truma iNet-Box** und eine **Truma Combi 6**: Heizung, Warmwasser, Dashboard und Messwerte ohne Cloud-Steuerung.
Eigenständiges Community-Projekt; keine Verbindung zum Hersteller und keine Freigabe durch Truma. Truma, iNet und Combi werden ausschließlich zur Beschreibung der Kompatibilität genannt. Keine Unterstützung für das andere iNet-X-Protokoll.

## Transparent entwickelt mit KI

Dieses Projekt wurde von **Lorilonlon mit wesentlicher Unterstützung von OpenAI Codex** entwickelt. Der KI-Assistent hat maßgeblich Code, Protokollanalyse, Tests, Dokumentation, Fehlersuche und Veröffentlichungsvorbereitung erarbeitet. Lorilonlon hat Anforderungen und Betriebsentscheidungen vorgegeben sowie die reale Anlage bedient und Rückmeldungen zu den Tests geliefert.

Das ist keine ausschließlich menschliche Entwicklung. Tests und Dokumentation wurden ebenfalls mit KI erstellt und sind deshalb keine unabhängige Prüfung. Es wird keine professionelle Sicherheitsprüfung, anwaltliche Freigabe oder Herstellerzertifizierung behauptet. Grenzen und offene Punkte werden mitveröffentlicht. Mehr dazu in [AI_DISCLOSURE.md](AI_DISCLOSURE.md).

## Erprobungsstand

Vorbereiteter Stand: Bridge 0.1.8, optionale Bluetooth-Kompatibilität 0.1.2. Experimentell. Die bisherige Steuerung wurde auf Raspberry Pi 4 / Home Assistant OS mit klassischer iNet-Box HW 1.3.0, FW 3.1.5 und Combi 6 erprobt; die neuen Messsensoren wurden auf dieser Anlage bereits live ausgelesen. Ein zusätzlicher SMS-Statusabruf bestätigte die Zuordnung der Innentemperatur und die Spannung; eine Kalibrierung über den Messbereich liegt nicht vor. Keine allgemeine Kompatibilitätszusage. Am 03.10.2026 meldete der Betreiber nach der Alltagserprobung einen problemlosen Betrieb. Das ist ein Erfahrungsbericht einer Installation, kein durchgehend ausgewerteter Langzeittest. Am 23.09.2026 war ein Verbindungsfehler aufgetreten; Wiederherstellung erforderte Box-/Bluetooth-Neustarts. Die Ursache wurde nicht abschließend nachgewiesen. Frische Installation aus einem GitHub-Repository und vollständiger Host-Neustart sind noch offen.

## Funktionen

- Lokale Bluetooth-Verbindung mit Kopplungsfenster für genau die konfigurierte Box.
- MQTT Discovery: Raumheizung, Solltemperatur, Eco/High und Warmwasser Aus/Niedrig/Hoch/Boost.
- Bei ausgeschalteter Raumheizung wird der Sollwert nur gespeichert; erst explizites Einschalten sendet ihn. Laufende Heizung übernimmt Temperaturänderungen sofort.
- Gemessene Raumtemperatur als eigener Sensor und als Isttemperatur der Klima-Entität; Versorgungsspannung und gemessene Wassertemperatur als eigene Sensoren.
- Fehlende oder unplausible Messwerte werden als unbekannt behandelt. Keine Schreibzugriffe auf Messkanäle. Keine Ermittlung des tatsächlichen Brennerbetriebs.
- Rücklesen nach Steuerbefehlen; keine automatische Wiederholung nach Verbindungsausfall. Als retained erkennbare MQTT-Befehle werden abgewiesen; die MQTT-3-Einschränkung ist unten beschrieben.
- Ingress-Einrichtungsseite mit Kopplung und zeitlich begrenzter Freigabe für die Handy-App.

## Installation aus GitHub

Repository: **[Lorilonlon/camper-heater-bridge](https://github.com/Lorilonlon/camper-heater-bridge)**.

[Repository in Home Assistant hinzufügen](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2FLorilonlon%2Fcamper-heater-bridge)

In Home Assistant unter **Einstellungen → Apps → App-Store → ⋮ → Repositories** diese Adresse hinzufügen. Dann **Camper Heater Bridge** auswählen. Die beiden Apps werden aus Quellcode lokal gebaut; es gibt keine vorgefertigten Projekt-Images.

Eine bestehende lokale Installation wird durch Hinzufügen des Repositorys **nicht automatisch migriert**. Der Repository-Präfix unterscheidet sich von `local_`. Nicht beide Bridges gleichzeitig starten. Vor einem späteren Wechsel private Optionen und lokale Daten sichern, die bisherige Bridge stoppen und Konfiguration/Kopplung kontrolliert übernehmen. Ein automatischer Migrationspfad ist nicht getestet.

## Installation und Einrichtung

1. Home Assistant OS (getestete Installationsart) mit MQTT-Integration und einem erreichbaren MQTT-Broker bereitstellen. Zugangsdaten privat in den App-Optionen eintragen.
2. Den Ordner `truma_inet_bridge` als lokale App installieren. Auf Home Assistant OS liegt das Verzeichnis in Terminal & SSH je nach Version unter `/addons` oder `/local_apps`. Den lokalen App-Store neu laden.
3. Die eigene Bluetooth-Adresse in `box_address` eintragen, Adapter wählen (meist `hci0`). Es wird keine persönliche Adresse mitgeliefert. Der Adapter muss BLE-Peripheral-Advertising und einen GATT-Server unterstützen; ein gewöhnlicher ESPHome-Bluetooth-Proxy ersetzt ihn nicht.
4. MQTT-Host, Port und nötige Zugangsdaten eintragen. TLS ist standardmäßig aktiv. Bei eigener CA deren öffentliches CA-Zertifikat eintragen; keine privaten Schlüssel. Ohne gültige eigene Box-Adresse startet die App nicht.
5. App starten, Ingress öffnen, Bluetooth auf allen zuvor gekoppelten Handys für die Einrichtung ausschalten und Kopplung starten. Anschließend die Bluetooth-Taste an der iNet-Box drücken. Bestehende Bindungen werden nicht gelöscht.
6. Zunächst im Lesemodus Werte prüfen. `allow_control` nur aktivieren, wenn tatsächlich gesteuert werden soll. Steuerung kann die Heizung physisch einschalten.
7. Für die beschrifteten Kacheln `dashboard/camper-inet-card.js` nach `/config/www/camper-inet-card.js` kopieren und unter Dashboard-Ressourcen `/local/camper-inet-card.js` als JavaScript-Modul registrieren. Falls `www` neu angelegt wurde, kann ein Home-Assistant-Neustart erforderlich sein. Die Karte enthält keine externen Bibliotheken und verwendet die nativen Home-Assistant-Bedienelemente.
8. Das Beispiel `dashboard.json` bei Bedarf über die Dashboard-Oberfläche importieren und die tatsächlich vergebenen Entity-IDs prüfen. Den Einrichtungslink an den installierten App-Slug anpassen; ein späteres Repository vergibt einen anderen Präfix als `local_`.

## Optionaler Bluetooth-Workaround

Nur bei dem dokumentierten Verbindungsproblem: `truma_bluetooth_compat` installieren und dort dieselbe eigene `box_address` eintragen. Diese separate App verändert zur Laufzeit den gemeinsamen Bluetooth-Dienst: vor einer Sicherheitsanfrage an genau diese Box wartet er 800 ms. Verschlüsselung wird nicht abgeschaltet. Andere Bluetooth-Aktionen können währenddessen kurz verzögert werden. Die App benötigt Host-D-Bus und Schreibzugriff auf `/share`; das ist eine weitreichende Berechtigung. Details und Rücknahme im zugehörigen README.

## Grenzen der Messwerte

Die Versorgungsspannung wird an der iNet-Box gemeldet; sie ist kein präziser Batterie-Shunt und kann wegen Leitungsverlusten vom Batteriewert abweichen. Die Raumtemperatur ist ein Messwert der Truma-Anlage, keine aus dem Sollwert abgeleitete Temperatur. Zuordnung und Skalierung sind in `PROTOCOL.md` mit Evidenzgrad dokumentiert. Warmwasser-Aus/Boost wurden anhand der App-Gerätedaten ergänzt und sind noch nicht physisch bestätigt.

## Entwicklung und Tests

Python-Abhängigkeiten: `truma_inet_bridge/requirements.txt`.

```sh
python -m pip install -r truma_inet_bridge/requirements.txt
PYTHONPATH=truma_inet_bridge python -m unittest discover -s tests -v
```

Die Linux-C-Tests laufen beim Build der Kompatibilitäts-App. Keine Original-APK, dekompilierten Klassen, Herstellerbilder oder Bluetooth-Mitschnitte werden benötigt oder mitgeliefert. MQTT-Steuerthemen nur ohne retain verwenden; MQTT-3 kann live weitergeleitete retained-Nachrichten nicht immer als solche kennzeichnen. Der Broker ist eine Vertrauensgrenze.

## Lizenz und Veröffentlichung

Eigener Projektcode: MIT, siehe LICENSE. Abhängigkeiten behalten ihre eigenen Lizenzen; siehe THIRD_PARTY.md. Keine Herstellerrechte oder Markenrechte werden durch diese Lizenz eingeräumt. Die erste Veröffentlichung erfolgt als experimenteller Quellcode-Pre-Release. Noch offene Prüfungen stehen in `RELEASE_CHECKLIST.md`; Herkunft und rechtliche Grenzen in `LEGAL.md`, vertrauliche Fehlermeldungen in `SECURITY.md`.

## Verbindungsdiagnose

Ab Bridge 0.1.8 läuft eine begrenzte lokale Diagnosehistorie automatisch mit. Sie protokolliert Zustandswechsel, Bluetooth-Verbindungsmerkmale, Fehlertypen und alle fünf Minuten einen Status mit letzter bestätigter Rückmeldung. Systemlast und CPU-/Speicher-/I/O-Wartezeiten helfen, Funkprobleme von einem überlasteten Rechner zu unterscheiden. Die Werte beziehen sich auf den Host und können durch andere Apps beeinflusst werden.

In der Bridge-Weboberfläche lässt sich die Historie über **Verbindungsprotokoll herunterladen** als ZIP exportieren. Drei rotierende Dateien unter `/data/diagnostics` belegen zusammen ungefähr höchstens 1,5 MiB; bei Erreichen der Grenze werden die ältesten Einträge ersetzt. Die Historie übersteht einen App-Neustart, aber keine Deinstallation ohne Sicherung. Sie enthält keine Funkpakete, Bluetooth-Schlüssel oder Konfigurations-Zugangsdaten. Zeitpunkte und Betriebszustände sind dennoch persönliche Betriebsdaten; Diagnosearchive nicht in das öffentliche Repository übernehmen.

Das Protokoll löst keine Steuerbefehle oder automatischen Neustarts aus. Ein harter Stromausfall kann nicht unmittelbar protokolliert werden; erkennbar sind die letzte Aufzeichnung und der nächste Start. Es erfolgt keine automatische Benachrichtigung.

## Betrieb und Sicherheit

Die App kann reale Heiz- und Warmwasserfunktionen auslösen. Sie ersetzt keine Sicherheitseinrichtungen, Herstelleranweisungen, Frostschutzüberwachung oder lokale Bedienmöglichkeit. Bei Ausfall bleibt der tatsächliche Gerätezustand maßgeblich; ein nicht verfügbarer Sensor bedeutet nicht „Heizung aus“. Zunächst im Lesemodus erproben und `allow_control` bewusst freigeben. Keine zugesicherte Eignung für unbeaufsichtigten oder sicherheitskritischen Betrieb.

Der optionale Kompatibilitätsdienst greift in den gemeinsamen Bluetooth-Systemdienst ein. Vor seiner Installation die dortigen Hinweise lesen. MQTT-Zugangsdaten nur lokal speichern und Broker-Zugriff begrenzen.
