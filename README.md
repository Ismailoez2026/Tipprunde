# WM-Tipprunde

Diese Version enthält:

- Tippsperre ab Anstoß
- Punkte: 4 exakt / 3 Tordifferenz / 2 Tendenz / 0 sonst
- fremde Tipps erst ab Anstoß sichtbar
- Regeln für alle sichtbar
- Weltmeister-Bonustipp mit 10 Punkten
- Flaggen über Emojis
- mobile Oberfläche
- Adminbereich
- CSV-Import für Spiele
- Render/GitHub-ready

## Lokal starten

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 Tipprunde.py
```

Dann aufrufen:

```text
http://127.0.0.1:5000
```

Optional Demo-Daten anlegen:

```text
http://127.0.0.1:5000/init-db
```

## Admin

Standardmäßig ist der Admin-Code:

```text
admin123
```

## CSV-Import

CSV-Spalten:

```text
home_team,away_team,kickoff,stage,group_name
```

Beispiel:

```csv
home_team,away_team,kickoff,stage,group_name
Deutschland,Frankreich,2026-06-12 21:00,Gruppenphase,A
Brasilien,Spanien,2026-06-13 18:00,Gruppenphase,B
Argentinien,Portugal,2026-06-14 20:00,Achtelfinale,
```
