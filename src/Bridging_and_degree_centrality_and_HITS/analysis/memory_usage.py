import subprocess
import psutil
import time
def measure_memory(command):
    """Run command and measure peak memory usage in MB."""
    proc = subprocess.Popen(command)
    p = psutil.Process(proc.pid)
    peak_mem = 0
    while proc.poll() is None:
        try:
            mem = p.memory_info().rss / (1024 * 1024) 
            if mem > peak_mem:
                peak_mem = mem
        except psutil.NoSuchProcess:
            break
        time.sleep(0.01)  
    proc.wait()
    return peak_mem

def main():
    print("Measuring memory usage for algorithms...")
    degree_cmd = ["./src/degree_centrality", "Data/cora/cora.cites", "results/degree_results.csv"]
    bridging_cmd = ["./src/bridging_centrality", "Data/cora/cora.cites", "results/bridging_results.csv"]
    hits_cmd = ["./src/hits_converge", "Data/cora/cora.cites", "results/hits_results.csv"]
    
    t0 = time.time()
    mem_degree = measure_memory(degree_cmd)
    print(f"Degree Centrality peak memory: {mem_degree:.2f} MB")

    t1 = time.time()
    mem_bridging = measure_memory(bridging_cmd)
    print(f"Bridging Centrality peak memory: {mem_bridging:.2f} MB")

    t2 = time.time()
    mem_hits = measure_memory(hits_cmd)
    print(f"HITS Centrality peak memory: {mem_hits:.2f} MB")

if __name__ == "__main__":
    main()
