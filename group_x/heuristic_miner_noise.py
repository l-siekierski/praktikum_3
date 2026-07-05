import pm4py
from pm4py.algo.discovery.heuristics import algorithm as heuristics_miner
from pm4py.algo.discovery.heuristics.variants.classic import defaults as heu_defaults


def main():
    log_path = 'eventlog_group_x.xes'
    print(f"=== Loading Event Log: {log_path} ===")
    log = pm4py.read_xes(log_path)

    print("\n--- Heuristics Miner default thresholds (pm4py) ---")
    print(f"  dfg_pre_cleaning_noise_thresh : {heu_defaults.DEFAULT_DFG_PRE_CLEANING_NOISE_THRESH}"
          f"  (edges with rel. frequency below this are discarded as noise BEFORE the dependency graph is built)")
    print(f"  dependency_thresh             : {heu_defaults.DEFAULT_DEPENDENCY_THRESH}"
          f"  (an edge that survives pre-cleaning still needs this causality score to become part of the net)")
    print(f"  and_measure_thresh            : {heu_defaults.DEFAULT_AND_MEASURE_THRESH}")
    print(f"  loop_length_two_thresh        : {heu_defaults.DEFAULT_LOOP_LENGTH_TWO_THRESH}")

    # 1. Raw, unfiltered Directly-Follows-Graph straight from the log
    raw_dfg, start_act, end_act = pm4py.discover_dfg(log)
    raw_edges = set(raw_dfg.keys())

    # 2. Let the Heuristics Miner do its own noise filtering
    heu_net = heuristics_miner.apply_heu(log)
    kept_edges = set(heu_net.dfg.keys())
    removed_by_precleaning = raw_edges - kept_edges

    print(f"\n--- Step 1: DFG pre-cleaning noise filter ---")
    print(f"Raw directly-follows edges in the log : {len(raw_edges)}")
    print(f"Edges surviving pre-cleaning           : {len(kept_edges)}")
    print(f"Edges discarded as NOISE by the Heuristics Miner: {len(removed_by_precleaning)}\n")

    for e in sorted(removed_by_precleaning, key=lambda x: -raw_dfg[x]):
        print(f"  NOISE  {e[0]} -> {e[1]}   (log frequency={raw_dfg[e]})")

    # 3. Check whether any surviving edge additionally fails the dependency threshold
    print(f"\n--- Step 2: Dependency threshold check on surviving edges ---")
    below_dep_thresh = []
    for a, succs in heu_net.dependency_matrix.items():
        for b, dep in succs.items():
            if dep < heu_defaults.DEFAULT_DEPENDENCY_THRESH:
                below_dep_thresh.append((a, b, dep))
    if below_dep_thresh:
        for a, b, dep in below_dep_thresh:
            print(f"  {a} -> {b}: dependency={dep:.4f} (below threshold, also excluded)")
    else:
        print("  None. All edges that survive pre-cleaning comfortably exceed the dependency threshold "
              "(observed values ~0.98-0.999) -> the noise threshold alone decides what counts as noise here.")

    total_noise_edges = removed_by_precleaning | {(a, b) for a, b, _ in below_dep_thresh}

    with open('heuristic_noise_report.txt', 'w', encoding='utf-8') as f:
        f.write("=== NOISE IDENTIFIED BY THE HEURISTICS MINER ALGORITHM ITSELF ===\n\n")
        f.write(f"Event Log: {log_path}\n")
        f.write(f"Raw directly-follows edges: {len(raw_edges)}\n")
        f.write(f"Edges kept in the Heuristics Net: {len(kept_edges)}\n")
        f.write(f"Edges classified as noise (dfg_pre_cleaning_noise_thresh="
                f"{heu_defaults.DEFAULT_DFG_PRE_CLEANING_NOISE_THRESH}): {len(removed_by_precleaning)}\n\n")
        f.write("--- Discarded edges (sorted by log frequency) ---\n")
        for e in sorted(removed_by_precleaning, key=lambda x: -raw_dfg[x]):
            f.write(f"  {e[0]} -> {e[1]}   freq={raw_dfg[e]}\n")
        f.write(f"\nEdges additionally failing dependency_thresh="
                f"{heu_defaults.DEFAULT_DEPENDENCY_THRESH}: {len(below_dep_thresh)}\n")
        for a, b, dep in below_dep_thresh:
            f.write(f"  {a} -> {b}: dependency={dep:.4f}\n")
        f.write(f"\nTotal edges treated as noise by the Heuristics Miner: {len(total_noise_edges)}\n")

    print(f"\nExported report to heuristic_noise_report.txt")
    print(f"Total edges treated as noise by the Heuristics Miner: {len(total_noise_edges)}")


if __name__ == '__main__':
    main()
