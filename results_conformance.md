# Conformance Checking Walkthrough & Analysis

We have completed the comparative conformance analysis of the **Alpha Miner** and **Heuristics Miner** Petri net models against the full `n8n_sim_process_log.xes` event log. 

The analysis was performed using two main conformance checking techniques:
1. **Token-based Replay (TBR):** Replaying cases event-by-event on the Petri net to compute token fitness and trace fitness.
2. **Footprint-based Conformance:** Analyzing causal relationships, start/end activities, and parallelisms at a global level using log and model footprints.

---

## Conformance Metrics Comparison

Below is the structured comparison of the conformance metrics for both discovered Petri Nets:

| Conformance Metric | Alpha Miner Net | Heuristics Miner Net | Interpretation & Insight |
| :--- | :---: | :---: | :--- |
| **Model Size (Places / Transitions / Arcs)** | 2 / 34 / 7 | 74 / 121 / 259 | Alpha Miner discovered an extremely under-structured model. Heuristics Miner captured a detailed, complex model. |
| **TBR Log Fitness** | **0.0082** | **0.9889** | **Heuristics Miner Net** explains almost all event sequences perfectly, whereas Alpha Miner has near-zero replay fitness. |
| **TBR Trace Fitness %** | 0.00% | 30.00% | 3 out of the 10 long-running simulation traces replay perfectly on Heuristics Miner Net; 0 on Alpha Miner Net. |
| **TBR Consumed / Produced Tokens** | 2,414 / 2,444 | 36,732 / 37,022 | The event log is extremely large (18,198 events). Heuristics Miner Net routes tens of thousands of tokens correctly. |
| **TBR Missing / Remaining Tokens (Errors)**| 2,394 / 2,424 | 266 / 556 | Alpha Miner Net suffers from massive token replay failures. Heuristics Miner Net has minimal errors. |
| **Footprint-based Fitness** | 0.8813 | 0.9549 | Both models score high, but for different reasons (see details below). |
| **Footprint-based Precision** | **0.1709** | **0.8816** | **Alpha Miner Net** has extremely low precision (over-generalization), while **Heuristics Miner Net** is highly precise. |
| **Footprint Total Violations** | 5 | 132 | Alpha Miner Net violates only 5 relationships because it allows almost anything. Heuristics Miner Net has 132 minor mismatches on low-frequency paths. |

---

## Detailed Findings & Process Mining Insights

### 1. The Alpha Miner Over-Generalization Paradox
* **Why is TBR fitness near-zero (0.0082) but Footprint fitness high (0.8813)?**
  The Alpha Miner Net is highly under-structured, containing only **2 places** for **34 transitions**. This means 30+ transitions are completely **disconnected (input-free and output-free)**.
  In Petri Net semantics, a transition without input places is *always enabled* and can fire at any time, infinitely.
  * **Footprint view:** Because the transitions are input-free, the model allows *any* transition to follow *any other* transition (all sequences are allowed). Thus, the footprint of the model is extremely permissive. Because it permits almost everything, the log's relationships are rarely "violated" (hence 0.8813 fitness and only 5 violations). However, this makes the model useless (precision of **0.1709**), as it allows endless behavior that never happens in reality.
  * **TBR view:** Token-based replay tracks actual token routing from the initial marking to the final marking. Since there are almost no places or arcs in the Alpha Miner model, tokens cannot be successfully consumed or produced at the appropriate steps. This results in a massive number of missing tokens (2,394) and remaining tokens (2,424) during replay, yielding a near-zero TBR log fitness.

### 2. Heuristics Miner Robustness
* **Outstanding TBR Fitness (0.9889):**
  The Heuristics Miner model achieves nearly perfect replay fitness. This demonstrates that the frequency thresholds and dependency calculations used during discovery successfully captured the main operational flows of the n8n processes, filter out noise, and establish correct routing logic.
* **High Footprint Precision (0.8816):**
  Unlike Alpha Miner, Heuristics Miner Net restricts execution paths to those actually observed in the event log. It does not generalize excessively, making it a highly reliable and precise process representation.
* **Understanding the 132 Footprint Violations:**
  Because Heuristics Miner restricts behavior to keep the model precise (high precision), it naturally introduces some violations on low-frequency, alternative paths that were omitted during discovery (to keep the model readable and avoid "spaghetti" structures). This is a standard process mining trade-off: sacrificing a tiny amount of fitness (from 1.0 to 0.9549) to gain major precision and keep the model comprehensible.

---

## Conclusion
The **Heuristics Miner Petri Net** is vastly superior. It accurately and precisely models the underlying n8n process logic, as proven by its high token replay fitness (98.9%) and footprint precision (88.2%). The Alpha Miner model is unusable due to severe under-structuring (input-free transitions) causing massive token-replay errors and over-generalization.
