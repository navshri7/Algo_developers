import argparse
import csv
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import os

RESULTS_FOLDER = "results"

def load_graph(path):
    G = nx.DiGraph()
    with open(path, "r") as f:
        for line in f:
            u, v = line.strip().split()
            G.add_edge(int(u), int(v))
    return G

def load_scores(algo):
    file_map = {
        "degree": "degree_results.csv",
        "bridging": "bridging_results.csv",
        "hits": "hits_results.csv"
    }
    scores = {}
    file_path = os.path.join(RESULTS_FOLDER, file_map[algo])

    with open(file_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if algo == "degree":
                scores[int(row["Node"])] = float(row["TotalDegree"])
            elif algo == "bridging":
                scores[int(row["Node"])] = float(row["BridgingCentrality"])
            elif algo == "hits":
                scores[int(row["Node"])] = float(row["Authority"])
    return scores

def run_score_degree_bias(graph_path, algorithm):
    os.makedirs("plots", exist_ok=True)

    print(f"\nLoading graph: {graph_path}")
    G = load_graph(graph_path)

    print(f"Loading {algorithm} scores...")
    scores = load_scores(algorithm)

    x_degree = []
    y_score = []

    for node in G.nodes():
        deg = G.in_degree(node) + G.out_degree(node)
        if node in scores:
            x_degree.append(deg)
            y_score.append(scores[node])

    x = np.array(x_degree)
    y = np.array(y_score)
    corr = np.corrcoef(x, y)[0, 1]
    print(f"Pearson correlation (degree vs {algorithm}) = {corr:.4f}")

    plt.figure(figsize=(8, 6))
    plt.scatter(x, y, s=8, alpha=0.6)
    plt.xlabel("Node Degree")
    plt.ylabel(f"{algorithm.capitalize()} Score")
    plt.title(f"Degree Bias — {algorithm.capitalize()} (corr={corr:.4f})")

    z = np.polyfit(x, y, 1)
    p = np.poly1d(z)
    plt.plot(x, p(x), "r--", linewidth=2)

    out_path = f"plots/score_vs_degree_{algorithm}.png"
    plt.savefig(out_path, dpi=300)
    plt.close()

    print(f"Plot saved to: {out_path}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--graph", type=str, required=True)
    parser.add_argument("--algorithm", type=str, required=True,
                        choices=["degree", "bridging", "hits"])
    args = parser.parse_args()
    run_score_degree_bias(args.graph, args.algorithm)

if __name__ == "__main__":
    main()
