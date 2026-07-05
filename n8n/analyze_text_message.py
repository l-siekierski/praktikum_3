import pm4py

def main():
    log_path = 'n8n_sim_process_log.xes'
    df = pm4py.read_xes(log_path)
    
    cases = df.groupby('case:concept:name')
    
    print("Analyzing transitions from any 'Send a text message*' activity to webhook/scrapers...")
    
    all_transitions = {}
    
    for case_id, group in cases:
        sorted_group = group.sort_values('time:timestamp')
        activities = sorted_group['concept:name'].tolist()
        
        for i in range(len(activities) - 1):
            act = activities[i]
            next_act = activities[i+1]
            if "text message" in act.lower():
                pair = (act, next_act)
                all_transitions[pair] = all_transitions.get(pair, 0) + 1
                
    print("\nAll transitions from 'Send a text message' variants:")
    for pair, count in sorted(all_transitions.items(), key=lambda x: x[1], reverse=True):
        if "webhook" in pair[1].lower() or "scrapper" in pair[1].lower() or "query" in pair[1].lower():
            print(f"  [BACK-LOOP] {pair[0]} -> {pair[1]}: {count} times")
        else:
            print(f"  {pair[0]} -> {pair[1]}: {count} times")

if __name__ == '__main__':
    main()
