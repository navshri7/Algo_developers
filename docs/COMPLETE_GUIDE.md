# Algorithm Analysis Suite - Complete Guide

## Overview

A comprehensive framework for analyzing and comparing graph algorithms across foundational (classical) and frontier (modern) approaches:

- **Foundational**: K-Core Decomposition, Betweenness Centrality
- **Frontier**: Katz Centrality, Eigenvector Centrality, PageRank Centrality

## Quick Start

```bash
# 1. Build
make build

# 2. Run everything
bash src/scripts/run_all.sh

# 3. View results
ls results/
```

## Project Structure

```
src/
├── algorithms/          # C++ implementations
│   ├── kcore.cpp
│   ├── betweenness_exact.cpp
│   ├── betweenness_approx.cpp
│   ├── katz_centrality.cpp
│   └── eigenvector_centrality.cpp
├── scripts/             # Bash runners
│   ├── run_all.sh       # Master script
│   ├── experiments_kcore.sh
│   ├── experiments_betweenness.sh
│   └── experiments_centrality.sh
└── python/              # Python utilities
    ├── data/            # Data preparation
    ├── analysis/        # Analysis & comparison
    └── visualization/   # Node visualizations

data/
├── cit-DBLP.edges
├── cit-HepTh.txt/
├── citeseer/
├── cora-dataset/
├── converted_datasets/  (generated)
└── synthetic_graphs/    (generated)

results/                 # All outputs
docs/                    # Documentation
bin/                     # Compiled binaries
```

## Algorithms

### K-Core Decomposition
- **Complexity**: O(V+E)
- **Type**: Foundational
- **Detects**: Structural hierarchy, core-periphery structure
- **Best for**: Community detection, network layers
- **Output**: K-core value per node (higher = more central)

### Betweenness Centrality (Exact)
- **Complexity**: O(V·E)
- **Type**: Foundational
- **Detects**: Bridge nodes, bottlenecks, critical infrastructure
- **Best for**: Communication networks, transportation
- **Output**: Betweenness value (0-1, normalized)

### Katz Centrality
- **Complexity**: O(V·E·iterations)
- **Type**: Frontier
- **Detects**: Influence propagation, weighted connections
- **Best for**: Citation networks, recommendation systems
- **Output**: Katz value (0-1, normalized)
- **Parameter**: Alpha (attenuation factor)

### Eigenvector Centrality
- **Complexity**: O(V·E·iterations)
- **Type**: Frontier
- **Detects**: Hub nodes, prestige, recursive importance
- **Best for**: Web ranking, collaboration networks
- **Output**: Eigenvector value (0-1, normalized)
- **Parameter**: Eigenvalue (network connectivity)

### PageRank Centrality
- **Complexity**: O(V·E·iterations)
- **Type**: Frontier
- **Detects**: Global importance via random walk probabilities
- **Best for**: Directed graphs, citation networks, web ranking
- **Output**: PageRank score (0–1, normalized)
- **Parameter**: Damping factor α = 0.85
- **Notes**: Implemented in `src/algorithms/pagerank_centrality.cpp` and integrated into experiments + analysis.

## Running Experiments

### All Experiments
```bash
bash src/scripts/run_all.sh
```

### Individual Algorithms
```bash
# K-Core
bash src/scripts/experiments_kcore.sh

# Betweenness
bash src/scripts/experiments_betweenness.sh

# Katz, Eigenvector & PageRank
bash src/scripts/experiments_centrality.sh
```

### Data Preparation Only
```bash
# Convert datasets
python3 src/python/data/convert_datasets.py

# Generate synthetic graphs
python3 src/python/data/generate_synthetic_graphs.py
```

## Visualizations

### Node Visualizations
```bash
python3 src/python/visualization/visualize_all_algorithms.py
```

Generates:
- **comparison_*.png** - Side-by-side algorithm comparison on verification graphs
- **ranking_heatmap_*.png** - Node ranking heatmaps showing algorithm agreement
- **top_nodes_*.png** - Bar charts of top 10 nodes per algorithm
- **animation_all_*.gif** - Animated comparison showing top N nodes

### Analysis Visualizations
```bash
# K-Core analysis
python3 src/python/analysis/visualizations_kcore.py

# Betweenness comparison
python3 src/python/analysis/visualizations_betweenness.py

# Comprehensive comparison
python3 src/python/analysis/compare_all_algorithms.py
```

## Datasets

### Real-World Citation Networks
- **cit-DBLP**: 12,592 nodes, 49,621 edges
- **cit-HepTh**: 27,769 nodes, 352,285 edges
- **CiteSeer**: 3,264 nodes, 4,536 edges
- **Cora**: 2,708 nodes, 5,278 edges

### Synthetic Test Graphs
- Verification graphs (5-20 nodes with known structure)
- Small graphs (100-1000 nodes)
- Medium graphs (5000-10000 nodes)
- Types: Erdős-Rényi, Barabási-Albert, Watts-Strogatz, cliques, power-law

## Results Structure

```
results/
├── synthetic/                    # K-Core on synthetic graphs
│   ├── summary.csv
│   └── *_detailed.txt
├── real_datasets/                # K-Core on real datasets
│   ├── summary.csv
│   └── *_detailed.txt
├── betweenness/
│   ├── exact/                    # Exact betweenness
│   │   ├── summary.csv
│   │   └── *_detailed.txt
│   ├── approximate/              # Approximate betweenness
│   │   ├── summary_approx.csv
│   │   └── *_approx_detailed.txt
│   └── comparison/               # Comparison visualizations
├── centrality/
│   ├── katz/                     # Katz centrality
│   │   ├── summary.csv
│   │   └── *_detailed.txt
│   └── eigenvector/              # Eigenvector centrality
│       ├── summary.csv
│       └── *_detailed.txt
│   └── pagerank/                 # PageRank centrality
│       ├── summary_pagerank.csv
│       └── *_pagerank_detailed.txt
├── algorithm_comparison/         # Cross-algorithm analysis
│   ├── node_ranking_overlap.png
│   ├── runtime_characteristics.png
│   └── comprehensive_analysis.txt
└── node_visualizations/          # Node-level visualizations
    ├── comparison_*.png
    ├── ranking_heatmap_*.png
    ├── top_nodes_*.png
    └── animation_all_*.gif
```

## Build System

### Makefile Targets
```bash
make setup              # Create directories
make build              # Compile all algorithms
make clean              # Remove binaries
make distclean          # Remove all generated files
make help               # Show help
```

### Manual Compilation
```bash
# Individual algorithms
g++ -std=c++17 -O3 -o bin/kcore src/algorithms/kcore.cpp
g++ -std=c++17 -O3 -o bin/betweenness_exact src/algorithms/betweenness_exact.cpp
g++ -std=c++17 -O3 -o bin/betweenness_approx src/algorithms/betweenness_approx.cpp
g++ -std=c++17 -O3 -o bin/katz_centrality src/algorithms/katz_centrality.cpp
g++ -std=c++17 -O3 -o bin/eigenvector_centrality src/algorithms/eigenvector_centrality.cpp
g++ -std=c++17 -O3 -o bin/pagerank_centrality src/algorithms/pagerank_centrality.cpp
```

## Output Files

### Summary CSV Format
```
Dataset,Vertices,Edges,Density,AvgDegree,Runtime_sec,Memory_MB,MaxValue,Algorithm
verify_known_structure,20,40,0.211,4.0,0.001234,2.5,5,K-Core
```

### Detailed Results Format
```
===== Top 100 Nodes =====
Rank    Node    Value
1       5       5.0
2       3       4.0
3       7       4.0
...
```

## Performance Characteristics

| Algorithm | Time | Space | Scalability | Deterministic |
|-----------|------|-------|-------------|---------------|
| K-Core | O(V+E) | O(V+E) | Excellent | Yes |
| Betweenness | O(V·E) | O(V+E) | Poor | Yes |
| Katz | O(V·E·i) | O(V+E) | Good | Yes |
| Eigenvector | O(V·E·i) | O(V+E) | Good | Yes |
| PageRank | O(V·E·i) | O(V+E) | Good | Yes |

## What Each Algorithm Detects

### K-Core
- **Structural hierarchy**: Identifies nested core-periphery layers
- **Community structure**: Nodes in same k-core are tightly connected
- **Network robustness**: K-core value indicates resilience
- **Example**: Social networks - core members vs peripheral members

### Betweenness
- **Bridge nodes**: Critical connection points between communities
- **Bottlenecks**: Information flow control points
- **Network vulnerability**: Removing high-betweenness nodes disrupts network
- **Example**: Transportation networks - critical junctions

### Katz
- **Influence propagation**: Importance based on reachability
- **Weighted connections**: Nearby connections more important
- **Attenuation-based**: Importance decays with distance
- **Example**: Citation networks - influential papers

### Eigenvector
- **Hub nodes**: Connected to other important nodes
- **Prestige**: Recursive importance measure
- **Network influence**: Spectral properties
- **Example**: Collaboration networks - prestigious researchers

### PageRank
- **Global influence**: Probability of landing at a node via random walk
- **Stability**: Dampens dominance of high-degree nodes
- **Directed importance**: Works especially well for citation/web graphs
- **Example**: Ranking academic papers, web pages (Google PageRank)

## Comparison: Foundational vs Frontier

### Foundational Algorithms
✓ Established mathematical foundations  
✓ Well-understood properties  
✓ Deterministic results  
✓ Limited parameters  
✗ Slower for large graphs  

### Frontier Algorithms
✓ Modern network science approach  
✓ Better scalability  
✓ More flexible modeling  
✓ Parameter-tunable  
✗ Iterative computation overhead  
**Includes**: Katz Centrality, Eigenvector Centrality, PageRank Centrality

## Recommendations by Use Case

### Small Networks (< 1000 nodes)
**Use**: Betweenness Centrality (exact)
- Accurate, deterministic, manageable computation

### Medium Networks (1000-100k nodes)
**Use**: Katz or Eigenvector Centrality
- Good balance of accuracy and speed

### Large Networks (> 100k nodes)
**Use**: K-Core Decomposition
- Linear time complexity

### Citation Networks
1. Eigenvector, PageRank or Katz Centrality (primary)
2. Betweenness for bottlenecks (secondary)
3. K-Core for communities (tertiary)

### Social Networks
1. K-Core for communities (primary)
2. Eigenvector for influencers (secondary)
3. Betweenness for bridges (tertiary)

### Infrastructure Networks
1. Betweenness for critical nodes (primary)
2. K-Core for robustness (secondary)
3. Katz for redundancy (tertiary)

## Dependencies

### C++
- g++ 5.0+ (C++17 support)

### Python
```bash
pip install -r requirements.txt
```

Includes:
- networkx (graph operations)
- matplotlib (visualization)
- pandas (data handling)
- seaborn (statistical visualization)
- Pillow (GIF creation)

## Troubleshooting

### Compilation Errors
```bash
# Ensure C++17 support
g++ --version

# Rebuild
make clean
make build
```

### Missing Datasets
```bash
# Verify dataset locations
ls data/

# Convert datasets
python3 src/python/data/convert_datasets.py
```

### Python Module Errors
```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Path Issues
```bash
# Ensure running from project root
cd /path/to/Algo_developers

# Use wrapper script
bash run.sh
```

## Advanced Usage

### Custom Graph Analysis
```bash
# Run single algorithm on custom graph
bin/kcore your_graph.txt results/custom kcore_test

# Convert custom dataset
python3 src/python/data/convert_datasets.py
```

### Batch Processing
```bash
# Run specific experiments
bash src/scripts/experiments_kcore.sh
bash src/scripts/experiments_betweenness.sh
bash src/scripts/experiments_centrality.sh
```

### Visualization Only
```bash
# Generate visualizations without re-running experiments
python3 src/python/visualization/visualize_all_algorithms.py
python3 src/python/analysis/compare_all_algorithms.py
```

## Performance Tuning

### Memory Usage
- Algorithms use O(V+E) space
- For very large graphs, consider approximate algorithms
- Use K-Core for linear memory usage

### Runtime Optimization
- Betweenness: Use approximate version for large graphs
- Katz/Eigenvector: Adjust iteration tolerance for faster convergence
- K-Core: Already optimal at O(V+E)

## Citation

If using this framework in research, please cite:

```bibtex
@software{algo_analysis_2024,
  title={Algorithm Analysis Suite},
  author={Your Name},
  year={2024},
  url={https://github.com/your-repo}
}
```

## License

Educational and research use.

## Support

For issues or questions:
1. Check TROUBLESHOOTING section above
2. Review output logs in results/
3. Verify dataset paths
4. Ensure dependencies are installed

## Next Steps

1. Run `make build` to compile
2. Run `bash src/scripts/run_all.sh` to execute all experiments
3. Check `results/` for outputs
4. View visualizations in `results/node_visualizations/`
5. Read comprehensive analysis in `results/algorithm_comparison/`
