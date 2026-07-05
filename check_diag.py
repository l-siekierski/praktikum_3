import pm4py

log = pm4py.read_xes('n8n_sim_process_log.xes')
print(f"Log type: {type(log)}")
print(f"Total events: {len(log)}")

if 'case:concept:name' in log.columns:
    cases = log['case:concept:name'].unique()
    print(f"Unique cases by case:concept:name: {len(cases)}")
    print(f"Case IDs: {list(cases)}")
else:
    print("case:concept:name not in columns. Columns are:")
    print(log.columns)
