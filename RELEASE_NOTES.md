# v0.1.8 — erster experimenteller Quellcode-Pre-Release

Camper Heater Bridge verbindet eine klassische Truma iNet-Box lokal über Bluetooth und MQTT mit Home Assistant. Enthalten sind Heizungs-/Warmwassersteuerung, separate Temperatur- und Spannungssensoren, Kopplungsoberfläche, beschriftete Dashboard-Karten und eine begrenzte Diagnosehistorie.

Getestete Betreiberanlage: Raspberry Pi 4, klassische iNet-Box HW 1.3.0 / FW 3.1.5 und Combi 6. Der Betreiber meldet am 03.10.2026 problemlosen Betrieb nach der Alltagserprobung. Keine generelle Kompatibilitäts- oder Dauerbetriebszusage. iNet X wird nicht unterstützt.

**Offen:** frische Installation aus GitHub, vollständiger Host-Neustart, physische Bestätigung der Warmwassermodi Aus und Boost. Die optionale Bluetooth-Kompatibilität 0.1.2 bleibt experimentell und greift in den gemeinsamen Systemdienst ein. Bei der Erprobung trat ein nicht abschließend erklärter Verbindungsfehler auf; daher kein Stable-Release.

Eigener Code: MIT. Fremdlizenzen: THIRD_PARTY.md. Unabhängiges Community-Projekt ohne Herstellerfreigabe. Dieser Release enthält keine Original-App, Firmware, privaten Mitschnitte, vorgefertigten Container oder Shared Libraries.

Bestehende lokale Installationen werden nicht automatisch in ein GitHub-Repository migriert. Die internen Slugs und Entity-IDs bleiben im Quellstand erhalten, der Repository-Präfix unterscheidet sich jedoch. README beachten.

## KI-Mitwirkung

Entwicklung, Tests, Dokumentation und Vorbereitung dieses Releases wurden maßgeblich mit OpenAI Codex erarbeitet. Lorilonlon hat Anforderungen vorgegeben und die reale Anlage erprobt. Die KI-gestützt erstellten Tests sind keine unabhängige Sicherheitsprüfung. Einzelheiten: AI_DISCLOSURE.md.

## Automatisierte Prüfung

GitHub-CI erfolgreich mit Python 3.13 und 3.14 sowie den acht Linux-C-Prüffällen. Dateiprüfung und Testdefinitionen stehen im Repository; keine unabhängige Auditierung.
