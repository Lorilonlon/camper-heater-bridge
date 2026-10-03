# Beiträge

Beiträge bitte als kleine nachvollziehbare Pull Requests mit Beschreibung und passenden Tests einreichen. Mit einem Beitrag ist zu bestätigen, dass du ihn einreichen und unter der bestehenden MIT-Lizenz bereitstellen darfst. Fremde Lizenz- und Copyright-Hinweise erhalten; kein pauschales Umlizenzieren.

Keine Original-APKs, dekompilierten Klassen, kopierten Herstellertexte/-bilder, privaten Konfigurationen oder Rohmitschnitte beilegen. Neue Schnittstellenwerte auf das zur Interoperabilität erforderliche Maß beschränken und ihre Herkunft sowie den Evidenzgrad sachlich dokumentieren. Keine Clean-Room-Behauptung ohne entsprechende Entwicklungsmethode.

Vor einem Pull Request:

```sh
python -m pip install -r truma_inet_bridge/requirements.txt
PYTHONPATH=truma_inet_bridge python -m unittest discover -s tests -v
python scripts/check_release.py
```

Die C-Tests benötigen Linux mit BlueZ-Entwicklungsheadern; der GitHub-Workflow prüft sie. Reale Heiz-/Warmwassertests nur bewusst und unter geeigneten Betriebsbedingungen durchführen. Ein Unit-Test ist keine Freigabe einer Hardwarekombination.

Wesentliche KI-Mitwirkung bitte im Pull Request nennen. Sie ist zulässig, ersetzt aber keine Prüfung von Herkunft, Rechten, Tests und fachlicher Richtigkeit. Keine erfundenen menschlichen Autoren oder Audit-Angaben.
