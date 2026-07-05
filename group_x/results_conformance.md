# Konformitätsprüfung: Analyse und Ergebnisse (Event-Log Gruppe X)

Das vergleichende Conformance Checking der Petri-Netz-Modelle des **Alpha Miners** und des **Heuristics Miners** gegen das vollständige Event-Log `eventlog_group_x.xes` ("Online Ordering Process – SoSe 2026") wurde abgeschlossen.

Das Log umfasst **17.676 Ereignisse** über **1.100 Traces (Fälle)** mit **13 unterschiedlichen Aktivitäten** (u. a. `Browse & Select Products`, `Place Order`, `Validate Order & Check Stock`, `Process Payment`, `Pick & Pack Items`, `Ship Order`, `Express Ship Order`, `Approve Bulk Order`, `Notify Out of Stock`, `Handle Payment Failure`).

Die Durchführung der Analyse erfolgte unter Verwendung zweier etablierter Verfahren der Konformitätsprüfung:
1. **Token-based Replay:** Das ereignisweise Abspielen der Prozessinstanzen (Traces) auf dem Petri-Netz zur Ermittlung der Token-Fitness und Trace-Fitness.
2. **Footprint-basierte Konformitätsprüfung:** Die Analyse kausaler Beziehungen, Start- und Endaktivitäten sowie Parallelitäten auf globaler Ebene durch den Vergleich von Log- und Modell-Footprints.

---

## Vergleich der Konformitätsmetriken

Die folgende Tabelle zeigt den strukturierten Vergleich der Konformitätsmetriken für beide entdeckten Petri-Netze:

| Konformitätsmetrik | Alpha-Miner-Netz | Heuristics-Miner-Netz | Interpretation & Erkenntnisse |
| :--- | :---: | :---: | :--- |
| **Modellgröße (Stellen / Transitionen / Kanten)** | 2 / 13 / 15 | 28 / 55 / 110 | Der Alpha Miner lieferte ein extrem unterstrukturiertes Modell mit nahezu isolierten Transitionen. Der Heuristics Miner erzeugte ein detaillierteres, strukturell konsistentes Modell. |
| **TBR Log Fitness (Fitnesswert)** | **0,2582** | **0,9984** | Das **Heuristics-Miner-Netz** erklärt nahezu alle Ereignissequenzen fehlerfrei, während das Alpha-Miner-Netz eine deutlich niedrigere Replay-Fitness aufweist. |
| **TBR Trace Fitness %** | 0,00% | 94,55% | 1.040 von 1.100 Traces lassen sich vollständig fehlerfrei auf dem Heuristics-Miner-Netz abspielen; beim Alpha-Miner-Netz ist kein einziger Trace vollständig fit. |
| **TBR Konsumierte / Produzierte Token** | 5.510 / 18.776 | 37.492 / 37.492 | Beim Heuristics-Miner-Netz sind konsumierte und produzierte Token exakt ausgeglichen, was auf ein sauberes, korrektes Token-Routing hindeutet. Beim Alpha-Miner-Netz klafft eine große Lücke (5.510 vs. 18.776), ein Indiz für fehlende bzw. fehlerhafte Stellen. |
| **TBR Fehlende / Verbleibende Token (Fehler)**| 3.310 / 16.576 | 60 / 60 | Das Alpha-Miner-Netz weist massive Fehler beim Token-Replay auf. Das Heuristics-Miner-Netz zeigt nur minimale, symmetrische Fehler (60 fehlend, 60 verbleibend) auf wenigen abweichenden Pfaden. |
| **Footprint-basierte Fitness** | 0,8431 | 0,9958 | Beide Modelle erzielen recht hohe Werte, jedoch aus unterschiedlichen Gründen (Details siehe unten). |
| **Footprint-basierte Präzision** | **0,3357** | **1,0000** | Das **Alpha-Miner-Netz** hat eine niedrige Präzision (Übergeneralisierung), während das **Heuristics-Miner-Netz** eine perfekte Präzision erreicht – es erlaubt kein Verhalten, das nicht auch im Log beobachtet wurde. |
| **Footprint Abweichungen (Gesamtzahl)** | 7 | 28 | Das Alpha-Miner-Netz verletzt nur 7 Relationen, da es durch isolierte Transitionen fast jedes Verhalten zulässt. Das Heuristics-Miner-Netz weist 28 Abweichungen auf, die vor allem auf seltenen Nebenpfaden rund um Express-Versand und Tracking-Informationen auftreten. |

---

## Detaillierte Erkenntnisse & Process-Mining-Analysen

### 1. Das Übergeneralisierungs-Paradoxon des Alpha Miners
* **Warum ist die TBR-Fitness niedrig (0,2582), aber die Footprint-Fitness vergleichsweise hoch (0,8431)?**
  Das Alpha-Miner-Netz ist stark unterstrukturiert und enthält lediglich **2 Stellen** für **13 Transitionen**. Ein Großteil der Transitionen ist damit vollständig oder größtenteils **isoliert (ohne ausreichende Ein-/Ausgangsstellen)**.
  In der Petri-Netz-Semantik ist eine Transition ohne Eingangsstellen *immer aktiviert* und kann somit jederzeit feuern.
  * **Footprint-Perspektive:** Da die Transitionen kaum durch Stellen eingeschränkt sind, lässt das Modell zu, dass sehr viele Aktivitätsfolgen auftreten können, die real gar nicht vorkommen (z. B. `Place Order → Place Order` oder `Place Order → Browse & Select Products`, siehe Abweichungsliste unten). Dadurch werden die tatsächlichen Log-Relationen selten verletzt (nur 7 Abweichungen, daher die relativ hohe Footprint-Fitness von 0,8431). Dies macht das Modell jedoch kaum aussagekräftig: die **Präzision von nur 0,3357** zeigt, dass es sehr viele Pfade erlaubt, die in der Realität nie vorkommen.
  * **TBR-Perspektive:** Das markenbasierte Replay (TBR) verfolgt den tatsächlichen Token-Fluss von der Anfangs- zur Endmarkierung. Da im Alpha-Miner-Modell kaum Stellen und Kanten existieren, können Token an den entsprechenden Schritten nicht korrekt konsumiert oder produziert werden. Dies führt zu 3.310 fehlenden und 16.576 verbleibenden Token, was in einer TBR-Log-Fitness von nur 0,2582 und 0 vollständig fitten Traces resultiert.

### 2. Robustheit des Heuristics Miners
* **Hervorragende TBR-Fitness (0,9984) und ausgeglichener Token-Fluss:**
  Das Heuristics-Miner-Modell erzielt eine nahezu perfekte Replay-Fitness; 1.040 von 1.100 Traces (94,55 %) werden vollständig fehlerfrei abgespielt. Konsumierte und produzierte Token sind mit jeweils 37.492 exakt identisch, was auf ein strukturell korrektes, in sich konsistentes Modell hinweist.
* **Perfekte Footprint-Präzision (1,0000):**
  Im Gegensatz zum Alpha Miner erlaubt das Heuristics-Miner-Netz **keine** Aktivitätsfolge, die nicht auch tatsächlich im Event-Log beobachtet wurde. Es findet keine Übergeneralisierung statt.
* **Erklärung der 28 Footprint-Abweichungen:**
  Die 28 Abweichungen betreffen ausschließlich Relationen, die **im Log vorkommen, aber vom Modell nicht abgedeckt werden** (z. B. Übergänge rund um `Receive Tracking Information`, `Express Ship Order`, `Send Tracking Information` und `Approve Bulk Order`). Diese seltenen Nebenpfade – etwa alternative Reihenfolgen bei Express-Versand oder Genehmigung von Großbestellungen – wurden bei der Modellentdeckung bewusst als Rauschen ausgefiltert, um ein lesbares Modell ohne "Spaghetti-Strukturen" zu erhalten. Da diese fehlenden Relationen nur die Fitness (nicht aber die Präzision) beeinflussen, sinkt die Footprint-Fitness nur geringfügig (auf 0,9958), während die Präzision unangetastet bei 1,0000 bleibt. Dies ist ein klassischer Fitness-Präzision-Trade-off: Ein geringer Verlust an Vollständigkeit wird zugunsten eines hochpräzisen, verständlichen Modells in Kauf genommen.

---

## Fazit
Auch für das Event-Log der Gruppe X (`eventlog_group_x.xes`, Online-Bestellprozess) ist das **Heuristics-Miner-Petri-Netz** dem Alpha-Miner-Netz in jeglicher Hinsicht überlegen. Es bildet die zugrundeliegende Bestellprozesslogik präzise ab, was durch die hohe TBR-Log-Fitness (99,84 %), die hohe Trace-Fitness (94,55 %) und die perfekte Footprint-Präzision (100 %) belegt wird. Das Alpha-Miner-Modell ist aufgrund der extremen Unterstrukturierung (nur 2 Stellen für 13 Transitionen, weitgehend isolierte Transitionen) kaum brauchbar, da es zu massiven Fehlern beim Token-Replay führt (0 fehlerfrei abgespielte Traces) und das reale Verhalten durch starke Übergeneralisierung (Präzision nur 33,57 %) verzerrt.
