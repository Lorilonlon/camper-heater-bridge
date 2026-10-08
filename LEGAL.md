# Herkunft, Rechte und Grenzen

Stand der Prüfung: 03.10.2026. Dieses Dokument beschreibt den Veröffentlichungsumfang und eine vorsichtige Einordnung nach deutschem/EU-Recht. Es ist weder eine anwaltliche Freigabe noch eine Zusicherung für jedes Land, jeden Vertrag oder jeden Einsatzzweck.

## Eigener Code und Schnittstellenwissen

Dieses Repository enthält die eigenständige Implementierung einer lokalen Schnittstelle. Die Entwicklung nutzte Beobachtungen des Bluetooth-Verkehrs an einer eigenen Anlage sowie die Untersuchung der Android-App. Einzelne Moduswerte stammen aus dafür relevanten App-Gerätedaten. Daher wird ausdrücklich **keine Clean-Room-Entwicklung ohne Kenntnis der Original-App** behauptet.

Veröffentlicht werden eigener Quellcode und die für seine Interoperabilität notwendigen UUIDs, Datenformate und Moduswerte. Nicht veröffentlicht werden Original-App/APK/XAPK, dekompilierte Klassen, vollständige Hersteller-Gerätedatenbanken, Firmware, Logos, Handbuchkopien, Rohmitschnitte, Schlüssel oder persönliche Gerätekonfigurationen. `PROTOCOL.md` trennt beobachtete Werte, Ableitungen und noch nicht physisch bestätigte Modi.

Der Betreiber hat am 03.10.2026 erklärt, dass für ihn keine besondere Geheimhaltungs- oder Entwicklervereinbarung mit Truma besteht. Das ersetzt nicht die Prüfung der eigenen Nutzungsberechtigung und etwaiger sonstiger Vertragsbedingungen. Ein Bezug aus einem APK-Archiv allein beweist keine Berechtigung. Diese tatsächlichen Voraussetzungen sind vom Herausgeber vor Veröffentlichung zu klären.

## Rechtliche Einordnung der Untersuchung

- [§ 69a Abs. 2 UrhG](https://www.gesetze-im-internet.de/urhg/__69a.html) unterscheidet geschützte Ausdrucksformen von den zugrunde liegenden Ideen und Grundsätzen. Daraus folgt keine pauschale Freigabe beliebiger fremder Dateien oder Datenbanken.
- [§ 69d Abs. 3 UrhG](https://www.gesetze-im-internet.de/urhg/__69d.html) erlaubt einem zur Nutzung Berechtigten bestimmte Beobachtungen und Tests im Rahmen erlaubter Nutzungshandlungen.
- [§ 69e UrhG](https://www.gesetze-im-internet.de/urhg/__69e.html) stellt zusätzliche Bedingungen an notwendige Dekompilierung für Interoperabilität. Dazu gehören Berechtigung, fehlende leichte Verfügbarkeit der nötigen Informationen und Beschränkung auf notwendige Teile. Auch die Weitergabe gewonnener Informationen ist begrenzt. Der Interoperabilitätszweck allein genügt deshalb nicht als pauschale Rechtfertigung.
- [§ 3 GeschGehG](https://www.gesetze-im-internet.de/geschgehg/__3.html) enthält Erlaubnistatbestände für eigenständige Erkenntnisse und bestimmte Untersuchungen; Besitz-, Zugänglichkeits- und Vertragssituation sind dabei zu berücksichtigen.

Für die Veröffentlichung wird der Umfang auf die benötigte Schnittstelle reduziert. Bei Zweifeln an Berechtigung, Vertragsbedingungen oder Umfang der früheren Untersuchung ist eine individuelle Prüfung durch einen im IT-/Urheberrecht tätigen Rechtsanwalt erforderlich. Keine Behauptung, eine solche Prüfung habe stattgefunden.

## Marken und Auffindbarkeit

**Camper Heater Bridge** ist der Projektname. Truma, iNet-Box und Combi werden beschreibend verwendet, um die kompatible Herstellerhardware eindeutig zu benennen. „Home Assistant“ beschreibt die Zielplattform. Es besteht keine Herstellerfreigabe, Partnerschaft oder offizielle Unterstützung. Die jeweiligen Kennzeichenrechte verbleiben bei ihren Inhabern; es werden keine Markenlizenzen erteilt.

[§ 23 MarkenG](https://www.gesetze-im-internet.de/markeng/__23.html) lässt bestimmte identifizierende und beschreibende Benutzungen unter den dort genannten Voraussetzungen zu. Ein Disclaimer allein macht nicht jede Gestaltung zulässig. Deshalb verwendet das Projekt keine Herstellerlogos, kein nachgebildetes App-Design und keine Aussagen wie „offiziell“ oder „zertifiziert“. Titel und Suchbegriffe dürfen die tatsächliche Kompatibilität sachlich benennen. Eine eigene Markenrecherche für „Camper Heater Bridge“ wurde nicht durchgeführt.

## Lizenz und Verteilung

Der eigene Projektcode bleibt unter MIT; bestehende Copyright-Hinweise bleiben erhalten. Die MIT-Lizenz erfasst keine fremden Marken, Herstellerprogramme, Patente oder Bibliotheken. Details stehen in `THIRD_PARTY.md`.

Der vorbereitete Release enthält ausschließlich Quellcode. Er veröffentlicht keine gebauten Container, Wheels, ausführbaren Dateien oder Shared Libraries. Insbesondere sind beim späteren Weitergeben der mit BlueZ-Headern gebauten Kompatibilitätsbibliothek deren Lizenzbedingungen gesondert zu bewerten und zu erfüllen. Ein reiner MIT-Hinweis wäre keine ausreichende Kennzeichnung aller Fremdbestandteile.

## Sicherheit und Haftung

Der Hinweis „Nutzung auf eigene Gefahr und Verantwortung“ macht den experimentellen Stand und die Verantwortung für Installation und Bedienung deutlich. Er ist kein pauschaler Ausschluss jeder Haftung. Insbesondere bleiben zwingende Haftung für Vorsatz, grobe Fahrlässigkeit, schuldhaft verursachte Schäden an Leben, Körper oder Gesundheit sowie sonstige unabdingbare gesetzliche Ansprüche unberührt. Das deutsche Recht begrenzt Haftungsausschlüsse unter anderem in [§ 276 Abs. 3 BGB](https://www.gesetze-im-internet.de/bgb/__276.html) und, soweit AGB-Recht anwendbar ist, [§ 309 Nr. 7 BGB](https://www.gesetze-im-internet.de/bgb/__309.html). Die konkrete rechtliche Wirkung hängt vom Einzelfall ab; dieser Hinweis ist keine anwaltlich geprüfte Vertragsklausel.

Die MIT-Lizenz enthält die übliche Gewährleistungs- und Haftungsklausel. Ihre Reichweite hängt vom anwendbaren Recht ab; zwingende gesetzliche Rechte werden dadurch nicht automatisch ausgeschlossen. Es gibt keine Aussage zu Produktsicherheits-, CE- oder sonstiger regulatorischer Konformität und keinen Anspruch auf Herstellergewährleistung für Folgen einer Fremdsteuerung. Bei kommerziellem Angebot oder Vertrieb von vorkonfigurierter Hardware ist eine neue rechtliche und technische Bewertung nötig.

Rückgelesene Sollwerte belegen nicht den sicheren Betrieb des Brenners. Herstelleranweisungen und Sicherheitseinrichtungen bleiben maßgeblich. Nutzung nur mit Anlagen und Konten, zu deren Steuerung die nutzende Person berechtigt ist.
