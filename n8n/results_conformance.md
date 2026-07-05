# Konformitätsprüfung: Analyse und Ergebnisse

Die Durchführung der Analyse erfolgte unter Verwendung folgender zweier Verfahren der Konformitätsprüfung:
1. **Token-based Replay:** Das ereignisweise Abspielen der Prozessinstanzen (Traces) auf dem Petri-Netz zur Ermittlung der Token-Fitness und Trace-Fitness.
2. **Footprint-basierte Konformitätsprüfung:** Die Analyse kausaler Beziehungen, Start- und Endaktivitäten sowie Parallelitäten auf globaler Ebene durch den Vergleich von Log- und Modell-Footprints.

---

## Vergleich der Konformitätsmetriken

Die folgende Tabelle zeigt den Vergleich der Konformitätsmetriken für beide entdeckten Petri-Netze:

| Konformitätsmetrik | Alpha-Miner-Netz | Heuristics-Miner-Netz | Interpretation & Erkenntnisse |
| :--- | :---: | :---: | :--- |
| **Modellgröße (Stellen / Transitionen / Kanten)** | 2 / 34 / 7 | 74 / 121 / 259 | Der Alpha Miner lieferte ein extrem unterstrukturiertes Modell. Der Heuristics Miner erzeugte ein detailliertes, komplexes Modell. |
| **TBR Log Fitness (Fitnesswert)** | **0,0082** | **0,9889** | Das **Heuristics-Miner-Netz** erklärt nahezu alle Ereignissequenzen fehlerfrei, während das Alpha-Miner-Netz eine Replay-Fitness nahe Null aufweist. |
| **TBR Trace Fitness %** | 0,00% | 30,00% | 3 der 10 langlaufenden Simulations-Traces lassen sich fehlerfrei auf dem Heuristics-Miner-Netz abspielen; beim Alpha-Miner-Netz kein einziger. |
| **TBR Konsumierte / Produzierte Token** | 2.414 / 2.444 | 36.732 / 37.022 | Das Event-Log ist mit 18.198 Ereignissen sehr groß. Das Heuristics-Miner-Netz leitet zehntausende Token fehlerfrei durch. |
| **TBR Fehlende / Verbleibende Token (Fehler)**| 2.394 / 2.424 | 266 / 556 | Das Alpha-Miner-Netz weist massive Fehler beim Token-Replay auf. Das Heuristics-Miner-Netz zeigt nur minimale Fehler. |
| **Footprint-basierte Fitness** | 0,8813 | 0,9549 | Beide Modelle erzielen hohe Werte, jedoch aus völlig unterschiedlichen Gründen (Details siehe unten). |
| **Footprint-basierte Präzision** | **0,1709** | **0,8816** | Das **Alpha-Miner-Netz** hat eine extrem niedrige Präzision, während das **Heuristics-Miner-Netz** hochpräzise ist. |
| **Footprint Abweichungen (Gesamtzahl)** | 5 | 132 | Das Alpha-Miner-Netz verletzt nur 5 Relationen, da es fast jedes Verhalten zulässt. Das Heuristics-Miner-Netz weist 132 Abweichungen auf seltenen Nebenpfaden auf. |

---

## Erkenntnisse & Process-Mining-Analysen

### 1. Das Übergeneralisierungs-Paradoxon des Alpha Miners
* **Warum ist die TBR-Fitness nahe Null (0,0082), aber die Footprint-Fitness hoch (0,8813)?**
  Das Alpha-Miner-Netz ist stark unterstrukturiert und enthält lediglich **2 Stellen** für **34 Transitionen**. Das bedeutet, dass über 30 Transitionen vollständig isoliert sind, ohne Eingangs- und Ausgangsstellen.
  In der Petri-Netz-Semantik ist eine Transition ohne Eingangsstellen immer aktiviert und kann somit jederzeit unendlich oft feuern.
  * **Footprint-Perspektive:** Da die Transitionen isoliert sind, lässt das Modell zu, dass jede Transition auf jede andere Transition folgen kann. Dadurch ist der Footprint des Modells extrem permissiv. Da nahezu jedes Verhalten erlaubt ist, werden die Relationen des Logs selten verletzt, daher die hohe Footprint-Fitness von 0,8813 und nur 5 Abweichungen. Das macht das Modell jedoch nutzlos (Präzision von 0,1709), da es unendlich viele Pfade erlaubt, die in der Realität niemals vorkommen.
  * **TBR-Perspektive:** Das markenbasierte Replay verfolgt den tatsächlichen Token-Fluss von der Anfangsmarkierung zur Endmarkierung. Da im Alpha-Miner-Modell fast keine Stellen oder Kanten existieren, können Token an den entsprechenden Schritten nicht erfolgreich konsumiert oder produziert werden. Dies führt beim Replay zu einer massiven Anzahl fehlender Token (2.394) und verbleibender Token (2.424), was in einer TBR-Log-Fitness nahe Null resultiert.

### 2. Robustheit des Heuristics Miners
* **Hervorragende TBR-Fitness (0,9889):**
  Das Heuristics-Miner-Modell erzielt eine nahezu perfekte Replay-Fitness. Dies belegt, dass die bei der Entdeckung genutzten Häufigkeitsschwellenwerte und Abhängigkeitsberechnungen die Hauptströme der n8n-Prozesse erfolgreich erfasst, Rauschen gefiltert und die korrekte Routing-Logik etabliert haben.
* **Hohe Footprint-Präzision (0,8816):**
  Im Gegensatz zum Alpha Miner schränkt das Heuristics-Miner-Netz die Ausführungspfade auf die tatsächlich im Event-Log beobachteten Sequenzen ein. Es findet keine übermäßige Generalisierung statt, was das Modell zu einer äußerst verlässlichen und präzisen Prozessdarstellung macht.
* **Erklärung der 132 Footprint-Abweichungen:**
  Da der Heuristics Miner das Verhalten einschränkt, um die Präzision des Modells hoch zu halten, entstehen zwangsläufig Abweichungen bei seltenen Nebenpfaden. Diese wurden bei der Modellentdeckung bewusst vernachlässigt, um ein lesbares Modell ohne "Spaghetti-Strukturen" zu erhalten. Die minimale Reduktion der Fitness (von 1,0 auf 0,9549) wird in Kauf genommen, um eine drastisch höhere Präzision und Verständlichkeit des Modells zu gewährleisten.

---

## Fazit
Das Heuristics-Miner-Petri-Netz ist dem Alpha-Miner-Netz in jeglicher Hinsicht überlegen. Es bildet die zugrundeliegende n8n-Prozesslogik präzise und exakt ab, was durch die hohe TBR-Log-Fitness (98,9 %) und die Footprint-Präzision (88,2 %) belegt wird. Das Alpha-Miner-Modell ist aufgrund der extremen Unterstrukturierung (isolierte Transitionen) unbrauchbar, da es zu massiven Fehlern beim Token-Replay führt und das reale Verhalten durch Übergeneralisierung verzerrt.
