#!/usr/bin/env python3
"""
Synthetic Graph Generator for K-Core Testing
Generates various graph types with different sizes and densities
"""

import networkx as nx
import random
import os
from pathlib import Path

def write_edge_list(G, filename):
    """Write graph in simple edge list format"""
    edges = list(G.edges())
    with open(filename, 'w') as f:
        f.write(f"{G.number_of_nodes()} {len(edges)}\n")
        for u, v in edges:
            # Convert to 1-indexed
            f.write(f"{u+1} {v+1}\n")

def generate_erdos_renyi(n, p, name):
    """Generate Erdős-Rényi random graph"""
    G = nx.erdos_renyi_graph(n, p)
    # Remove self-loops and ensure connected
    G.remove_edges_from(nx.selfloop_edges(G))
    return G, name

def generate_barabasi_albert(n, m, name):
    """Generate Barabási-Albert scale-free graph"""
    G = nx.barabasi_albert_graph(n, m)
    return G, name

def generate_watts_strogatz(n, k, p, name):
    """Generate Watts-Strogatz small-world graph"""
    G = nx.watts_strogatz_graph(n, k, p)
    return G, name

def generate_powerlaw_cluster(n, m, p, name):
    """Generate powerlaw cluster graph"""
    G = nx.powerlaw_cluster_graph(n, m, p)
    return G, name

def generate_dense_cliques(num_cliques, clique_size, inter_edges, name):
    """Generate graph with dense cliques connected by sparse edges"""
    G = nx.Graph()
    node_id = 0
    
    # Create cliques
    clique_nodes = []
    for i in range(num_cliques):
        clique = list(range(node_id, node_id + clique_size))
        clique_nodes.append(clique)
        for u in clique:
            for v in clique:
                if u < v:
                    G.add_edge(u, v)
        node_id += clique_size
    
    # Add inter-clique edges
    for _ in range(inter_edges):
        c1, c2 = random.sample(range(num_cliques), 2)
        u = random.choice(clique_nodes[c1])
        v = random.choice(clique_nodes[c2])
        G.add_edge(u, v)
    
    return G, name

def generate_known_kcore_graph():
    """Generate a small graph with known k-core structure for verification"""
    G = nx.Graph()
    
    # Create a 5-core (complete graph K6)
    core5 = list(range(6))
    for i in core5:
        for j in core5:
            if i < j:
                G.add_edge(i, j)
    
    # Add a 3-core connected to 5-core
    core3 = list(range(6, 10))
    for i in core3:
        for j in core3:
            if i < j:
                G.add_edge(i, j)
    # Connect to 5-core
    G.add_edge(5, 6)
    G.add_edge(5, 7)
    
    # Add a 2-core (cycle)
    core2 = list(range(10, 15))
    for i in range(len(core2)):
        G.add_edge(core2[i], core2[(i+1) % len(core2)])
    G.add_edge(core2[0], core2[2])  # Extra edge
    # Connect to 3-core
    G.add_edge(9, 10)
    
    # Add a 1-core (star)
    center = 15
    leaves = list(range(16, 20))
    for leaf in leaves:
        G.add_edge(center, leaf)
    G.add_edge(center, 14)  # Connect to 2-core
    
    return G, "known_structure"

def generate_verification_graphs():
    """Generate small graphs for manual verification"""
    graphs = []
    
    # Simple path
    G = nx.path_graph(5)
    graphs.append((G, "path_5"))
    
    # Simple cycle
    G = nx.cycle_graph(6)
    graphs.append((G, "cycle_6"))
    
    # Complete graph
    G = nx.complete_graph(7)
    graphs.append((G, "complete_7"))
    
    # Star graph
    G = nx.star_graph(8)
    graphs.append((G, "star_9"))
    
    # Known structure
    graphs.append(generate_known_kcore_graph())
    
    return graphs

def main():
    output_dir = Path("data/synthetic_graphs")
    output_dir.mkdir(exist_ok=True, parents=True)
    
    print("Generating synthetic test graphs...")
    print("=" * 60)
    
    all_graphs = []
    
    # 1. Verification graphs (small, known structure)
    print("\n1. Verification Graphs (small, known k-core)")
    verify_graphs = generate_verification_graphs()
    for G, name in verify_graphs:
        filename = output_dir / f"verify_{name}.txt"
        write_edge_list(G, filename)
        all_graphs.append((G, name))
        print(f"   ✓ {name}: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    
    # 2. Small graphs for testing (100-1000 nodes)
    print("\n2. Small Test Graphs (100-1000 nodes)")
    small_configs = [
        (100, 0.05, "er_100_sparse"),
        (100, 0.2, "er_100_dense"),
        (500, 0.01, "er_500_sparse"),
        (500, 0.05, "er_500_dense"),
        (1000, 0.005, "er_1000_sparse"),
        (1000, 0.02, "er_1000_dense"),
    ]
    
    for n, p, name in small_configs:
        G, gname = generate_erdos_renyi(n, p, name)
        filename = output_dir / f"{gname}.txt"
        write_edge_list(G, filename)
        all_graphs.append((G, gname))
        print(f"   ✓ {gname}: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    
    # 3. Medium graphs (5000-10000 nodes)
    print("\n3. Medium Test Graphs (5000-10000 nodes)")
    medium_configs = [
        (5000, 0.001, "er_5k_sparse"),
        (5000, 0.003, "er_5k_dense"),
        (10000, 0.0005, "er_10k_sparse"),
        (10000, 0.001, "er_10k_dense"),
    ]
    
    for n, p, name in medium_configs:
        G, gname = generate_erdos_renyi(n, p, name)
        filename = output_dir / f"{gname}.txt"
        write_edge_list(G, filename)
        all_graphs.append((G, gname))
        print(f"   ✓ {gname}: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    
    # 4. Scale-free graphs (Barabási-Albert)
    print("\n4. Scale-Free Graphs (Barabási-Albert)")
    ba_configs = [
        (1000, 3, "ba_1k_m3"),
        (1000, 5, "ba_1k_m5"),
        (5000, 3, "ba_5k_m3"),
        (5000, 5, "ba_5k_m5"),
        (10000, 3, "ba_10k_m3"),
    ]
    
    for n, m, name in ba_configs:
        G, gname = generate_barabasi_albert(n, m, name)
        filename = output_dir / f"{gname}.txt"
        write_edge_list(G, filename)
        all_graphs.append((G, gname))
        print(f"   ✓ {gname}: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    
    # 5. Small-world graphs (Watts-Strogatz)
    print("\n5. Small-World Graphs (Watts-Strogatz)")
    ws_configs = [
        (1000, 6, 0.1, "ws_1k_k6_p01"),
        (1000, 10, 0.3, "ws_1k_k10_p03"),
        (5000, 6, 0.1, "ws_5k_k6_p01"),
    ]
    
    for n, k, p, name in ws_configs:
        G, gname = generate_watts_strogatz(n, k, p, name)
        filename = output_dir / f"{gname}.txt"
        write_edge_list(G, filename)
        all_graphs.append((G, gname))
        print(f"   ✓ {gname}: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    
    # 6. Dense clique structures
    print("\n6. Clique-Based Graphs")
    clique_configs = [
        (5, 20, 10, "cliques_5x20"),
        (10, 15, 20, "cliques_10x15"),
        (20, 10, 50, "cliques_20x10"),
    ]
    
    for num_cliques, clique_size, inter_edges, name in clique_configs:
        G, gname = generate_dense_cliques(num_cliques, clique_size, inter_edges, name)
        filename = output_dir / f"{gname}.txt"
        write_edge_list(G, filename)
        all_graphs.append((G, gname))
        print(f"   ✓ {gname}: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    
    # 7. Power-law cluster graphs
    print("\n7. Power-Law Cluster Graphs")
    plc_configs = [
        (1000, 3, 0.1, "plc_1k_m3_p01"),
        (5000, 4, 0.2, "plc_5k_m4_p02"),
    ]
    
    for n, m, p, name in plc_configs:
        G, gname = generate_powerlaw_cluster(n, m, p, name)
        filename = output_dir / f"{gname}.txt"
        write_edge_list(G, filename)
        all_graphs.append((G, gname))
        print(f"   ✓ {gname}: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    
    print("\n" + "=" * 60)
    print(f"Generated {len(all_graphs)} synthetic graphs")
    print(f"Output directory: {output_dir.absolute()}")
    
    # Create a manifest
    with open(output_dir / "MANIFEST.txt", 'w') as f:
        f.write("Synthetic Graph Manifest\n")
        f.write("=" * 60 + "\n\n")
        for G, name in all_graphs:
            density = (2.0 * G.number_of_edges()) / (G.number_of_nodes() * (G.number_of_nodes() - 1))
            avg_degree = (2.0 * G.number_of_edges()) / G.number_of_nodes()
            f.write(f"{name}\n")
            f.write(f"  Nodes: {G.number_of_nodes()}\n")
            f.write(f"  Edges: {G.number_of_edges()}\n")
            f.write(f"  Avg Degree: {avg_degree:.2f}\n")
            f.write(f"  Density: {density:.6f}\n\n")

if __name__ == "__main__":
    main()
