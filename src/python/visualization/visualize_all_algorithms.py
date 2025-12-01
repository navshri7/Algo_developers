#!/usr/bin/env python3
"""
Comprehensive Node Visualization for All Algorithms
Visualizes node rankings and selections from all 4 algorithms:
- K-Core, Betweenness (Exact), Katz, Eigenvector Centrality
Includes graph drawings, node coloring, and animated GIFs
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
import networkx as nx
from matplotlib.animation import FuncAnimation, PillowWriter
import re
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (16, 12)
plt.rcParams['font.size'] = 9

# Algorithm metadata - ALL 9 ALGORITHMS
ALGORITHMS = {
    'kcore': {
        'name': 'K-Core',
        'color': 'YlOrRd',
        'result_dir': 'results/synthetic',
        'category': 'Foundational',
        'file_suffix': None
    },
    'betweenness': {
        'name': 'Betweenness',
        'color': 'viridis',
        'result_dir': 'results/betweenness/exact',
        'category': 'Foundational',
        'file_suffix': None
    },
    'degree': {
        'name': 'Degree',
        'color': 'Blues',
        'result_dir': 'results/degree_centrality',
        'category': 'Foundational',
        'file_suffix': None
    },
    'bridging': {
        'name': 'Bridging',
        'color': 'Greens',
        'result_dir': 'results/bridging_centrality',
        'category': 'Foundational',
        'file_suffix': None
    },
    'katz': {
        'name': 'Katz',
        'color': 'plasma',
        'result_dir': 'results/centrality/katz',
        'category': 'Frontier',
        'file_suffix': None
    },
    'eigenvector': {
        'name': 'Eigenvector',
        'color': 'cool',
        'result_dir': 'results/centrality/eigenvector',
        'category': 'Frontier',
        'file_suffix': None
    },
    'hits_hub': {
        'name': 'HITS (Hub)',
        'color': 'Reds',
        'result_dir': 'results/hits',
        'category': 'Frontier',
        'file_suffix': '_hub'
    },
    'hits_auth': {
        'name': 'HITS (Auth)',
        'color': 'Oranges',
        'result_dir': 'results/hits',
        'category': 'Frontier',
        'file_suffix': '_authority'
    },
    'pagerank': {
        'name': 'PageRank',
        'color': 'magma',
        'result_dir': 'results/centrality/pagerank',
        'category': 'Frontier',
        'file_suffix': '_pagerank'
    }
}

def load_graph_from_file(filepath):
    """Load graph from edge list file"""
    G = nx.Graph()
    try:
        with open(filepath, 'r') as f:
            line = f.readline()
            parts = line.strip().split()
            n, m = int(parts[0]), int(parts[1])
            
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 2:
                    u, v = int(parts[0]) - 1, int(parts[1]) - 1
                    G.add_edge(u, v)
        
        return G
    except Exception as e:
        print(f"Error loading graph: {e}")
        return None

def parse_detailed_results(filepath):
    """Parse detailed results file to get node rankings and values"""
    rankings = {}
    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
            in_section = False
            skip_next = False
            rank_counter = 1
            
            for line in lines:
                line_stripped = line.strip()
                
                # Look for section start - handle multiple formats:
                # "=== Top 100 Vertices by Coreness ===" (K-Core)
                # "Top 10 by Total Degree:" (Degree)
                # "Top 10 by Bridging Centrality:" (Bridging)
                # "Top 10 by Hub Score:" (HITS Hub)
                # "Top 10 by Authority Score:" (HITS Auth)
                if not in_section and "Top" in line:
                    if "Vertices" in line:
                        # K-Core format with header row
                        in_section = True
                        skip_next = True
                        rank_counter = 1
                        continue
                    elif any(keyword in line for keyword in ["Total Degree", "Bridging Centrality", "Hub Score", "Authority Score", "Rank", "Betweenness"]):
                        # Other formats - no header row, data starts immediately
                        in_section = True
                        skip_next = False
                        rank_counter = 1
                        continue
                
                # Stop if we hit another "Top" section (for files with multiple sections)
                if in_section and line_stripped.startswith("Top"):
                    break
                
                # Skip header line (only for K-Core format)
                if skip_next:
                    skip_next = False
                    continue
                
                # Parse data lines
                if in_section and line_stripped:
                    # Skip separator lines
                    if line_stripped.startswith("==="):
                        in_section = False
                        continue
                    
                    # Skip empty lines or section headers
                    if not line_stripped or ("Rank" in line_stripped and not line_stripped[0].isdigit() and "Node" not in line_stripped):
                        continue
                    
                    # Try tab-separated format first (betweenness, k-core, etc.)
                    # Format: "1	62	11391541.943472"
                    parts = line_stripped.split('\t')
                    if len(parts) >= 3 and parts[0].isdigit():
                        try:
                            rank = int(parts[0])
                            node_id = int(parts[1]) - 1  # Convert to 0-indexed
                            value = float(parts[2])
                            rankings[node_id] = (rank, value)
                        except (ValueError, IndexError):
                            continue
                    elif len(parts) >= 2 and parts[0].isdigit():
                        # Some files might only have rank and node_id
                        try:
                            rank = int(parts[0])
                            node_id = int(parts[1]) - 1  # Convert to 0-indexed
                            rankings[node_id] = (rank, 0.0)  # Default value
                        except (ValueError, IndexError):
                            continue
                    else:
                        # Try space-separated format with "Node" prefix
                        # Format: "  1. Node 62: 709" or "1. Node 62: 709"
                        match = re.search(r'(\d+)\.\s*Node\s+(\d+):\s*([\d.]+)', line)
                        if match:
                            try:
                                rank = int(match.group(1))
                                node_id = int(match.group(2)) - 1  # Convert to 0-indexed
                                value = float(match.group(3))
                                rankings[node_id] = (rank, value)
                            except (ValueError, IndexError):
                                continue
    except Exception as e:
        pass
    
    return rankings

def visualize_all_algorithms_comparison(output_dir):
    """Create side-by-side comparison of all 4 algorithms on verification graphs"""
    print("Generating algorithm comparison visualizations...")
    
    # Verification graphs
    graphs_to_viz = [
        ('data/synthetic_graphs/verify_known_structure.txt', 'Known Structure'),
        ('data/synthetic_graphs/verify_complete_7.txt', 'Complete Graph K7'),
        ('data/synthetic_graphs/verify_cycle_6.txt', 'Cycle Graph'),
        ('data/synthetic_graphs/verify_star_9.txt', 'Star Graph'),
    ]
    
    for graph_file, graph_title in graphs_to_viz:
        if not Path(graph_file).exists():
            continue
        
        fig, axes = plt.subplots(2, 3, figsize=(21, 16))
        axes = axes.flatten()

        
        G = load_graph_from_file(graph_file)
        if G is None:
            continue
        
        graph_base = Path(graph_file).stem
        
        # Plot each algorithm
        for algo_idx, (algo_key, algo_info) in enumerate(ALGORITHMS.items()):
            if algo_idx >= len(axes):
                break
            
            ax = axes[algo_idx]
            
            # Find result file
            if algo_key == 'pagerank':
                result_file = Path(algo_info['result_dir']) / f"{graph_base}_pagerank_detailed.txt"
            elif algo_info.get('file_suffix'):
                result_file = Path(algo_info['result_dir']) / f"{graph_base}{algo_info['file_suffix']}_detailed.txt"
            else:
                result_file = Path(algo_info['result_dir']) / f"{graph_base}_detailed.txt"
            
            # Special handling for K-Core - check both synthetic and real_datasets
            if algo_key == 'kcore' and not result_file.exists():
                result_file = Path('results/real_datasets') / f"{graph_base}_detailed.txt"
            
            if not result_file.exists():
                ax.text(0.5, 0.5, f"{algo_info['name']}\n(No results)", 
                       ha='center', va='center', fontsize=12)
                ax.set_title(f"{algo_info['name']} - {graph_title}", fontsize=12, fontweight='bold')
                continue
            
            rankings = parse_detailed_results(str(result_file))
            
            if not rankings:
                ax.text(0.5, 0.5, f"{algo_info['name']}\n(Failed to parse)", 
                       ha='center', va='center', fontsize=12)
                ax.set_title(f"{algo_info['name']} - {graph_title}", fontsize=12, fontweight='bold')
                continue
            
            # Create layout
            pos = nx.spring_layout(G, k=0.5, iterations=50, seed=42)
            
            # Get node values
            node_values = np.zeros(len(G))
            for node_id, (rank, value) in rankings.items():
                if node_id < len(node_values):
                    node_values[node_id] = value
            
            # Node sizes based on rank
            node_sizes = []
            for node in G.nodes():
                if node in rankings:
                    rank, _ = rankings[node]
                    size = max(100, 1000 - rank * 50)
                else:
                    size = 100
                node_sizes.append(size)
            
            # Draw network
            nx.draw_networkx_edges(G, pos, ax=ax, alpha=0.2, width=1)
            
            nodes = nx.draw_networkx_nodes(G, pos, ax=ax, node_size=node_sizes,
                                          node_color=node_values, cmap=algo_info['color'],
                                          vmin=0, vmax=np.max(node_values) if np.max(node_values) > 0 else 1)
            
            nx.draw_networkx_labels(G, pos, ax=ax, font_size=8, font_weight='bold')
            
            plt.colorbar(nodes, ax=ax, label='Centrality Value')
            ax.set_title(f"{algo_info['name']} - {graph_title}", fontsize=12, fontweight='bold')
            ax.axis('off')
        
        plt.tight_layout()
        output_file = output_dir / f"comparison_{graph_base}.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"  ✓ Saved: {output_file.name}")
        plt.close()

def create_animated_comparison(output_dir):
    """Create animated GIFs comparing algorithms on verification graphs"""
    print("Generating animated comparisons...")
    
    graphs_to_animate = [
        ('data/synthetic_graphs/verify_known_structure.txt', 'known_structure'),
        ('data/synthetic_graphs/verify_complete_7.txt', 'complete_7'),
        ('data/synthetic_graphs/verify_cycle_6.txt', 'cycle_6'),
        ('data/synthetic_graphs/verify_star_9.txt', 'star_9'),
    ]
    
    for graph_file, graph_name in graphs_to_animate:
        if not Path(graph_file).exists():
            continue
        
        G = load_graph_from_file(graph_file)
        if G is None:
            continue
        
        graph_base = Path(graph_file).stem
        
        # Create animation showing all algorithms - use 3x3 grid for 9 algorithms
        fig, axes = plt.subplots(3, 3, figsize=(24, 20))
        axes = axes.flatten()
        
        pos = nx.spring_layout(G, k=0.5, iterations=50, seed=42)
        
        # Preload all data
        all_rankings = {}
        for algo_key, algo_info in ALGORITHMS.items():
            # Construct file path based on algorithm
            if algo_key == 'pagerank':
                result_file = Path(algo_info['result_dir']) / f"{graph_base}_pagerank_detailed.txt"
            elif algo_info.get('file_suffix'):
                result_file = Path(algo_info['result_dir']) / f"{graph_base}{algo_info['file_suffix']}_detailed.txt"
            else:
                result_file = Path(algo_info['result_dir']) / f"{graph_base}_detailed.txt"
            
            # Special handling for K-Core - check both synthetic and real_datasets
            if algo_key == 'kcore' and not result_file.exists():
                result_file = Path('results/real_datasets') / f"{graph_base}_detailed.txt"
            
            if result_file.exists():
                rankings = parse_detailed_results(str(result_file))
                all_rankings[algo_key] = rankings
                if not rankings:
                    print(f"  ⚠ {algo_info['name']}: File exists but no rankings extracted from {result_file}")
                else:
                    print(f"  ✓ {algo_info['name']}: Loaded {len(rankings)} nodes from {result_file.name}")
            else:
                all_rankings[algo_key] = {}
                print(f"  ⚠ {algo_info['name']}: File not found: {result_file}")

        
        def animate(frame):
            for ax in axes:
                ax.clear()
            
            # Show top N nodes for this frame
            top_n = min(frame + 1, 10)
            
            for algo_idx, (algo_key, algo_info) in enumerate(ALGORITHMS.items()):
                if algo_idx >= len(axes):
                    break
                
                ax = axes[algo_idx]
                rankings = all_rankings.get(algo_key, {})
                
                if not rankings:
                    ax.text(0.5, 0.5, f"{algo_info['name']}\n(No data)", 
                           ha='center', va='center', fontsize=12)
                    ax.set_title(f"{algo_info['name']} - Top {top_n}", fontsize=12, fontweight='bold')
                    ax.axis('off')
                    continue
                
                # Highlight top N nodes
                top_nodes = sorted(rankings.items(), key=lambda x: x[1][0])[:top_n]
                top_node_ids = set(node_id for node_id, _ in top_nodes)
                
                # Node colors
                node_colors = []
                for node in G.nodes():
                    if node in top_node_ids:
                        node_colors.append('red')
                    else:
                        node_colors.append('lightgray')
                
                # Node sizes
                node_sizes = []
                for node in G.nodes():
                    if node in rankings:
                        rank, _ = rankings[node]
                        size = max(100, 1000 - rank * 50)
                    else:
                        size = 100
                    node_sizes.append(size)
                
                # Draw
                nx.draw_networkx_edges(G, pos, ax=ax, alpha=0.2, width=1)
                nx.draw_networkx_nodes(G, pos, ax=ax, node_size=node_sizes,
                                      node_color=node_colors, alpha=0.8)
                nx.draw_networkx_labels(G, pos, ax=ax, font_size=8, font_weight='bold')
                
                ax.set_title(f"{algo_info['name']} - Top {top_n} Nodes", fontsize=12, fontweight='bold')
                ax.axis('off')
        
        # Create animation
        anim = FuncAnimation(fig, animate, frames=10, interval=500, repeat=True)
        
        output_file = output_dir / f"animation_all_{graph_name}.gif"
        writer = PillowWriter(fps=2)
        anim.save(output_file, writer=writer)
        print(f"  ✓ Saved: {output_file.name}")
        plt.close()

def create_algorithm_ranking_heatmap(output_dir):
    """Create heatmap showing how different algorithms rank the same nodes"""
    print("Generating ranking heatmap...")
    
    graphs_to_analyze = [
        ('data/synthetic_graphs/verify_known_structure.txt', 'known_structure'),
        ('data/synthetic_graphs/verify_complete_7.txt', 'complete_7'),
    ]
    
    for graph_file, graph_name in graphs_to_analyze:
        if not Path(graph_file).exists():
            continue
        
        G = load_graph_from_file(graph_file)
        if G is None:
            continue
        
        graph_base = Path(graph_file).stem
        
        # Load rankings from all algorithms
        all_rankings = {}
        for algo_key, algo_info in ALGORITHMS.items():
            if algo_key == 'pagerank':
                result_file = Path(algo_info['result_dir']) / f"{graph_base}_pagerank_detailed.txt"
            elif algo_info.get('file_suffix'):
                result_file = Path(algo_info['result_dir']) / f"{graph_base}{algo_info['file_suffix']}_detailed.txt"
            else:
                result_file = Path(algo_info['result_dir']) / f"{graph_base}_detailed.txt"
            
            # Special handling for K-Core - check both synthetic and real_datasets
            if algo_key == 'kcore' and not result_file.exists():
                result_file = Path('results/real_datasets') / f"{graph_base}_detailed.txt"
            
            if result_file.exists():
                all_rankings[algo_key] = parse_detailed_results(str(result_file))

        
        if not all_rankings:
            continue
        
        # Create ranking matrix
        num_nodes = len(G)
        ranking_matrix = np.zeros((len(ALGORITHMS), num_nodes))
        
        for algo_idx, (algo_key, algo_info) in enumerate(ALGORITHMS.items()):
            rankings = all_rankings.get(algo_key, {})
            for node_id, (rank, _) in rankings.items():
                if node_id < num_nodes:
                    ranking_matrix[algo_idx, node_id] = rank
        
        # Plot heatmap
        fig, ax = plt.subplots(figsize=(14, 6))
        
        algo_names = [ALGORITHMS[k]['name'] for k in ALGORITHMS.keys()]
        im = ax.imshow(ranking_matrix, cmap='RdYlGn_r', aspect='auto')
        
        ax.set_yticks(range(len(algo_names)))
        ax.set_yticklabels(algo_names)
        ax.set_xlabel('Node ID', fontsize=12, fontweight='bold')
        ax.set_ylabel('Algorithm', fontsize=12, fontweight='bold')
        ax.set_title(f'Node Rankings Heatmap - {graph_name}', fontsize=14, fontweight='bold')
        
        plt.colorbar(im, ax=ax, label='Rank (lower=better)')
        plt.tight_layout()
        
        output_file = output_dir / f"ranking_heatmap_{graph_name}.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"  ✓ Saved: {output_file.name}")
        plt.close()

def create_top_nodes_comparison(output_dir):
    """Create bar charts comparing top nodes across algorithms"""
    print("Generating top nodes comparison...")
    
    graphs_to_compare = [
        ('data/synthetic_graphs/verify_known_structure.txt', 'known_structure'),
        ('data/synthetic_graphs/verify_complete_7.txt', 'complete_7'),
    ]
    
    for graph_file, graph_name in graphs_to_compare:
        if not Path(graph_file).exists():
            continue
        
        graph_base = Path(graph_file).stem
        
        fig, axes = plt.subplots(2, 3, figsize=(21, 12))
        axes = axes.flatten()

        
        for algo_idx, (algo_key, algo_info) in enumerate(ALGORITHMS.items()):
            if algo_idx >= len(axes):
                break
            
            ax = axes[algo_idx]
            if algo_key == 'pagerank':
                result_file = Path(algo_info['result_dir']) / f"{graph_base}_pagerank_detailed.txt"
            elif algo_info.get('file_suffix'):
                result_file = Path(algo_info['result_dir']) / f"{graph_base}{algo_info['file_suffix']}_detailed.txt"
            else:
                result_file = Path(algo_info['result_dir']) / f"{graph_base}_detailed.txt"
            
            # Special handling for K-Core - check both synthetic and real_datasets
            if algo_key == 'kcore' and not result_file.exists():
                result_file = Path('results/real_datasets') / f"{graph_base}_detailed.txt"

            
            if not result_file.exists():
                ax.text(0.5, 0.5, f"{algo_info['name']}\n(No data)", 
                       ha='center', va='center')
                ax.set_title(algo_info['name'])
                continue
            
            rankings = parse_detailed_results(str(result_file))
            
            if not rankings:
                ax.text(0.5, 0.5, f"{algo_info['name']}\n(No rankings)", 
                       ha='center', va='center')
                ax.set_title(algo_info['name'])
                continue
            
            # Get top 10 nodes
            top_nodes = sorted(rankings.items(), key=lambda x: x[1][0])[:10]
            node_ids = [f"N{n+1}" for n, _ in top_nodes]
            values = [v for _, (_, v) in top_nodes]
            
            # Plot
            colors = sns.color_palette(algo_info['color'], len(node_ids))
            ax.barh(node_ids, values, color=colors)
            ax.set_xlabel('Centrality Value', fontsize=11, fontweight='bold')
            ax.set_title(f"{algo_info['name']} - Top 10 Nodes", fontsize=12, fontweight='bold')
            ax.invert_yaxis()
        
        plt.tight_layout()
        output_file = output_dir / f"top_nodes_{graph_name}.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"  ✓ Saved: {output_file.name}")
        plt.close()

def print_top_10_all_algorithms():
    """Print top 10 nodes for each algorithm side-by-side (REAL GRAPHS ONLY)"""
    print("\n" + "=" * 130)
    print("TOP 10 NODES BY EACH ALGORITHM - FOUNDATIONAL vs FRONTIER (REAL GRAPHS)")
    print("=" * 130)
    print()
    
    # Real graphs only - for foundational vs frontier comparison
    graphs = [
        ('data/converted_datasets/cit-DBLP.txt', 'cit-DBLP'),
        ('data/converted_datasets/cit-HepTh.txt', 'cit-HepTh'),
        ('data/converted_datasets/citeseer.txt', 'CiteSeer'),
        ('data/converted_datasets/cora.txt', 'Cora'),
    ]
    
    for graph_file, graph_name in graphs:
        if not Path(graph_file).exists():
            continue
        
        print(f"\n{graph_name}")
        print("-" * 130)
        
        graph_base = Path(graph_file).stem
        
        # Load top 10 from each algorithm
        all_top_10 = {}
        
        algorithms = [
            ('K-Core', 'results/synthetic'),
            ('Betweenness', 'results/betweenness/exact'),
            ('Katz', 'results/centrality/katz'),
            ('Eigenvector', 'results/centrality/eigenvector'),
            ('PageRank', 'results/centrality/pagerank'),
        ]
        
        for algo_name, result_dir in algorithms:
            if algo_name == 'PageRank':
                result_file = Path(result_dir) / f"{graph_base}_pagerank_detailed.txt"
            else:
                result_file = Path(result_dir) / f"{graph_base}_detailed.txt"
            
            if result_file.exists():
                rankings = extract_top_nodes_with_values(result_file, 10)
                all_top_10[algo_name] = rankings
            else:
                all_top_10[algo_name] = []

        
        # Print side-by-side
        max_rows = max(len(v) for v in all_top_10.values()) if all_top_10.values() else 0
        
        # Header
        header = ""
        for algo_name in all_top_10.keys():
            header += f"{algo_name:25} | "
        print(header)
        print("-" * 130)
        
        # Rows
        for row_idx in range(max_rows):
            row_str = ""
            for algo_name in all_top_10.keys():
                if row_idx < len(all_top_10[algo_name]):
                    node_id, value = all_top_10[algo_name][row_idx]
                    row_str += f"Rank {row_idx+1:2d}: N{node_id:2d}({value:8.5f}) | "
                else:
                    row_str += f"{'':28} | "
            print(row_str)
        
        print()

def extract_top_nodes_with_values(filepath, k=10):
    """Extract top k nodes with their values from detailed results file"""
    nodes = []
    try:
        with open(filepath, 'r') as f:
            in_section = False
            count = 0
            for line in f:
                if "Top" in line or "Rank" in line:
                    in_section = True
                    continue
                if in_section and line.strip() and not line.startswith("==="):
                    parts = line.strip().split('\t')
                    if len(parts) >= 3 and parts[0].isdigit():
                        try:
                            node_id = int(parts[1])
                            value = float(parts[2])
                            nodes.append((node_id, value))
                            count += 1
                            if count >= k:
                                break
                        except (ValueError, IndexError):
                            continue
    except:
        pass
    
    return nodes

def main():
    print("=" * 80)
    print("COMPREHENSIVE NODE VISUALIZATION - ALL ALGORITHMS")
    print("=" * 80)
    print()
    
    # Create output directory
    output_dir = Path("results/node_visualizations")
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # Generate all visualizations
    visualize_all_algorithms_comparison(output_dir)
    print()
    
    create_algorithm_ranking_heatmap(output_dir)
    print()
    
    create_top_nodes_comparison(output_dir)
    print()
    
    create_animated_comparison(output_dir)
    print()
    
    # Print final comparison
    print_top_10_all_algorithms()
    
    print("=" * 80)
    print("Visualization complete!")
    print("=" * 80)
    print(f"\nAll outputs saved to: {output_dir.absolute()}")
    print("\nGenerated files:")
    print("  - comparison_*.png (Side-by-side algorithm comparison)")
    print("  - ranking_heatmap_*.png (Node ranking heatmaps)")
    print("  - top_nodes_*.png (Top 10 nodes bar charts)")
    print("  - animation_all_*.gif (Animated algorithm comparison)")
    print()

if __name__ == "__main__":
    main()
