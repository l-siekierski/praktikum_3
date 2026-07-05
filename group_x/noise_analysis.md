# Noise-Analyse: `eventlog_group_x.xes`

## Vorgehen
Das Event-Log wurde auf Trace-Varianten-Ebene analysiert (Sequenz der `concept:name`-Werte je Case, nur `lifecycle:transition = complete`). Von den **1.100 Traces** verteilen sich alle Fälle auf nur **49 distinkte Varianten** – das reicht, um sauberes Kernverhalten von seltenem/verrauschtem Verhalten zu trennen.

## Ergebnis: Zwei klar getrennte Gruppen

| Gruppe | Varianten | Fälle | Anteil |
| :--- | :---: | :---: | :---: |
| **Hauptvarianten** (>10 Fälle je Variante) | 9 | 1.036 | **94,18 %** |
| **Noise-Varianten** (≤10 Fälle je Variante) | 40 | 64 | **5,82 %** |

### Die 9 Hauptvarianten (das eigentliche Prozessmodell)
1. Standardversand: `Browse & Select Products → Place Order → Validate Order & Check Stock → Receive Confirmation → Process Payment → Pick & Pack Items → Ship Order → Send Tracking Information → Receive Tracking Information` (445 Fälle, 40,45 %)
2. Express-Versand-Variante (187 Fälle, 17,00 %)
3. Großbestellung mit Freigabe (`Approve Bulk Order`) + Standardversand (108 Fälle, 9,82 %)
4. Abbruch wegen fehlendem Lagerbestand (`Notify Out of Stock`) (102 Fälle, 9,27 %)
5. Abgebrochene/unvollständige Fälle nach `Place Order` (52 Fälle, 4,73 %)
6. Zahlungsfehler (`Handle Payment Failure`) (49 Fälle, 4,45 %)
7. Großbestellung + Express-Versand (44 Fälle, 4,00 %)
8. Abgebrochene Großbestellung nach Freigabe (38 Fälle, 3,45 %)
9. Großbestellung + Zahlungsfehler (11 Fälle, 1,00 %)

Diese 9 Varianten bilden ein in sich konsistentes, nachvollziehbares Geschäftsprozessmodell (inkl. Ausnahmepfade wie Zahlungsfehler oder Lagerengpässen).

## Der Noise: drei künstliche Störungstypen

Die verbleibenden 40 Varianten (64 Fälle, 5,82 %) wurden per Editierdistanz (Damerau-Levenshtein) mit der jeweils nächstgelegenen Hauptvariante verglichen. Dabei zeigt sich, dass **jede** Noise-Variante durch **genau eine** der drei klassischen Störungsoperationen aus einer Hauptvariante hervorgeht:

| Noise-Typ | Fälle | Beschreibung | Beispiel |
| :--- | :---: | :--- | :--- |
| **Doppeltes/eingefügtes Event** | 30 | Eine Aktivität wird zusätzlich (meist am Ende) wiederholt | `... → Receive Tracking Information → Receive Tracking Information` |
| **Fehlendes Event (Skip)** | 18 | Eine Aktivität der Standardsequenz fehlt | `Browse & Select Products → Validate Order & Check Stock → ...` (ohne `Place Order`) |
| **Vertauschte Events** | 16 | Zwei benachbarte Aktivitäten sind in der Reihenfolge getauscht | `... → Process Payment → Receive Confirmation → ...` (statt umgekehrt) |

**Gesamt: 64 Fälle / 5,82 % des Logs sind synthetisch verrauscht.**

## Auswirkung auf die Konformitätsprüfung (Bezug zu `results_conformance.md`)

Die im Conformance-Checking dokumentierten **25 Footprint-Abweichungen des Heuristics-Miner-Netzes** wurden gegen die Directly-Follows-Relationen abgeglichen, die *ausschließlich* in den 64 Noise-Traces auftreten (in keiner der 9 Hauptvarianten):

> **Alle 25 von 25 Footprint-Abweichungen (100 %)** lassen sich exakt auf Kanten zurückführen, die nur durch Noise-Traces entstehen (z. B. `Receive Confirmation → Pick & Pack Items`, `Process Payment → Ship Order`, `Receive Tracking Information → Browse & Select Products`).

Das bestätigt die frühere Einschätzung im Conformance-Report: Der Heuristics Miner filtert dieses seltene, unregelmäßige Verhalten während der Modellentdeckung bewusst als Rauschen heraus (Frequenz-Schwellenwerte), um ein sauberes, verständliches Modell zu erhalten. Die dadurch entstehenden Footprint-Abweichungen sind somit **kein Modellfehler**, sondern die direkte, vollständig erklärbare Konsequenz der synthetisch eingefügten Störungen im Log.

## Artefakte
- [`noise_analysis.py`](noise_analysis.py) — Analyseskript (Varianten-Frequenz, Editierdistanz-Klassifikation, Directly-Follows-Abgleich)
- [`noise_report.txt`](noise_report.txt) — vollständiger Rohbericht mit allen 40 Noise-Varianten im Detail
