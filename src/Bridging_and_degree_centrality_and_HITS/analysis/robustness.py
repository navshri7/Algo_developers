import argparse
import random
import numpy as np
import networkx as nx
from scipy.stats import kendalltau
import matplotlib.pyplot as plt
from copy import deepcopy
def compute_scores(G, algorithm):
    if algorithm == "degree":
        c = nx.degree_centrality(G)
    elif algorithm == "bridge":
        bc = nx.betweenness_centrality(G, normalized=True)
        bridgeness = {node: bc[node] / (G.degree(node) + 1e-9) for node in G.nodes()}
        c = bridgeness
    elif algorithm == "hits":
        hubs, auths = nx.hits(G, max_iter=500, tol=1e-08, normalized=True)
        c = hubs
    else:
        raise ValueError("Unknown algorithm")
    return c

def kendall_rank_similarity(orig_scores, pert_scores):
    nodes = list(orig_scores.keys())
    orig_vals = [orig_scores[n] for n in nodes]
    pert_vals = [pert_scores[n] for n in nodes]
    tau, _ = kendalltau(orig_vals, pert_vals)
    return tau

def robustness_test(graph_path, algorithm):
    print(f"\nLoading graph: {graph_path}")
    G = nx.read_edgelist(graph_path, nodetype=str, create_using=nx.DiGraph)
    G = G.to_undirected()
    print(f"Computing original scores for {algorithm.upper()}...")
    original_scores = compute_scores(G, algorithm)
    removal_levels = [0, 1, 3, 5, 7, 10, 15, 20]  
    similarities = []
    edges = list(G.edges())
    for r in removal_levels:
        print(f"Removing {r}% edges and recomputing...")
        if r == 0:
            pert_scores = original_scores
        else:
            G_copy = deepcopy(G)
            remove_count = int(len(edges) * r / 100)
            to_remove = random.sample(edges, remove_count)
            G_copy.remove_edges_from(to_remove)
            pert_scores = compute_scores(G_copy, algorithm)

        tau = kendall_rank_similarity(original_scores, pert_scores)
        similarities.append(tau if tau is not None else 0)

    plt.plot(removal_levels, similarities, marker='o')
    plt.xlabel("% of edges removed")
    plt.ylabel("Kendall-τ similarity")
    plt.title(f"Robustness of {algorithm.upper()} Centrality")
    plt.grid(True)
    out_path = f"plots/robustness_{algorithm}.png"
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"\nRobustness plot saved to: {out_path}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--graph", type=str, required=True)
    parser.add_argument("--algorithm", type=str, choices=["degree", "bridge", "hits"], required=True)
    args = parser.parse_args()
    robustness_test(args.graph, args.algorithm)

if __name__ == "__main__":
    main()
