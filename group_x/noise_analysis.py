import pm4py
from collections import Counter


def damerau_levenshtein(a, b):
    la, lb = len(a), len(b)
    d = [[0] * (lb + 1) for _ in range(la + 1)]
    for i in range(la + 1):
        d[i][0] = i
    for j in range(lb + 1):
        d[0][j] = j
    for i in range(1, la + 1):
        for j in range(1, lb + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            d[i][j] = min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + cost)
            if i > 1 and j > 1 and a[i - 1] == b[j - 2] and a[i - 2] == b[j - 1]:
                d[i][j] = min(d[i][j], d[i - 2][j - 2] + 1)
    return d[la][lb]


def classify(variant, main_variants):
    best_dist, best_main = min(
        ((damerau_levenshtein(variant, m), m) for m in main_variants), key=lambda x: x[0]
    )
    len_diff = len(variant) - len(best_main)
    if len_diff == -1:
        kind = "missing_event"
    elif len_diff == 1:
        kind = "duplicate_event"
    elif len_diff == 0 and best_dist == 1:
        kind = "swapped_events"
    else:
        kind = f"other(dist={best_dist},len_diff={len_diff})"
    return kind, best_main, best_dist


def pairs(seq):
    return set(zip(seq, seq[1:]))


def main():
    log_path = 'eventlog_group_x.xes'
    main_threshold = 10  # variants above this frequency are treated as "clean" main behavior

    print(f"=== Loading Event Log: {log_path} ===")
    log = pm4py.read_xes(log_path)
    comp = log[log['lifecycle:transition'] == 'complete'].sort_values(['case:concept:name', 'time:timestamp'])
    variants_per_case = comp.groupby('case:concept:name')['concept:name'].apply(tuple)
    var_counts = Counter(variants_per_case)
    total_cases = len(variants_per_case)

    main_variants = [v for v, c in var_counts.items() if c > main_threshold]
    noise_variants = {v: c for v, c in var_counts.items() if c <= main_threshold}
    total_noise_cases = sum(noise_variants.values())

    print(f"\nDistinct variants: {len(var_counts)} | Total cases: {total_cases}")
    print(f"Main variants (>{main_threshold} cases): {len(main_variants)}, covering "
          f"{total_cases - total_noise_cases} cases ({(total_cases - total_noise_cases) / total_cases * 100:.2f}%)")
    print(f"Noise variants (<={main_threshold} cases): {len(noise_variants)}, covering "
          f"{total_noise_cases} cases ({total_noise_cases / total_cases * 100:.2f}%)")

    # classify each noisy variant by edit distance to nearest main variant
    classification = Counter()
    details = []
    for v, c in noise_variants.items():
        kind, best_main, dist = classify(v, main_variants)
        classification[kind] += c
        details.append((c, kind, v, best_main))

    print("\n--- Noise type breakdown (edit-distance classification vs. nearest main variant) ---")
    for kind, total in classification.most_common():
        print(f"  {kind:20s}: {total} cases")

    # directly-follows relations that only occur inside noisy traces
    main_pairs = set()
    for v in main_variants:
        main_pairs |= pairs(v)

    noise_only_pairs = Counter()
    for v in noise_variants:
        for p in pairs(v):
            if p not in main_pairs:
                noise_only_pairs[p] += var_counts[v]

    print(f"\n--- Directly-follows relations occurring ONLY in noisy traces ({len(noise_only_pairs)}) ---")
    for p, c in noise_only_pairs.most_common():
        print(f"  {p[0]} -> {p[1]}  ({c} cases)")

    # write report
    with open('noise_report.txt', 'w', encoding='utf-8') as f:
        f.write("=== NOISE ANALYSIS: eventlog_group_x.xes ===\n\n")
        f.write(f"Total cases: {total_cases}, distinct variants: {len(var_counts)}\n")
        f.write(f"Main variants (>{main_threshold} cases): {len(main_variants)} "
                f"covering {total_cases - total_noise_cases} cases "
                f"({(total_cases - total_noise_cases) / total_cases * 100:.2f}%)\n")
        f.write(f"Noise variants (<={main_threshold} cases): {len(noise_variants)} "
                f"covering {total_noise_cases} cases ({total_noise_cases / total_cases * 100:.2f}%)\n\n")

        f.write("--- Noise type breakdown ---\n")
        for kind, total in classification.most_common():
            f.write(f"  {kind}: {total} cases\n")

        f.write("\n--- Noisy variants in detail ---\n")
        for c, kind, v, m in sorted(details, key=lambda x: -x[0]):
            f.write(f"[{kind}] count={c}\n")
            f.write(f"  variant: {' -> '.join(v)}\n")
            f.write(f"  nearest main variant: {' -> '.join(m)}\n\n")

        f.write("--- Directly-follows relations occurring ONLY in noisy traces ---\n")
        for p, c in noise_only_pairs.most_common():
            f.write(f"  {p[0]} -> {p[1]}  ({c} cases)\n")

    print("\nExported detailed report to noise_report.txt")


if __name__ == '__main__':
    main()
