import os
import time
import pm4py
from pm4py.algo.discovery.footprints import algorithm as footprints_discovery
from pm4py.algo.conformance.footprints import algorithm as footprints_conformance
from pm4py.algo.conformance.footprints.util import evaluation as fp_evaluation

def main():
    log_path = 'n8n_sim_process_log.xes'
    print(f"=== Loading Event Log: {log_path} ===")
    start_time = time.time()
    log = pm4py.read_xes(log_path)
    num_events = len(log)
    num_cases = log['case:concept:name'].nunique() if 'case:concept:name' in log.columns else 0
    print(f"Loaded event log with {num_events} events and {num_cases} cases in {time.time() - start_time:.2f} seconds.\n")

    # Load Petri Nets
    alpha_pnml_path = 'alpha_miner_petri_net.pnml'
    heur_pnml_path = 'heuristics_miner_petri_net.pnml'

    print(f"=== Loading Alpha Miner Petri Net ===")
    net_alpha, im_alpha, fm_alpha = pm4py.read_pnml(alpha_pnml_path)
    print(f"Places: {len(net_alpha.places)}, Transitions: {len(net_alpha.transitions)}, Arcs: {len(net_alpha.arcs)}")

    print(f"\n=== Loading Heuristics Miner Petri Net ===")
    net_heur, im_heur, fm_heur = pm4py.read_pnml(heur_pnml_path)
    print(f"Places: {len(net_heur.places)}, Transitions: {len(net_heur.transitions)}, Arcs: {len(net_heur.arcs)}\n")

    # ==========================================
    # PART 1: Token-based Replay Conformance
    # ==========================================
    print("=== Running Token-based Replay (TBR) ===")
    
    # 1. Alpha Miner TBR
    print("Applying TBR on Alpha Miner Model...")
    tbr_start = time.time()
    fit_alpha = pm4py.fitness_token_based_replay(log, net_alpha, im_alpha, fm_alpha)
    diag_alpha = pm4py.conformance_diagnostics_token_based_replay(log, net_alpha, im_alpha, fm_alpha)
    tbr_alpha_time = time.time() - tbr_start
    print(f"Alpha Miner TBR completed in {tbr_alpha_time:.2f} seconds.")
    
    # 2. Heuristics Miner TBR
    print("Applying TBR on Heuristics Miner Model...")
    tbr_start = time.time()
    fit_heur = pm4py.fitness_token_based_replay(log, net_heur, im_heur, fm_heur)
    diag_heur = pm4py.conformance_diagnostics_token_based_replay(log, net_heur, im_heur, fm_heur)
    tbr_heur_time = time.time() - tbr_start
    print(f"Heuristics Miner TBR completed in {tbr_heur_time:.2f} seconds.\n")

    # ==========================================
    # PART 2: Footprint-based Conformance (Global / Entire Event Log)
    # ==========================================
    print("=== Running Footprint-based Conformance (Global) ===")
    
    # 1. Discover Log Footprints (Global)
    print("Discovering footprints from Event Log...")
    fp_start = time.time()
    fp_log = footprints_discovery.apply(log) # Defaults to ENTIRE_EVENT_LOG
    print(f"Log footprints discovered in {time.time() - fp_start:.2f} seconds.")

    # 2. Discover Alpha Model Footprints
    print("Discovering footprints from Alpha Miner Model...")
    fp_alpha = footprints_discovery.apply(net_alpha, im_alpha, parameters={"max_elab_time": 5})
    
    # 3. Discover Heuristics Model Footprints
    print("Discovering footprints from Heuristics Miner Model...")
    fp_heur = footprints_discovery.apply(net_heur, im_heur, parameters={"max_elab_time": 5})

    # 4. Footprint Conformance for Alpha Miner
    print("Running Footprint Conformance for Alpha Miner...")
    conf_alpha = footprints_conformance.apply(fp_log, fp_alpha, variant=footprints_conformance.Variants.LOG_EXTENSIVE)
    fit_fp_alpha = fp_evaluation.fp_fitness(fp_log, fp_alpha, conf_alpha)
    prec_fp_alpha = fp_evaluation.fp_precision(fp_log, fp_alpha)

    # 5. Footprint Conformance for Heuristics Miner
    print("Running Footprint Conformance for Heuristics Miner...")
    conf_heur = footprints_conformance.apply(fp_log, fp_heur, variant=footprints_conformance.Variants.LOG_EXTENSIVE)
    fit_fp_heur = fp_evaluation.fp_fitness(fp_log, fp_heur, conf_heur)
    prec_fp_heur = fp_evaluation.fp_precision(fp_log, fp_heur)
    print("Footprint-based conformance completed.\n")

    # ==========================================
    # PART 3: Analysis & Report Generation
    # ==========================================
    print("=== Generating Comparison Summary ===")
    
    def summarize_tbr_diagnostics(diag):
        total_traces = len(diag)
        fit_traces = sum(1 for x in diag if x.get('trace_is_fit', False))
        fit_pct = (fit_traces / total_traces) * 100 if total_traces > 0 else 0.0
        
        total_missing = sum(x.get('missing_tokens', 0) for x in diag)
        total_remaining = sum(x.get('remaining_tokens', 0) for x in diag)
        total_consumed = sum(x.get('consumed_tokens', 0) for x in diag)
        total_produced = sum(x.get('produced_tokens', 0) for x in diag)
        
        return {
            'total': total_traces,
            'fit_traces': fit_traces,
            'fit_pct': fit_pct,
            'missing': total_missing,
            'remaining': total_remaining,
            'consumed': total_consumed,
            'produced': total_produced
        }
        
    sum_tbr_alpha = summarize_tbr_diagnostics(diag_alpha)
    sum_tbr_heur = summarize_tbr_diagnostics(diag_heur)

    # Summarize footprint violations
    # For LOG_EXTENSIVE, conf_alpha and conf_heur are dictionaries.
    viol_total_alpha = (len(conf_alpha['footprints']) + 
                        len(conf_alpha['start_activities']) + 
                        len(conf_alpha['end_activities'])) if conf_alpha else 0
    viol_total_heur = (len(conf_heur['footprints']) + 
                       len(conf_heur['start_activities']) + 
                       len(conf_heur['end_activities'])) if conf_heur else 0

    # Let's print a structured table
    print("\n" + "="*80)
    print("                   CONFORMANCE CHECKING RESULTS COMPARISON")
    print("="*80)
    print(f"{'Metric':<35} | {'Alpha Miner Net':<20} | {'Heuristics Miner Net':<20}")
    print("-"*80)
    
    # TBR Metrics
    print(f"{'Token Replay Log Fitness':<35} | {fit_alpha['log_fitness']:.4f}               | {fit_heur['log_fitness']:.4f}")
    print(f"{'Token Replay Trace Fitness Pct':<35} | {fit_alpha['perc_fit_traces']:.2f}%              | {fit_heur['perc_fit_traces']:.2f}%")
    print(f"{'TBR Fit Traces Count':<35} | {sum_tbr_alpha['fit_traces']}/{sum_tbr_alpha['total']}           | {sum_tbr_heur['fit_traces']}/{sum_tbr_heur['total']}")
    print(f"{'TBR Total Consumed Tokens':<35} | {sum_tbr_alpha['consumed']:<20} | {sum_tbr_heur['consumed']:<20}")
    print(f"{'TBR Total Produced Tokens':<35} | {sum_tbr_alpha['produced']:<20} | {sum_tbr_heur['produced']:<20}")
    print(f"{'TBR Total Missing Tokens (Error)':<35} | {sum_tbr_alpha['missing']:<20} | {sum_tbr_heur['missing']:<20}")
    print(f"{'TBR Total Remaining Tokens (Error)':<35} | {sum_tbr_alpha['remaining']:<20} | {sum_tbr_heur['remaining']:<20}")
    
    print("-"*80)
    # Footprint Metrics
    print(f"{'Footprint-based Fitness':<35} | {fit_fp_alpha:.4f}               | {fit_fp_heur:.4f}")
    print(f"{'Footprint-based Precision':<35} | {prec_fp_alpha:.4f}               | {prec_fp_heur:.4f}")
    print(f"{'Footprint Total Violations Count':<35} | {viol_total_alpha:<20} | {viol_total_heur:<20}")
    print("="*80)

    # Let's write the results to a file for easy reading
    with open('conformance_report_raw.txt', 'w', encoding='utf-8') as f:
        f.write("=== CONFORMANCE CHECKING RESULTS COMPARISON ===\n\n")
        f.write(f"Event Log: {log_path}\n")
        f.write(f"Total Events: {num_events}\n")
        f.write(f"Total Cases (Traces): {num_cases}\n\n")
        f.write(f"ALPHA MINER MODEL:\n")
        f.write(f"  Places: {len(net_alpha.places)}, Transitions: {len(net_alpha.transitions)}, Arcs: {len(net_alpha.arcs)}\n")
        f.write(f"  TBR Log Fitness: {fit_alpha['log_fitness']:.6f}\n")
        f.write(f"  TBR Trace Fitness %: {fit_alpha['perc_fit_traces']:.2f}%\n")
        f.write(f"  TBR Fit Traces: {sum_tbr_alpha['fit_traces']}/{sum_tbr_alpha['total']}\n")
        f.write(f"  TBR Consumed: {sum_tbr_alpha['consumed']}, Produced: {sum_tbr_alpha['produced']}\n")
        f.write(f"  TBR Missing: {sum_tbr_alpha['missing']}, Remaining: {sum_tbr_alpha['remaining']}\n")
        f.write(f"  Footprint Fitness: {fit_fp_alpha:.6f}\n")
        f.write(f"  Footprint Precision: {prec_fp_alpha:.6f}\n")
        f.write(f"  Footprint Total Violations: {viol_total_alpha}\n\n")
        
        f.write(f"HEURISTICS MINER MODEL:\n")
        f.write(f"  Places: {len(net_heur.places)}, Transitions: {len(net_heur.transitions)}, Arcs: {len(net_heur.arcs)}\n")
        f.write(f"  TBR Log Fitness: {fit_heur['log_fitness']:.6f}\n")
        f.write(f"  TBR Trace Fitness %: {fit_heur['perc_fit_traces']:.2f}%\n")
        f.write(f"  TBR Fit Traces: {sum_tbr_heur['fit_traces']}/{sum_tbr_heur['total']}\n")
        f.write(f"  TBR Consumed: {sum_tbr_heur['consumed']}, Produced: {sum_tbr_heur['produced']}\n")
        f.write(f"  TBR Missing: {sum_tbr_heur['missing']}, Remaining: {sum_tbr_heur['remaining']}\n")
        f.write(f"  Footprint Fitness: {fit_fp_heur:.6f}\n")
        f.write(f"  Footprint Precision: {prec_fp_heur:.6f}\n")
        f.write(f"  Footprint Total Violations: {viol_total_heur}\n\n")

        # Inspect footprint violations
        f.write("=== FOOTPRINT VIOLATIONS DETAIL (ALPHA MINER) ===\n")
        if conf_alpha and (conf_alpha['footprints'] or conf_alpha['start_activities'] or conf_alpha['end_activities']):
            viol_idx = 1
            for viol in list(conf_alpha['footprints'])[:25]:
                f.write(f"  {viol_idx}. Relation mismatch: {viol}\n")
                viol_idx += 1
            for viol in list(conf_alpha['start_activities'])[:10]:
                f.write(f"  {viol_idx}. Start activity mismatch: {viol}\n")
                viol_idx += 1
            for viol in list(conf_alpha['end_activities'])[:10]:
                f.write(f"  {viol_idx}. End activity mismatch: {viol}\n")
                viol_idx += 1
        else:
            f.write("  No footprint deviations found.\n")
            
        f.write("\n=== FOOTPRINT VIOLATIONS DETAIL (HEURISTICS MINER) ===\n")
        if conf_heur and (conf_heur['footprints'] or conf_heur['start_activities'] or conf_heur['end_activities']):
            viol_idx = 1
            for viol in list(conf_heur['footprints'])[:25]:
                f.write(f"  {viol_idx}. Relation mismatch: {viol}\n")
                viol_idx += 1
            for viol in list(conf_heur['start_activities'])[:10]:
                f.write(f"  {viol_idx}. Start activity mismatch: {viol}\n")
                viol_idx += 1
            for viol in list(conf_heur['end_activities'])[:10]:
                f.write(f"  {viol_idx}. End activity mismatch: {viol}\n")
                viol_idx += 1
        else:
            f.write("  No footprint deviations found.\n")

    print("Successfully exported report to conformance_report_raw.txt")

if __name__ == '__main__':
    main()
