import subprocess
import time
def measure_time(command):
    start = time.time()
    subprocess.run(command, check=True)
    end = time.time()
    return end - start

def main():
    print("Measuring wall-clock execution time...\n")
    degree_cmd = ["./src/degree_centrality", "Data/cora/cora.cites", "results/degree_results.csv"]
    t_degree = measure_time(degree_cmd)
    print(f"Degree Centrality time: {t_degree:.4f} seconds")

    bridge_cmd = ["./src/bridging_centrality", "Data/cora/cora.cites", "results/bridging_results.csv"]
    t_bridge = measure_time(bridge_cmd)
    print(f"Bridging Centrality time: {t_bridge:.4f} seconds")

    hits_cmd = ["./src/hits_converge", "Data/cora/cora.cites", "results/hits_results.csv"]
    t_hits = measure_time(hits_cmd)
    print(f"HITS algorithm time: {t_hits:.4f} seconds")

    print("\nSummary:")
    print(f"{'Algorithm':<20}{'Time (s)':>10}")
    print(f"{'-'*30}")
    print(f"{'Degree Centrality':<20}{t_degree:>10.4f}")
    print(f"{'Bridging Centrality':<20}{t_bridge:>10.4f}")
    print(f"{'HITS':<20}{t_hits:>10.4f}")

if __name__ == "__main__":
    main()
