#!/usr/bin/env python3
"""
Node Visualization for Graph Algorithms
Visualizes node rankings and selections from k-core and betweenness algorithms
Includes graph drawings with node coloring based on centrality measures
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
import networkx as nx
from matplotlib.animation import FuncAnimation, PillowWriter
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 10)
plt.rcParams['font.size'] = 9

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
                    u, v = int(parts[0]) - 1, int(parts[1]) - 1  # Convert to 0-indexed
                    G.add_edge(u, v)
        
        return G
    except Exception as e:
        print(f"Error loading graph: {e}")
        return None

def parse_detailed_results(filepath):
    """Parse detailed results file to get node rankings"""
    rankings = {}
    try:
        with open(filepath, 'r') as f:
            in_section = False
            for line in f:
                if "Top" in line or "Rank" in line:
                    in_section = True
                    continue
                if in_section and line.strip() and not line.startswith("==="):
                    parts = line.strip().split('\t')
                    if len(parts) >= 3 and parts[0].isdigit():
                        try:
                            rank = int(parts[0])
                            node_id = int(parts[1]) - 1  # Convert to 0-indexed
                            value = float(parts[2])
                            rankings[node_id] = (rank, value)
                        except (ValueError, IndexError):
                            continue
    except Exception as e:
        print(f"Error parsing results: {e}")
    
    return rankings

def visualize_node_rankings_kcore(output_dir):
    """Visualize k-core node rankings for small graphs"""
    fig, axes = plt.subplots(2, 2, figsize=(16, 14))
    axes = axes.flatten()
    
    # Select interesting small graphs
    graphs_to_viz = [
        ('synthetic_graphs/verify_known_structure.txt', 'results/synthetic/verify_known_structure_detailed.txt', 'Known Structure'),
        ('synthetic_graphs/verify_complete_7.txt', 'results/synthetic/verify_complete_7_detailed.txt', 'Complete Graph K7'),
        ('synthetic_graphs/verify_cycle_6.txt', 'results/synthetic/verify_cycle_6_detailed.txt', 'Cycle Graph'),
        ('synthetic_graphs/verify_star_9.txt', 'results/synthetic/verify_star_9_detailed.txt', 'Star Graph'),
    ]
    
    for idx, (graph_file, result_file, title) in enumerate(graphs_to_viz):
        if idx >= len(axes):
            break
        
        if not Path(graph_file).exists() or not Path(result_file).exists():
            axes[idx].text(0.5, 0.5, f'{title}\n(Data not available)', 
                          ha='center', va='center', fontsize=12)
            axes[idx].set_title(title, fontsize=12, fontweight='bold')
            continue
        
        G = load_graph_from_file(graph_file)
        rankings = parse_detailed_results(result_file)
        
        if G is None or not rankings:
            axes[idx].text(0.5, 0.5, f'{title}\n(Failed to load)', 
                          ha='center', va='center', fontsize=12)
            axes[idx].set_title(title, fontsize=12, fontweight='bold')
            continue
        
        # Create layout
        pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
        
        # Get k-core values for coloring
        kcore_values = nx.core_number(G)
        node_colors = [kcore_values.get(i, 0) for i in range(len(G))]
        node_sizes = [300 + 100 * rankings.get(i, (0, 0))[0] for i in range(len(G))]
        
        # Draw graph
        nx.draw_networkx_edges(G, pos, ax=axes[idx], alpha=0.3, width=1)
        nodes = nx.draw_networkx_nodes(G, pos, node_color=node_colors, 
                                       node_size=node_sizes, cmap='YlOrRd',
                                       ax=axes[idx], edgecolors='black', linewidths=1.5)
        
        # Draw labels
        labels = {i: str(i) for i in range(len(G))}
        nx.draw_networkx_labels(G, pos, labels, font_size=8, ax=axes[idx])
        
        axes[idx].set_title(f'{title}\n(Node size = rank, Color = k-core value)', 
                           fontsize=12, fontweight='bold')
        axes[idx].axis('off')
        
        # Add colorbar
        sm = plt.cm.ScalarMappable(cmap='YlOrRd', 
                                   norm=plt.Normalize(vmin=min(node_colors), 
                                                     vmax=max(node_colors)))
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=axes[idx], fraction=0.046, pad=0.04)
        cbar.set_label('K-Core Value', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'kcore_node_rankings.png', dpi=300, bbox_inches='tight')
    print(f"  ✓ Saved: kcore_node_rankings.png")
    plt.close()

def visualize_node_rankings_betweenness(output_dir):
    """Visualize betweenness node rankings for small graphs"""
    fig, axes = plt.subplots(2, 2, figsize=(16, 14))
    axes = axes.flatten()
    
    graphs_to_viz = [
        ('synthetic_graphs/verify_known_structure.txt', 
         'results/betweenness/exact/verify_known_structure_detailed.txt',
         'results/betweenness/approximate/verify_known_structure_approx_detailed.txt',
         'Known Structure'),
        ('synthetic_graphs/verify_complete_7.txt',
         'results/betweenness/exact/verify_complete_7_detailed.txt',
         'results/betweenness/approximate/verify_complete_7_approx_detailed.txt',
         'Complete Graph K7'),
        ('synthetic_graphs/verify_cycle_6.txt',
         'results/betweenness/exact/verify_cycle_6_detailed.txt',
         'results/betweenness/approximate/verify_cycle_6_approx_detailed.txt',
         'Cycle Graph'),
        ('synthetic_graphs/verify_star_9.txt',
         'results/betweenness/exact/verify_star_9_detailed.txt',
         'results/betweenness/approximate/verify_star_9_approx_detailed.txt',
         'Star Graph'),
    ]
    
    for idx, (graph_file, exact_file, approx_file, title) in enumerate(graphs_to_viz):
        if idx >= len(axes):
            break
        
        if not Path(graph_file).exists():
            axes[idx].text(0.5, 0.5, f'{title}\n(Graph not found)', 
                          ha='center', va='center', fontsize=12)
            axes[idx].set_title(title, fontsize=12, fontweight='bold')
            continue
        
        G = load_graph_from_file(graph_file)
        exact_rankings = parse_detailed_results(exact_file) if Path(exact_file).exists() else {}
        
        if G is None:
            axes[idx].text(0.5, 0.5, f'{title}\n(Failed to load)', 
                          ha='center', va='center', fontsize=12)
            axes[idx].set_title(title, fontsize=12, fontweight='bold')
            continue
        
        # Create layout
        pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
        
        # Get betweenness centrality for coloring
        bc = nx.betweenness_centrality(G)
        node_colors = [bc.get(i, 0) for i in range(len(G))]
        node_sizes = [300 + 100 * exact_rankings.get(i, (0, 0))[0] for i in range(len(G))]
        
        # Draw graph
        nx.draw_networkx_edges(G, pos, ax=axes[idx], alpha=0.3, width=1)
        nodes = nx.draw_networkx_nodes(G, pos, node_color=node_colors,
                                       node_size=node_sizes, cmap='viridis',
                                       ax=axes[idx], edgecolors='black', linewidths=1.5)
        
        # Draw labels
        labels = {i: str(i) for i in range(len(G))}
        nx.draw_networkx_labels(G, pos, labels, font_size=8, ax=axes[idx])
        
        axes[idx].set_title(f'{title}\n(Node size = rank, Color = betweenness centrality)',
                           fontsize=12, fontweight='bold')
        axes[idx].axis('off')
        
        # Add colorbar
        sm = plt.cm.ScalarMappable(cmap='viridis',
                                   norm=plt.Normalize(vmin=min(node_colors),
                                                     vmax=max(node_colors)))
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=axes[idx], fraction=0.046, pad=0.04)
        cbar.set_label('Betweenness', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'betweenness_node_rankings.png', dpi=300, bbox_inches='tight')
    print(f"  ✓ Saved: betweenness_node_rankings.png")
    plt.close()

def create_animation_kcore(graph_file, result_file, output_file, title):
    """Create animation showing k-core decomposition process"""
    G = load_graph_from_file(graph_file)
    rankings = parse_detailed_results(result_file)
    
    if G is None or not rankings:
        return False
    
    # Get k-core values
    kcore_values = nx.core_number(G)
    max_kcore = max(kcore_values.values()) if kcore_values else 0
    
    # Create layout
    pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
    
    # Sort nodes by k-core value (decomposition order)
    sorted_nodes = sorted(range(len(G)), key=lambda i: kcore_values.get(i, 0))
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    def update(frame):
        ax.clear()
        
        # Nodes to highlight up to this frame
        highlighted = set(sorted_nodes[:frame + 1])
        
        # Color nodes based on whether they're highlighted
        node_colors = ['#FF6B6B' if i in highlighted else '#E0E0E0' for i in range(len(G))]
        node_sizes = [400 if i in highlighted else 200 for i in range(len(G))]
        
        # Draw graph
        nx.draw_networkx_edges(G, pos, ax=ax, alpha=0.2, width=1)
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes,
                              ax=ax, edgecolors='black', linewidths=1)
        
        # Draw labels
        labels = {i: f"{i}\n(k={kcore_values.get(i, 0)})" for i in range(len(G))}
        nx.draw_networkx_labels(G, pos, labels, font_size=7, ax=ax)
        
        ax.set_title(f'{title}\nK-Core Decomposition (Step {frame + 1}/{len(G)})',
                    fontsize=14, fontweight='bold')
        ax.axis('off')
    
    anim = FuncAnimation(fig, update, frames=len(G), interval=500, repeat=True)
    
    try:
        writer = PillowWriter(fps=2)
        anim.save(output_file, writer=writer)
        plt.close()
        return True
    except Exception as e:
        print(f"  ✗ Error creating animation: {e}")
        plt.close()
        return False

def create_animation_betweenness(graph_file, result_file, output_file, title):
    """Create animation showing betweenness centrality ranking"""
    G = load_graph_from_file(graph_file)
    rankings = parse_detailed_results(result_file)
    
    if G is None or not rankings:
        return False
    
    # Create layout
    pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
    
    # Sort nodes by betweenness rank
    sorted_nodes = sorted(range(len(G)), 
                         key=lambda i: rankings.get(i, (float('inf'), 0))[0])
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    def update(frame):
        ax.clear()
        
        # Nodes to highlight up to this frame
        highlighted = set(sorted_nodes[:frame + 1])
        
        # Color nodes based on rank
        node_colors = []
        for i in range(len(G)):
            if i in highlighted:
                rank = rankings.get(i, (0, 0))[0]
                # Color gradient from green (high rank) to red (low rank)
                node_colors.append(plt.cm.RdYlGn(1 - rank / len(G)))
            else:
                node_colors.append('#E0E0E0')
        
        node_sizes = [400 if i in highlighted else 200 for i in range(len(G))]
        
        # Draw graph
        nx.draw_networkx_edges(G, pos, ax=ax, alpha=0.2, width=1)
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes,
                              ax=ax, edgecolors='black', linewidths=1)
        
        # Draw labels with betweenness values
        labels = {}
        for i in range(len(G)):
            if i in rankings:
                rank, value = rankings[i]
                labels[i] = f"{i}\n(#{rank})"
            else:
                labels[i] = str(i)
        
        nx.draw_networkx_labels(G, pos, labels, font_size=7, ax=ax)
        
        ax.set_title(f'{title}\nBetweenness Centrality Ranking (Step {frame + 1}/{len(G)})',
                    fontsize=14, fontweight='bold')
        ax.axis('off')
    
    anim = FuncAnimation(fig, update, frames=len(G), interval=500, repeat=True)
    
    try:
        writer = PillowWriter(fps=2)
        anim.save(output_file, writer=writer)
        plt.close()
        return True
    except Exception as e:
        print(f"  ✗ Error creating animation: {e}")
        plt.close()
        return False

def create_comparison_animation(graph_file, kcore_file, bc_exact_file, output_file, title):
    """Create side-by-side comparison animation"""
    G = load_graph_from_file(graph_file)
    kcore_rankings = parse_detailed_results(kcore_file)
    bc_rankings = parse_detailed_results(bc_exact_file)
    
    if G is None:
        return False
    
    # Create layout
    pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
    
    # Get max frames
    max_frames = max(len(kcore_rankings), len(bc_rankings))
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
    
    def update(frame):
        ax1.clear()
        ax2.clear()
        
        # K-Core visualization
        kcore_values = nx.core_number(G)
        highlighted_kcore = set(sorted(range(len(G)), 
                                      key=lambda i: kcore_values.get(i, 0))[:frame + 1])
        
        node_colors_kc = ['#FF6B6B' if i in highlighted_kcore else '#E0E0E0' 
                         for i in range(len(G))]
        node_sizes_kc = [400 if i in highlighted_kcore else 200 for i in range(len(G))]
        
        nx.draw_networkx_edges(G, pos, ax=ax1, alpha=0.2, width=1)
        nx.draw_networkx_nodes(G, pos, node_color=node_colors_kc, node_size=node_sizes_kc,
                              ax=ax1, edgecolors='black', linewidths=1)
        labels = {i: str(i) for i in range(len(G))}
        nx.draw_networkx_labels(G, pos, labels, font_size=8, ax=ax1)
        ax1.set_title(f'K-Core Decomposition\n(Step {frame + 1}/{max_frames})',
                     fontsize=12, fontweight='bold')
        ax1.axis('off')
        
        # Betweenness visualization
        sorted_bc = sorted(range(len(G)), 
                          key=lambda i: bc_rankings.get(i, (float('inf'), 0))[0])
        highlighted_bc = set(sorted_bc[:frame + 1])
        
        node_colors_bc = []
        for i in range(len(G)):
            if i in highlighted_bc:
                rank = bc_rankings.get(i, (0, 0))[0]
                node_colors_bc.append(plt.cm.RdYlGn(1 - rank / len(G)))
            else:
                node_colors_bc.append('#E0E0E0')
        
        node_sizes_bc = [400 if i in highlighted_bc else 200 for i in range(len(G))]
        
        nx.draw_networkx_edges(G, pos, ax=ax2, alpha=0.2, width=1)
        nx.draw_networkx_nodes(G, pos, node_color=node_colors_bc, node_size=node_sizes_bc,
                              ax=ax2, edgecolors='black', linewidths=1)
        nx.draw_networkx_labels(G, pos, labels, font_size=8, ax=ax2)
        ax2.set_title(f'Betweenness Centrality\n(Step {frame + 1}/{max_frames})',
                     fontsize=12, fontweight='bold')
        ax2.axis('off')
        
        fig.suptitle(f'{title} - Algorithm Comparison', fontsize=14, fontweight='bold')
    
    anim = FuncAnimation(fig, update, frames=max_frames, interval=500, repeat=True)
    
    try:
        writer = PillowWriter(fps=2)
        anim.save(output_file, writer=writer)
        plt.close()
        return True
    except Exception as e:
        print(f"  ✗ Error creating comparison animation: {e}")
        plt.close()
        return False

def main():
    print("=" * 70)
    print("Node Visualization for Graph Algorithms")
    print("=" * 70)
    print()
    
    # Create output directory
    viz_dir = Path("results/node_visualizations")
    viz_dir.mkdir(exist_ok=True, parents=True)
    
    # Generate static visualizations
    print("Generating static node ranking visualizations...")
    print("-" * 70)
    
    visualize_node_rankings_kcore(viz_dir)
    visualize_node_rankings_betweenness(viz_dir)
    
    print()
    print("Generating animated visualizations...")
    print("-" * 70)
    
    # Create animations for small graphs
    animations = [
        ('synthetic_graphs/verify_known_structure.txt',
         'results/synthetic/verify_known_structure_detailed.txt',
         'results/betweenness/exact/verify_known_structure_detailed.txt',
         'Known Structure'),
        ('synthetic_graphs/verify_complete_7.txt',
         'results/synthetic/verify_complete_7_detailed.txt',
         'results/betweenness/exact/verify_complete_7_detailed.txt',
         'Complete Graph K7'),
        ('synthetic_graphs/verify_cycle_6.txt',
         'results/synthetic/verify_cycle_6_detailed.txt',
         'results/betweenness/exact/verify_cycle_6_detailed.txt',
         'Cycle Graph'),
        ('synthetic_graphs/verify_star_9.txt',
         'results/synthetic/verify_star_9_detailed.txt',
         'results/betweenness/exact/verify_star_9_detailed.txt',
         'Star Graph'),
    ]
    
    for graph_file, kcore_file, bc_file, title in animations:
        if Path(graph_file).exists():
            # K-Core animation
            anim_file = viz_dir / f"kcore_{Path(graph_file).stem}.gif"
            if create_animation_kcore(graph_file, kcore_file, str(anim_file), f"{title} - K-Core"):
                print(f"  ✓ Created: {anim_file.name}")
            
            # Betweenness animation
            anim_file = viz_dir / f"betweenness_{Path(graph_file).stem}.gif"
            if create_animation_betweenness(graph_file, bc_file, str(anim_file), f"{title} - Betweenness"):
                print(f"  ✓ Created: {anim_file.name}")
            
            # Comparison animation
            anim_file = viz_dir / f"comparison_{Path(graph_file).stem}.gif"
            if create_comparison_animation(graph_file, kcore_file, bc_file, str(anim_file), title):
                print(f"  ✓ Created: {anim_file.name}")
    
    print()
    print("=" * 70)
    print("Node visualization complete!")
    print("=" * 70)
    print(f"\nAll outputs saved to: {viz_dir.absolute()}")
    print("\nGenerated files:")
    print("  Static visualizations:")
    print("    - kcore_node_rankings.png")
    print("    - betweenness_node_rankings.png")
    print("  Animated visualizations (GIF):")
    print("    - kcore_*.gif (K-core decomposition process)")
    print("    - betweenness_*.gif (Betweenness ranking process)")
    print("    - comparison_*.gif (Side-by-side comparison)")
    print()

if __name__ == "__main__":
    main()
