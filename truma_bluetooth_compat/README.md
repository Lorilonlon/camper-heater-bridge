# Bluetooth-Kompatibilität (experimentell)

Nur für klassische iNet-Boxen mit dem beobachteten Timing-Problem beim Aufbau einer verschlüsselten Bluetooth-Verbindung. Kein allgemeiner BlueZ-Patch und keine Unterstützung für iNet X.

In `box_address` dieselbe eigene Box-Adresse wie in der Bridge eintragen. Ohne gültige Adresse startet diese App nicht. Der Zielwert wird über eine geprüfte Konfiguration an die Bibliothek übergeben; keine persönliche Geräteadresse ist eingebaut.

Die Bibliothek verzögert nur eine BT_SECURITY-Anhebung von LOW auf mindestens MEDIUM, wenn ein ATT-Socket (CID 4) zur konfigurierten Box gehört. Anschließend wird der ursprüngliche Systemaufruf mit denselben Parametern ausgeführt. Schlüssel werden weder gelesen noch geändert. Alle anderen Gegenstellen bleiben außerhalb dieser Bedingung. Die Wartezeit blockiert den gemeinsamen Bluetooth-Dienst kurz; deshalb sind andere Geräte kurzzeitig von Verzögerungen betroffen.

Die App schreibt ausschließlich ihren markierten Laufzeit-Override `/run/systemd/system/bluetooth.service.d/90-truma-inet-timing.conf`, legt ihre Dateien unter `/share/truma-inet-compat` ab und startet den Bluetooth-Dienst neu. Fremde Overrides oder fremde LD_PRELOAD-Einstellungen werden nicht überschrieben. Benötigt Host-D-Bus und einen beschreibbaren Share-Ordner; diese Berechtigungen sind weitreichend.

Stoppen entfernt den eigenen Override und startet den ursprünglichen Bluetooth-Dienst neu. Vor Deinstallation zuerst regulär stoppen. Bei hartem Prozessabbruch kann der Laufzeit-Override bis zur nächsten Rücknahme oder einem Host-Neustart bestehen bleiben. Die Bibliothek nicht löschen, solange der Override aktiv ist. Normales Stoppen/Starten wurde in der früheren Inbetriebnahme geprüft; die neue konfigurierbare Variante muss nach Installation erneut beobachtet werden.

Acht C-Prüffälle werden beim Linux-Container-Build ausgeführt: nur die Zieladresse und Sicherheitsanhebung verzögern, andere Adresse/verschlüsselter Socket/Peerfehler/anderer Sockettyp/niedrige Sicherheitsstufe werden unverändert durchgereicht, fehlende oder ungültige Konfiguration verzögert nichts. Bisher auf aarch64 ausgelegt.
