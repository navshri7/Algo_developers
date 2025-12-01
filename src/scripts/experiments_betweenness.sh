#!/bin/bash

# Betweenness Centrality Experiment Runner
# Runs both exact and approximate betweenness on synthetic and real datasets

set -e

# Get project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$PROJECT_ROOT"

echo "======================================================================"
echo "Betweenness Centrality: Comprehensive Experiment Suite"
echo "======================================================================"
echo ""

# Create directory structure
mkdir -p results/betweenness/exact
mkdir -p results/betweenness/approximate
mkdir -p results/betweenness/comparison
mkdir -p bin

# Compile the C++ programs
echo "Step 1: Compiling Betweenness implementations..."
g++ -std=c++17 -O3 -o bin/betweenness_exact src/algorithms/betweenness_exact.cpp
if [ $? -eq 0 ]; then
    echo "  ✓ Exact betweenness compilation successful"
else
    echo "  ✗ Exact betweenness compilation failed"
    exit 1
fi

g++ -std=c++17 -O3 -o bin/betweenness_approx src/algorithms/betweenness_approx.cpp
if [ $? -eq 0 ]; then
    echo "  ✓ Approximate betweenness compilation successful"
else
    echo "  ✗ Approximate betweenness compilation failed"
    exit 1
fi
echo ""

# Run experiments on synthetic graphs
echo "Step 2: Running experiments on synthetic graphs..."
echo "----------------------------------------------------------------------"

# Verification graphs
echo "2.1 Verification Graphs:"
for graph in data/synthetic_graphs/verify_*.txt; do
    if [ -f "$graph" ]; then
        basename=$(basename "$graph" .txt)
        echo "  Running: $basename"
        bin/betweenness_exact "$graph" "results/betweenness/exact" "$basename"
        bin/betweenness_approx "$graph" "results/betweenness/approximate" "$basename"
    fi
done
echo ""

# Small graphs
echo "2.2 Small Test Graphs (100-1000 nodes):"
for graph in data/synthetic_graphs/er_*_*.txt data/synthetic_graphs/ba_1k_*.txt data/synthetic_graphs/ws_1k_*.txt; do
    if [ -f "$graph" ]; then
        basename=$(basename "$graph" .txt)
        echo "  Running: $basename"
        bin/betweenness_exact "$graph" "results/betweenness/exact" "$basename"
        bin/betweenness_approx "$graph" "results/betweenness/approximate" "$basename"
    fi
done
echo ""

# Medium graphs
echo "2.3 Medium Test Graphs (5000-10000 nodes):"
for graph in data/synthetic_graphs/er_5k_*.txt data/synthetic_graphs/er_10k_*.txt data/synthetic_graphs/ba_5k_*.txt data/synthetic_graphs/ba_10k_*.txt data/synthetic_graphs/ws_5k_*.txt; do
    if [ -f "$graph" ]; then
        basename=$(basename "$graph" .txt)
        echo "  Running: $basename"
        bin/betweenness_exact "$graph" "results/betweenness/exact" "$basename"
        bin/betweenness_approx "$graph" "results/betweenness/approximate" "$basename"
    fi
done
echo ""

# Run experiments on real datasets
echo "Step 3: Running experiments on real datasets..."
echo "----------------------------------------------------------------------"

# cit-DBLP
if [ -f "data/converted_datasets/cit-DBLP.txt" ]; then
    echo "3.1 Running on cit-DBLP..."
    bin/betweenness_exact "data/converted_datasets/cit-DBLP.txt" "results/betweenness/exact" "cit-DBLP"
    bin/betweenness_approx "data/converted_datasets/cit-DBLP.txt" "results/betweenness/approximate" "cit-DBLP"
    echo ""
else
    echo "3.1 Skipping cit-DBLP (not found)"
    echo ""
fi

# cit-HepTh
if [ -f "data/converted_datasets/cit-HepTh.txt" ]; then
    echo "3.2 Running on cit-HepTh..."
    bin/betweenness_exact "data/converted_datasets/cit-HepTh.txt" "results/betweenness/exact" "cit-HepTh"
    bin/betweenness_approx "data/converted_datasets/cit-HepTh.txt" "results/betweenness/approximate" "cit-HepTh"
    echo ""
else
    echo "3.2 Skipping cit-HepTh (not found)"
    echo ""
fi

# CiteSeer
if [ -f "data/converted_datasets/citeseer.txt" ]; then
    echo "3.3 Running on CiteSeer..."
    bin/betweenness_exact "data/converted_datasets/citeseer.txt" "results/betweenness/exact" "citeseer"
    bin/betweenness_approx "data/converted_datasets/citeseer.txt" "results/betweenness/approximate" "citeseer"
    echo ""
else
    echo "3.3 Skipping CiteSeer (not found)"
    echo ""
fi

# Cora
if [ -f "data/converted_datasets/cora.txt" ]; then
    echo "3.4 Running on Cora..."
    bin/betweenness_exact "data/converted_datasets/cora.txt" "results/betweenness/exact" "cora"
    bin/betweenness_approx "data/converted_datasets/cora.txt" "results/betweenness/approximate" "cora"
    echo ""
else
    echo "3.4 Skipping Cora (not found)"
    echo ""
fi

echo "======================================================================"
echo "All experiments completed!"
echo "======================================================================"
echo ""
echo "Results are available in:"
echo "  - results/betweenness/exact/        (exact betweenness results)"
echo "  - results/betweenness/approximate/  (approximate betweenness results)"
echo ""
echo "Next step: Run visualization script to compare results"
echo "  python3 visualizations_betweenness.py"
echo ""
