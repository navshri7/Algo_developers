#!/bin/bash

# Master Experiment Runner
# Runs all algorithms on all datasets with proper organization

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$PROJECT_ROOT"

echo "======================================================================"
echo "Algorithm Analysis Suite - Master Runner"
echo "======================================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if binaries exist
if [ ! -d "bin" ] || [ -z "$(ls -A bin)" ]; then
    echo "Building algorithms..."
    make build
    echo ""
fi

# Step 1: Data Preparation
echo -e "${BLUE}Step 1: Preparing Data${NC}"
echo "----------------------------------------------------------------------"

if [ ! -d "data/converted_datasets" ] || [ -z "$(ls -A data/converted_datasets)" ]; then
    echo "Converting datasets..."
    python3 src/python/data/convert_datasets.py
    echo ""
fi

if [ ! -d "data/synthetic_graphs" ] || [ -z "$(ls -A data/synthetic_graphs)" ]; then
    echo "Generating synthetic graphs..."
    python3 src/python/data/generate_synthetic_graphs.py
    echo ""
fi

# Step 2: Run K-Core Experiments
echo -e "${BLUE}Step 2: K-Core Decomposition${NC}"
echo "----------------------------------------------------------------------"
bash src/scripts/experiments_kcore.sh
echo ""

# Step 3: Run Betweenness Experiments
echo -e "${BLUE}Step 3: Betweenness Centrality${NC}"
echo "----------------------------------------------------------------------"
bash src/scripts/experiments_betweenness.sh
echo ""

# Step 4: Run Centrality Experiments
echo -e "${BLUE}Step 4: Katz & Eigenvector Centrality${NC}"
echo "----------------------------------------------------------------------"
bash src/scripts/experiments_centrality.sh
echo ""

# Step 5: Generate Visualizations
echo -e "${BLUE}Step 5: Generating Visualizations${NC}"
echo "----------------------------------------------------------------------"

echo "K-Core analysis..."
python3 src/python/analysis/visualizations_kcore.py

echo "Betweenness comparison..."
python3 src/python/analysis/visualizations_betweenness.py

echo "Node visualizations..."
python3 src/python/visualization/visualize_nodes.py

echo "Comprehensive algorithm comparison..."
python3 src/python/analysis/compare_all_algorithms.py

echo ""
echo "======================================================================"
echo -e "${GREEN}All experiments completed successfully!${NC}"
echo "======================================================================"
echo ""
echo "Results available in:"
echo "  - results/synthetic/              (K-Core synthetic results)"
echo "  - results/real_datasets/          (K-Core real dataset results)"
echo "  - results/betweenness/            (Betweenness results)"
echo "  - results/centrality/             (Katz & Eigenvector results)"
echo "  - results/algorithm_comparison/   (Comprehensive comparison)"
echo "  - results/node_visualizations/    (Node rankings & animations)"
echo ""
echo "Documentation:"
echo "  - docs/QUICKSTART.md              (Quick start guide)"
echo "  - docs/ALGORITHM_COMPARISON.md    (Algorithm analysis)"
echo ""
