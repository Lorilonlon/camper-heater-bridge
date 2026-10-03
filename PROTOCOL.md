# Schnittstellenbeschreibung zur unabhängigen Interoperabilität

Diese Notizen beschränken sich auf die für die implementierten Funktionen erforderlichen Schnittstelleninformationen. Herkunft und rechtliche Grenzen: LEGAL.md. Keine Original-App-Dateien, dekompilierten Klassen oder vollständigen Herstellerdatenbanken sind enthalten.

Keine festen ATT-Handles verwenden. Die Zuordnung erfolgt über Service- und Characteristic-UUID. Bytefolgen und Messwerte unten sind technische Beispiele ohne Geräteadresse, Schlüssel oder Personenbezug.

| Funktion | Service | Characteristic | Nutzdaten |
|---|---|---|---|
| Gemessene Raumtemperatur | 00000000-0003-0001-0000-0000fe088214 | 00000001-0003-0001-0000-0000fe088214 | UInt16 LE, Rohwert / 10 − 273 °C |
| Gemessene Wassertemperatur | gleicher Messdienst | 00000003-0003-0001-0000-0000fe088214 | UInt16 LE, Rohwert / 10 − 273 °C |
| Versorgungsspannung | gleicher Messdienst | 00000004-0003-0001-0000-0000fe088214 | UInt16 LE, Rohwert / 10 V |
| Heiz-Sollwert | 00010000-0004-0001-0000-0000fe088214 | 00010001-0004-0001-0000-0000fe088214 | UInt16 LE, (°C + 273) × 10; Null schaltet aus |
| Gebläse | gleicher Heizdienst | 00010002-0004-0001-0000-0000fe088214 | Aus 0, Eco 1, High 10 |
| Warmwasser | gleicher Heizdienst | 00010004-0004-0001-0000-0000fe088214 | UInt16 LE: Aus 0, Niedrig 3130, Hoch 3330, Boost 4730 |


## Herkunft und Evidenz

- Service-/Characteristic-Zuordnung und zahlreiche Lese-/Schreibwerte wurden im Bluetooth-Verkehr der Original-App an der Betreiberanlage beobachtet. Die Implementierung verwendet UUID-Discovery statt aufgezeichneter Handle-Nummern.
- Heiz-Sollwerte 19/30 °C, Ausschalten und Warmwasser Niedrig/Hoch wurden beobachtet. Die Bridge las 19 °C und Ausschalten nach eigenen Befehlen zurück. Der übrige ganzzahlige Heizbereich 5–30 °C folgt dem ermittelten Format; nicht jede Kombination wurde physisch getestet.
- Warmwasser Aus/Boost stammen aus den für Combi 6 relevanten Moduswerten der untersuchten App-Gerätedaten. Ein vollständiges Original-Datenobjekt wird nicht veröffentlicht. Diese beiden Modi wurden noch nicht physisch bestätigt. Boost ist ein Moduskennwert, keine reale Temperatur.
- Raumtemperatur- und Spannungskanal wurden zusätzlich mit Statuswerten der Anlage plausibilisiert; der Wasserkanal wurde durch einen separaten Statusabruf bestätigt. Das ist keine Kalibrierung oder Genauigkeitszusage über den gesamten Messbereich.

## Rechenbeispiele und Grenzen

`bc 0b` entspricht als UInt16 LE dem Wert 3004 und ergibt nach dem ermittelten Geräteformat 27,4 °C. `34 0d` entspricht 3380 und ergibt 65 °C. `86 00` entspricht 134 und ergibt 13,4 V. Der Offset 273 wird als beobachtetes Geräteformat verwendet, nicht als allgemeine physikalische Definition der Kelvin-Skala.

Fehlende, falsch lange, Null-/65535- und außerhalb des vorgesehenen Plausibilitätsbereichs liegende Messwerte werden als unbekannt behandelt. Messwerte haben keinen Schreibpfad; ihr Ausfall sperrt die Grundsteuerung nicht automatisch. Ein Heiz-Sollwert ungleich Null schaltet auf Geräteebene zugleich die Heizung ein. Deshalb speichert die Bridge Temperaturänderungen bei ausgeschalteter Heizung zunächst lokal.

Kein Nachweis des tatsächlichen Brennerbetriebs, keine Rekonstruktion von Firmware oder Sicherheitslogik und keine Kompatibilitätszusage für iNet X oder andere Gerätekombinationen.
