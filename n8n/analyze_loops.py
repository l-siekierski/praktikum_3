import pm4py
import pandas as pd

def main():
    log_path = 'n8n_sim_process_log.xes'
    print(f"Reading event log from {log_path}...")
    df = pm4py.read_xes(log_path)
    print("Total events (rows):", len(df))
    
    # Group by case ID
    cases = df.groupby('case:concept:name')
    print("Total cases:", len(cases))
    
    loop_counts = {}
    examples = []
    
    # We want to trace cases
    for case_id, group in cases:
        # Sort by timestamp to ensure chronological order of events in trace
        sorted_group = group.sort_values('time:timestamp')
        activities = sorted_group['concept:name'].tolist()
        
        for i in range(len(activities) - 1):
            act = activities[i]
            next_act = activities[i+1]
            if act == 'Send a text message1':
                pair = (act, next_act)
                loop_counts[pair] = loop_counts.get(pair, 0) + 1
                if 'Scrapper' in next_act or next_act == 'Webhook' or 'Query' in next_act:
                    if len(examples) < 5:
                        examples.append({
                            "case_id": case_id,
                            "sequence": activities[max(0, i-2): min(len(activities), i+4)]
                        })
                        
    print("\n--- Transitions from 'Send a text message1' ---")
    for pair, count in sorted(loop_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {pair[0]} -> {pair[1]}: {count} times")
        
    print("\n--- Example trace sequences showing loops back to Scrappers/Queries ---")
    for ex in examples:
        print(f"Case {ex['case_id']}: {' -> '.join(ex['sequence'])}")

if __name__ == '__main__':
    main()
