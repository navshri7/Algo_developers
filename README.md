# Algorithm Analysis Suite

Comprehensive framework for analyzing and comparing graph algorithms:
- **Foundational**: K-Core Decomposition, Betweenness Centrality
- **Frontier**: Katz Centrality, Eigenvector Centrality

## Quick Start

```bash
make build                    # Compile all algorithms
bash src/scripts/run_all.sh   # Run everything
```

## Key Features

✓ 4 centrality algorithms with full framework integration  
✓ 4 real-world citation networks + 30+ synthetic test graphs  
✓ Comprehensive visualizations with animated GIFs  
✓ Node-level analysis and ranking comparisons  
✓ Performance metrics (runtime, memory, efficiency)  
✓ Foundational vs Frontier algorithm comparison  

## Documentation

**→ [COMPLETE_GUIDE.md](docs/COMPLETE_GUIDE.md)** - Full documentation with everything you need

## Project Structure

```
src/algorithms/          C++ implementations
src/scripts/             Bash experiment runners
src/python/              Python utilities (data, analysis, visualization)
data/                    Datasets (real + synthetic)
results/                 All experiment outputs
bin/                     Compiled binaries
docs/                    Documentation
```

## Algorithms

| Algorithm | Type | Complexity | Detects |
|-----------|------|-----------|---------|
| K-Core | Foundational | O(V+E) | Structural hierarchy |
| Betweenness | Foundational | O(V·E) | Bridge nodes, bottlenecks |
| Katz | Frontier | O(V·E·i) | Influence propagation |
| Eigenvector | Frontier | O(V·E·i) | Hub nodes, prestige |

## Visualizations

- **comparison_*.png** - Side-by-side algorithm comparison
- **ranking_heatmap_*.png** - Node ranking heatmaps
- **top_nodes_*.png** - Top 10 nodes bar charts
- **animation_all_*.gif** - Animated algorithm comparison
- **runtime_characteristics.png** - Performance analysis
- **node_ranking_overlap.png** - Algorithm agreement analysis

## Results

```
results/
├── synthetic/                    K-Core on synthetic graphs
├── real_datasets/                K-Core on real datasets
├── betweenness/                  Betweenness results
├── centrality/                   Katz & Eigenvector results
├── algorithm_comparison/         Cross-algorithm analysis
└── node_visualizations/          Node-level visualizations
```

## Build & Run

```bash
make setup              # Create directories
make build              # Compile algorithms
make clean              # Remove binaries
make distclean          # Clean everything

bash src/scripts/run_all.sh          # Run all experiments
bash src/scripts/experiments_kcore.sh
bash src/scripts/experiments_betweenness.sh
bash src/scripts/experiments_centrality.sh
```

## Dependencies

- **C++**: g++ 5.0+ (C++17)
- **Python**: networkx, matplotlib, pandas, seaborn, Pillow

```bash
pip install -r requirements.txt
```

## For More Information

See [docs/COMPLETE_GUIDE.md](docs/COMPLETE_GUIDE.md) for:
- Detailed algorithm descriptions
- Use case recommendations
- Advanced usage
- Troubleshooting
- Performance tuning

---

Educational and research use.
