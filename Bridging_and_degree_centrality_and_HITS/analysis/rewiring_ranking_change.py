import networkx as nx
import numpy as np
import random
import matplotlib.pyplot as plt
import os
def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def load_graph(path):
    G = nx.read_edgelist(path, nodetype=int, create_using=nx.DiGraph)
    return G

def degree_rank(G):
    score = dict(G.degree())
    return sorted(score, key=score.get, reverse=True)

def bridging_rank(G):
    btw = nx.betweenness_centrality(G)
    bc = {}
    for node in G.nodes():
        deg = G.degree(node)
        if deg > 1:
            bc[node] = btw[node] * (1 / deg)
        else:
            bc[node] = 0
    return sorted(bc, key=bc.get, reverse=True)

def hits_rank(G):
    hubs, auth = nx.hits(G, max_iter=500, tol=1e-08)
    return sorted(auth, key=auth.get, reverse=True)

def rewire_graph(G, percent):
    H = G.copy()
    edges = list(H.edges())
    rewire_count = int(len(edges) * percent / 100)
    attempts = 0

    while rewire_count > 0 and attempts < 10_000:
        attempts += 1
        (u, v) = random.choice(edges)
        (x, y) = random.choice(edges)
        if (u, v) == (x, y):
            continue
        e1 = (u, y)
        e2 = (x, v)
        if u == y or x == v:
            continue
        if H.has_edge(*e1) or H.has_edge(*e2):
            continue
        if not H.has_edge(u, v) or not H.has_edge(x, y):
            continue
        H.remove_edge(u, v)
        H.remove_edge(x, y)
        H.add_edge(*e1)
        H.add_edge(*e2)
        edges.remove((u, v))
        edges.remove((x, y))
        edges.append(e1)
        edges.append(e2)
        rewire_count -= 1

    return H

graph_path = "Data/cora/cora.cites"
G = load_graph(graph_path)

percentages = [0, 2, 5, 7, 10, 15]  
K = 20  
algorithms = {
    "Degree": degree_rank,
    "Bridging": bridging_rank,
    "HITS": hits_rank
}
changes = {algo: [] for algo in algorithms}
original_ranks = {algo: fn(G)[:K] for algo, fn in algorithms.items()}
for p in percentages:
    print(f"Rewiring {p}% ...")

    if p == 0:
        H = G
    else:
        H = rewire_graph(G, p)
    for algo, fn in algorithms.items():
        new_rank = fn(H)[:K]
        overlap = len(set(original_ranks[algo]).intersection(set(new_rank)))
        change = K - overlap  
        changes[algo].append(change)
ensure_dir("plots")
plt.figure(figsize=(8, 5))

for algo, vals in changes.items():
    plt.plot(percentages, vals, marker="o", label=algo)

plt.xlabel("Percentage of edges rewired")
plt.ylabel("Number of replaced nodes in Top-K ranking")
plt.title("Ranking Change After Rewiring")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("plots/ranking_change_rewiring.png", dpi=300)
plt.close()
print("\nSaved plot → plots/ranking_change_rewiring.png")