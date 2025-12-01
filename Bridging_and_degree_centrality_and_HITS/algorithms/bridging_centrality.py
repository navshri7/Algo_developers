import networkx as nx
import numpy as np

def bridging_centrality(G, k=None, normalized=True):
    betweenness = nx.betweenness_centrality(G, normalized=normalized)
    bridging_coeff = {}
    for v in G.nodes():
        degree_v = G.degree(v)
        if degree_v == 0:
            bridging_coeff[v] = 0
            continue
        neigh = list(G.neighbors(v))
        denom = sum(1 / G.degree(u) for u in neigh if G.degree(u) > 0)

        if denom == 0:
            bridging_coeff[v] = 0
        else:
            bridging_coeff[v] = (1 / degree_v) / denom
    bridging_cent = {v: betweenness[v] * bridging_coeff[v] for v in G.nodes()}
    sorted_scores = sorted(bridging_cent.items(), key=lambda x: x[1], reverse=True)

    if k:
        return sorted_scores[:k]
    return sorted_scores


def run_bridging_centrality(graph_path, k=10):
    """
    Loads graph from edgelist and prints top-k bridging centrality nodes.
    """
    print(f"Loading graph from: {graph_path}")
    G = nx.read_edgelist(graph_path, nodetype=str)

    print("\nComputing bridging centrality...")
    scores = bridging_centrality(G, k=k)
    
    print("\nTop bridging nodes:")
    for rank, (node, score) in enumerate(scores, start=1):
        print(f"{rank}. {node} — {score:.6f}")

    return scores

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--graph", type=str, required=True, help="Path to edge list file")
    parser.add_argument("--k", type=int, default=10, help="Top-k nodes to show")
    args = parser.parse_args()

    run_bridging_centrality(args.graph, args.k)
