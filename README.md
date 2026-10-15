# Komplexitäts-Framework Pro – Masterarbeit

Interaktive, deutschsprachige Streamlit-Anwendung zur transparenten Methodenauswahl und wirtschaftlichen Anschlussprüfung.

## Funktionsumfang

- Acht Methodenprofile **M1–M8** aus der Method Coding Matrix der bereitgestellten Abschlussarbeit: DS, MRL, OUT, ES, Framework-Lens.
- **Stufe A:** Prüfung der Daten-Signatur und des Informationsreifegrads (MRL 1–4).
- **Stufe B:** Fachliche Eignungsbestätigung für den konkreten Anwendungsfall (bewusst manuell).
- **Stufe C:** Wirtschaftliche Anschlussprüfung nach Kapitel 5: B1 Wirkungsbrücke, B2 Ressourcenbrücke, B3 Bewertungsbrücke.
- Ressourcen **R1–R6**, Anschlussdistanz **A1–A4**, Daten **U** (Verbrauch) und **K** (Kostensatz), Status **W0–W2**.
- Vergleich frei definierter Szenarien **V0/V1/V2**, Tabellen, Diagramm, JSON-Prüfbericht und CSV-Methodenmatrix.
- Tests für Zulassung und wirtschaftliche Reife.

## Schnellstart (lokal)

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Tests: `python -m pytest -q`.

## GitHub / Streamlit Community Cloud

1. Neues GitHub-Repository erstellen.
2. Dateien aus diesem Ordner ins Repository hochladen (inklusive `methods.json`, `engine.py`, `app.py`, `requirements.txt` und `.streamlit/config.toml`).
3. In Streamlit Community Cloud **New app** wählen, GitHub-Repository verbinden und als Entry point `app.py` eintragen.

## Wissenschaftliche Grenzen

Die acht Methoden sind **Profile zur Auswahl**, keine nachimplementierten wissenschaftlichen Originalalgorithmen. Die App behauptet keine Berechnung von Hinckley, Ben-Arieh usw. Methodencodes sind eine thesis-spezifische Klassifikation, nicht eine offizielle Norm. Die Daten-Signaturen und MRL-Werte stammen aus der bereitgestellten Method Coding Matrix und sind vor einer produktiven Anwendung gegen Primärquellen zu prüfen. `V0–V2` sind in dieser Anwendung frei definierbare Vergleichsszenarien; eine abweichende Bedeutung im Text der Abschlussarbeit muss separat harmonisiert werden. Die Stufen W0/W1/W2 setzen B1/B2 voraus und vermeiden ausdrücklich erfundene Eurobeträge. W2 berechnet ausschließlich U × K für dokumentierte Annahmen.

Keine Speicherung auf einem Server; Daten verbleiben in der laufenden Streamlit-Sitzung, bis ein Bericht heruntergeladen wird.
