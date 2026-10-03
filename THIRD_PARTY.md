# Fremdsoftware und Lizenzumfang

Der eigene Quellcode steht unter MIT. Die nachfolgenden Bibliotheken werden beim lokalen Build installiert; ihre Programmdateien sind nicht Bestandteil des Quellcode-Archivs. Ihre eigenen Copyright-, Lizenz- und gegebenenfalls NOTICE-Dateien dürfen bei Weiterverteilung nicht entfernt oder unter MIT umetikettiert werden.

| Bestandteil | Version / Bezug | Lizenzhinweis |
|---|---|---|
| dbus-next | 0.2.3, [PyPI](https://pypi.org/project/dbus-next/0.2.3/) | MIT |
| aiohttp | 3.14.3, [PyPI](https://pypi.org/project/aiohttp/3.14.3/) | Paketmetadaten: Apache-2.0 AND MIT; einschließlich fremder Parserbestandteile |
| paho-mqtt | 2.1.0, [Originalhinweis](https://github.com/eclipse-paho/paho.mqtt.python/blob/v2.1.0/LICENSE.txt) | EPL-2.0 oder EDL-1.0 laut dualer Lizenzierung; nicht MIT |
| Python | Basisimage Python 3.13 | PSF-Lizenz und enthaltene Fremdkomponenten; konkrete Image-Version prüfen |
| Alpine Linux / musl / Systempakete | Alpine 3.22 aus den Dockerfiles | Jeweilige Paketlizenzen; kein einheitliches MIT-Image |
| BlueZ-Entwicklungsheader | `bluez-dev` beim Kompatibilitäts-Build | Die geprüften Header `lib/bluetooth.h` und `lib/l2cap.h` tragen GPL-2.0-or-later; nicht pauschal LGPL |

Quellen zu den Headern: [bluetooth.h, BlueZ 5.82](https://github.com/bluez/bluez/blob/5.82/lib/bluetooth.h), [l2cap.h, BlueZ 5.82](https://github.com/bluez/bluez/blob/5.82/lib/l2cap.h). Der Paketmanager kann beim Build eine andere Patchversion auflösen; deren tatsächliche Hinweise sind ebenfalls zu prüfen. Das Projekt liefert diese Header nicht mit. Die beim Build verwendeten Inline-Funktionen/Makros und eine spätere Weitergabe des gebauten Shims sind lizenzrechtlich nicht allein durch die MIT-Lizenz des eigenen C-Quelltextes abgedeckt. Keine Zusicherung, dass ein daraus gebautes Binary ausschließlich unter MIT verteilt werden darf.

## Umfang dieser Veröffentlichung

Nur eigener Quellcode, Buildrezepte, Tests und Dokumentation werden veröffentlicht. Kein GHCR-/Docker-Hub-Push und keine Binär-Release-Assets sind eingerichtet. Der Build erfolgt lokal beim Nutzer. Die Lizenzprüfung behauptet keine vollständige Freigabe künftig gebauter Container.

`DEPENDENCIES.json` dokumentiert die Python-Paketmetadaten der isolierten Testauflösung vom 03.10.2026. Das ist eine Momentaufnahme auf dem Testrechner, keine vollständige Container-SBOM. Transitive Pakete sind derzeit nicht vollständig festgeschrieben; Basisimage-Tags sind ebenfalls beweglich. Ein späterer Linux-/Container-Build kann andere transitive Versionen enthalten.

Vor Verteilung fertiger Images oder Bibliotheken: tatsächlich aufgelöste Pakete und Header erfassen, vollständige Original-Lizenz-/NOTICE-Texte erhalten, gegebenenfalls erforderlichen korrespondierenden Quellcode einschließlich Buildanweisungen bereitstellen und Lizenzkompatibilität prüfen. Externe Quell-Links allein ersetzen solche Pflichten nicht automatisch.

Keine Herstellerprogramme, Herstellerbilder oder dekompilierten Dateien werden mitgeliefert. Die MIT-Copyright-Zeilen bezeichnen die Rechte am eigenen Code, nicht die Rechte von Truma, Home Assistant oder den Bibliotheksautoren.
