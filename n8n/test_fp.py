import time
import pm4py
from pm4py.algo.discovery.footprints import algorithm as footprints_discovery

def test():
    print("Loading nets...")
    net_alpha, im_alpha, fm_alpha = pm4py.read_pnml('alpha_miner_petri_net.pnml')
    net_heur, im_heur, fm_heur = pm4py.read_pnml('heuristics_miner_petri_net.pnml')

    print("Testing footprint discovery on Alpha Miner Net...")
    t0 = time.time()
    fp_alpha = footprints_discovery.apply(net_alpha, im_alpha, parameters={"max_elab_time": 2})
    print(f"Alpha Miner Net footprints discovered in {time.time() - t0:.4f}s")

    print("Testing footprint discovery on Heuristics Miner Net...")
    t0 = time.time()
    try:
        fp_heur = footprints_discovery.apply(net_heur, im_heur, parameters={"max_elab_time": 2})
        print(f"Heuristics Miner Net footprints discovered in {time.time() - t0:.4f}s")
    except Exception as e:
        print(f"Error on Heuristics Miner Net footprints: {e}")

if __name__ == '__main__':
    test()
