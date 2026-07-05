import os
import pm4py
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.algo.discovery.alpha import algorithm as alpha_miner
from pm4py.algo.discovery.heuristics import algorithm as heuristics_miner
from pm4py.objects.petri_net.exporter import exporter as pnml_exporter

def make_readable(net):
    counts = {}
    for t in net.transitions:
        if t.label:
            # Clean label to contain only alphanumeric characters and underscores
            clean_label = "".join([c if c.isalnum() or c == '_' else '_' for c in t.label])
            # Remove consecutive underscores
            while "__" in clean_label:
                clean_label = clean_label.replace("__", "_")
            counts[clean_label] = counts.get(clean_label, 0) + 1
            t.name = f"{clean_label}_{counts[clean_label]}"
        else:
            counts["tau"] = counts.get("tau", 0) + 1
            t.name = f"tau_{counts['tau']}"

def main():
    log_path = 'n8n_sim_process_log.xes'
    print(f"Reading event log from {log_path}...")
    
    # 1. Load the XES log
    log = pm4py.read_xes(log_path)
    
    # Print basic statistics
    print("\n--- Event Log Statistics ---")
    activities = pm4py.get_event_attribute_values(log, "concept:name")
    print(f"Number of cases (traces): {len(log)}")
    print(f"Number of unique activities: {len(activities)}")
    print(f"Activities: {list(activities.keys())}")
    
    # 2. Alpha Miner Process Discovery
    print("\n--- Applying Alpha Miner ---")
    net_alpha, im_alpha, fm_alpha = alpha_miner.apply(log)
    make_readable(net_alpha)
    print(f"Alpha Miner Petri Net details:")
    print(f"  Places: {len(net_alpha.places)}")
    print(f"  Transitions: {len(net_alpha.transitions)}")
    print(f"  Arcs: {len(net_alpha.arcs)}")
    
    # Export Alpha Miner Petri Net to PNML
    alpha_pnml_path = 'alpha_miner_petri_net.pnml'
    pm4py.write_pnml(net_alpha, im_alpha, fm_alpha, alpha_pnml_path)
    print(f"Exported Alpha Miner Petri Net to: {alpha_pnml_path}")
    
    # 3. Heuristics Miner Process Discovery
    print("\n--- Applying Heuristics Miner ---")
    # Discover a heuristics net first
    heu_net = heuristics_miner.apply_heu(log)
    print(f"Heuristics Net details:")
    print(f"  Activities (nodes): {len(heu_net.nodes)}")
    
    # Convert/discover heuristics Petri net
    net_heur, im_heur, fm_heur = heuristics_miner.apply(log)
    make_readable(net_heur)
    print(f"Heuristics Miner Petri Net details:")
    print(f"  Places: {len(net_heur.places)}")
    print(f"  Transitions: {len(net_heur.transitions)}")
    print(f"  Arcs: {len(net_heur.arcs)}")
    
    # Export Heuristics Miner Petri Net to PNML
    heur_pnml_path = 'heuristics_miner_petri_net.pnml'
    pm4py.write_pnml(net_heur, im_heur, fm_heur, heur_pnml_path)
    print(f"Exported Heuristics Miner Petri Net to: {heur_pnml_path}")

    # Generate Graphviz dot source if possible, so user can visualize it
    print("\n--- Generating Graphviz Dot Files ---")
    try:
        from pm4py.visualization.petri_net import visualizer as pn_visualizer
        
        # Alpha Miner visualization (DOT file representation)
        gviz_alpha = pn_visualizer.apply(net_alpha, im_alpha, fm_alpha)
        alpha_dot_path = 'alpha_miner_petri_net.gv'
        with open(alpha_dot_path, 'w', encoding='utf-8') as f:
            f.write(str(gviz_alpha))
        print(f"Exported Alpha Miner DOT source to: {alpha_dot_path}")
        
        # Heuristics Miner visualization (DOT file representation)
        gviz_heur = pn_visualizer.apply(net_heur, im_heur, fm_heur)
        heur_dot_path = 'heuristics_miner_petri_net.gv'
        with open(heur_dot_path, 'w', encoding='utf-8') as f:
            f.write(str(gviz_heur))
        print(f"Exported Heuristics Miner DOT source to: {heur_dot_path}")
        
    except Exception as e:
        print(f"Failed to generate DOT files: {e}")

if __name__ == '__main__':
    main()
