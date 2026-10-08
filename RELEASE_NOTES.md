# v0.1.8 — erster experimenteller Quellcode-Pre-Release

> [!WARNING]
> **Experimentelle Software – Nutzung auf eigene Gefahr und Verantwortung.**
>
> Dies ist ein privates Community-Projekt zur Steuerung einer echten Heizung und Warmwasseranlage, kein vom Hersteller freigegebenes Produkt. Fehler, Verbindungsabbrüche, falsche Anzeigen und unerwartete Schaltvorgänge sind möglich. Fehlbedienung oder Fehlfunktionen können Personen verletzen oder Sachschäden verursachen, etwa durch Brand, Überhitzung oder Frost.
>
> Prüfe die Eignung für deine Anlage selbst, teste Änderungen vor Ort unter Aufsicht und halte dich an die Herstelleranweisungen. Sicherheitseinrichtungen dürfen nicht umgangen werden. Verlasse dich für Frostschutz oder andere sicherheitsrelevante Aufgaben nicht allein auf diese Software oder das Dashboard. Bei unerwartetem Verhalten die Bridge stoppen und die Anlage nach Herstelleranleitung lokal bedienen.
>
> Die Software wird gemäß MIT-Lizenz ohne Zusicherung von Fehlerfreiheit, Zuverlässigkeit oder Eignung bereitgestellt. Zwingende gesetzliche Haftung bleibt unberührt; „auf eigene Gefahr“ bedeutet keinen vollständigen Haftungsausschluss. Siehe [Sicherheit und Haftung](https://github.com/Lorilonlon/truma-home-assistant-bridge/blob/main/LEGAL.md#sicherheit-und-haftung).

Camper Heater Bridge verbindet eine klassische Truma iNet-Box lokal über Bluetooth und MQTT mit Home Assistant. Enthalten sind Heizungs-/Warmwassersteuerung, separate Temperatur- und Spannungssensoren, Kopplungsoberfläche und beschriftete Dashboard-Karten.

Getestete Betreiberanlage: Raspberry Pi 4, klassische iNet-Box HW 1.3.0 / FW 3.1.5 und Combi 6. Der Betreiber meldet am 03.10.2026 problemlosen Betrieb nach der Alltagserprobung. Keine generelle Kompatibilitäts- oder Dauerbetriebszusage. iNet X wird nicht unterstützt.

**Offen:** frische Installation aus GitHub, vollständiger Host-Neustart, physische Bestätigung der Warmwassermodi Aus und Boost. Die optionale Bluetooth-Kompatibilität 0.1.2 bleibt experimentell und greift in den gemeinsamen Systemdienst ein. Bei der Erprobung trat ein nicht abschließend erklärter Verbindungsfehler auf; daher kein Stable-Release.

Eigener Code: MIT. Fremdlizenzen: THIRD_PARTY.md. Unabhängiges Community-Projekt ohne Herstellerfreigabe. Dieser Release enthält keine Original-App, Firmware, privaten Mitschnitte, vorgefertigten Container oder Shared Libraries.

Bestehende lokale Installationen werden nicht automatisch in ein GitHub-Repository migriert. Die internen Slugs und Entity-IDs bleiben im Quellstand erhalten, der Repository-Präfix unterscheidet sich jedoch. README beachten.

## KI-Mitwirkung

Entwicklung, Tests, Dokumentation und Vorbereitung dieses Releases wurden maßgeblich mit OpenAI Codex erarbeitet. Lorilonlon hat Anforderungen vorgegeben und die reale Anlage erprobt. Die KI-gestützt erstellten Tests sind keine unabhängige Sicherheitsprüfung. Einzelheiten: AI_DISCLOSURE.md.

## Automatisierte Prüfung

GitHub-CI erfolgreich mit Python 3.13 und 3.14 sowie den acht Linux-C-Prüffällen. Dateiprüfung und Testdefinitionen stehen im Repository; keine unabhängige Auditierung.

## Hinweis zur Repository-Umbenennung (08.10.2026)

Neue Adresse: https://github.com/Lorilonlon/truma-home-assistant-bridge. Bei bereits installierten Apps den bisherigen Home-Assistant-Repository-Eintrag zunächst beibehalten; eine neue Adresse kann eine separate App-Installation erzeugen. Details stehen in der [aktuellen README](https://github.com/Lorilonlon/truma-home-assistant-bridge#bereits-%C3%BCber-github-installiert). Dieser Dokumentationshinweis ändert weder den Release-Tag noch den Steuerungscode.
