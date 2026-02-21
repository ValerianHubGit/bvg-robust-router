# 🚇 BVG Robust Router

**Nicht die schnellste – die zuverlässigste Verbindung.**

Ein Python-Projekt das Verbindungen im Berliner ÖPNV nicht nach Fahrtzeit, sondern nach **Robustheit** bewertet und sortiert. Entwickelt als Portfolio-Projekt mit Fokus auf saubere Softwarearchitektur, API-Integration und mathematisch motiviertem Scoring.

---

## Motivation

Wer in Berlin täglich Bahn fährt, kennt das Problem: Die schnellste Verbindung ist oft die riskanteste. Ein Umstieg mit zwei Minuten Puffer, eine Linie mit häufigen Verspätungen – und der Abend ist ruiniert.

Standardmäßige Routenplaner optimieren auf Fahrtzeit. Dieser Router optimiert auf **Zuverlässigkeit**.

---

## Funktionsweise

### Robustheitsscore

Jede Verbindung erhält einen Score nach folgender Formel:

$$R(J) = w_1 \cdot T + w_2 \cdot \sum_{i} \frac{1}{\max(p_i, 1)} + w_3 \cdot n$$

| Variable | Bedeutung |
|----------|-----------|
| $T$ | Gesamtdauer der Journey in Minuten |
| $p_i$ | Pufferzeit in Minuten an echtem Umstieg $i$ |
| $n$ | Anzahl echter Umstiege |
| $w_1 = 0.3$ | Gewicht Gesamtdauer |
| $w_2 = 4.0$ | Gewicht Umstiegsrisiko |
| $w_3 = 8.0$ | Gewicht Anzahl Umstiege |

**Intuition:** Kurze Pufferzeiten bestrafen überproportional – $\frac{1}{p_i}$ divergiert für $p_i \to 0$. Fußwege und Verbindungen ohne Umstieg gehen nicht in die Risikosumme ein. Ein niedriger Score bedeutet eine robustere Verbindung.

---

## Architektur

```
bvg-robust-router/
├── src/
│   ├── api/
│   │   ├── bvg_client.py   # BVG-REST-API Wrapper
│   │   └── models.py       # Dataclasses: Stop, Connection, Journey
│   ├── graph/
│   │   ├── robustness.py   # Scoring-Funktion
│   │   └── router.py       # Sortierung nach Score
│   └── ui/
│       └── app.py          # Streamlit Interface
└── tests/
```

### Designentscheidungen

**Keine eigene Graphtraversierung:** Die BVG-REST-API liefert fertige Journeys – ein eigener Dijkstra-Algorithmus über einen vollständigen Berliner Netzgraphen würde Millionen von API-Calls erfordern und keinen Mehrwert liefern. Stattdessen bewerten und sortieren wir die API-Antworten mit einem mathematisch fundierten Score. Diese Entscheidung ist bewusst und dokumentiert.

**Dataclasses statt rohen Dicts:** Alle API-Antworten werden sofort in typisierte Dataclasses (`Stop`, `Connection`, `Journey`) übersetzt. Das macht den Code lesbar, testbar und erweiterbar.

**Fußwege als eigener Verbindungstyp:** Legs ohne `tripId` werden als `"walking"` markiert und gehen nicht in den Umstiegsrisiko-Score ein.

---

## Installation

```bash
# Repository klonen
git clone https://github.com/ValerianHubGit/bvg-robust-router.git
cd bvg-robust-router

# Virtuelle Umgebung erstellen
python3 -m venv .venv
source .venv/bin/activate

# Abhängigkeiten installieren
pip install -r requirements.txt

# App starten
PYTHONPATH=. streamlit run src/ui/app.py
```

Kein API-Key erforderlich – die [BVG-REST-API](https://v6.bvg.transport.rest) ist öffentlich zugänglich.

---

## Verwendete Technologien

| Paket | Zweck |
|-------|-------|
| `requests` | HTTP-Calls zur BVG-REST-API |
| `streamlit` | Web-Interface |
| `dataclasses` | Typisierte Datenmodelle |
| `datetime` | Zeitstempel-Parsing (ISO 8601) |

---

## Bekannte Limitierungen & geplante Erweiterungen

**Aktuelle Limitierungen:**
- Die öffentliche BVG-API ist instabil und kann 500/503-Fehler zurückgeben
- Maximal ~6 Verbindungen pro Abfrage (API-seitige Begrenzung)
- Historische Verspätungsdaten stehen über diese API nicht zur Verfügung – der Score basiert auf Echtzeit-Struktur, nicht auf statistischen Verspätungsraten

**Geplante Erweiterungen:**
- **Alternative Umstiegswege:** An Umstiegspunkten der initialen Journeys Sub-Abfragen schalten und eigene Journeys aus den besten Teilstrecken zusammenbauen – dies würde echter Robustheitsoptimierung deutlich näher kommen
- **Kartenansicht:** Folium-Integration zur visuellen Darstellung der Route
- **Historische Verspätungsgewichtung:** Sobald entsprechende Daten verfügbar sind, Linien-spezifische Verspätungswahrscheinlichkeiten in den Score integrieren
- **Statistisch fundierter Robustheitsscore:** Erweiterung zu einem echten Erwartungswert der Verspätung unter Berücksichtigung nicht-Markovscher Zustandsabhängigkeiten

---

## Autor

**Valerian Kurowski** – M.Sc. Mathematik, TU Berlin  
[GitHub](https://github.com/ValerianHubGit)
