import pm4py
from pm4py.objects.log.obj import EventLog

def main():
    log_path = 'n8n_sim_process_log.xes'
    print(f"Reading event log from {log_path}...")
    log = pm4py.read_xes(log_path)
    
    print("\nDiscovering models...")
    # Alpha Miner
    net_alpha, im_alpha, fm_alpha = pm4py.discover_petri_net_alpha(log)
    
    # Heuristics Miner
    net_heur, im_heur, fm_heur = pm4py.discover_petri_net_heuristics(log)
    
    # Sampling for fast conformance check (e.g. 500 traces)
    sample_size = 500
    print(f"\nSampling {sample_size} cases from the log for fast evaluation...")
    # Slicing the log (or event log object)
    if isinstance(log, EventLog):
        log_sample = EventLog(log[:sample_size])
    else:
        log_sample = log[:sample_size]
        
    print("\nEvaluating Alpha Miner model on sample...")
    # Alpha Miner Fitness & Precision
    fit_alpha = pm4py.fitness_token_based_replay(log_sample, net_alpha, im_alpha, fm_alpha)
    prec_alpha = pm4py.precision_token_based_replay(log_sample, net_alpha, im_alpha, fm_alpha)
    
    print("\nEvaluating Heuristics Miner model on sample...")
    # Heuristics Miner Fitness & Precision
    fit_heur = pm4py.fitness_token_based_replay(log_sample, net_heur, im_heur, fm_heur)
    prec_heur = pm4py.precision_token_based_replay(log_sample, net_heur, im_heur, fm_heur)
    
    print("\n" + "="*50)
    print("           MODEL COMPARISON RESULTS")
    print("="*50)
    print(f"Log Sample Size: {len(log_sample)} traces")
    print("\nALPHA MINER MODEL:")
    print(f"  Places:      {len(net_alpha.places)}")
    print(f"  Transitions: {len(net_alpha.transitions)}")
    print(f"  Arcs:        {len(net_alpha.arcs)}")
    print(f"  Fitness:     {fit_alpha['log_fitness']:.4f} (percentage of replayed events: {fit_alpha['perc_fit_traces']:.2f}%)")
    print(f"  Precision:   {prec_alpha:.4f}")
    
    print("\nHEURISTICS MINER MODEL:")
    print(f"  Places:      {len(net_heur.places)}")
    print(f"  Transitions: {len(net_heur.transitions)}")
    print(f"  Arcs:        {len(net_heur.arcs)}")
    print(f"  Fitness:     {fit_heur['log_fitness']:.4f} (percentage of replayed events: {fit_heur['perc_fit_traces']:.2f}%)")
    print(f"  Precision:   {prec_heur:.4f}")
    print("="*50)

if __name__ == '__main__':
    main()
