#!/bin/bash

# K-Core Decomposition Experiment Runner
# This script runs comprehensive experiments on synthetic and real datasets

set -e  # Exit on error

echo "======================================================================"
echo "K-Core Decomposition: Comprehensive Experiment Suite"
echo "======================================================================"
echo ""

# Create directory structure
mkdir -p results/synthetic
mkdir -p results/real_datasets
mkdir -p synthetic_graphs
mkdir -p converted_datasets

# Compile the C++ program
echo "Step 1: Compiling K-Core implementation..."
g++ -std=c++17 -O3 -o kcore kcore.cpp
if [ $? -eq 0 ]; then
    echo "  ✓ Compilation successful"
else
    echo "  ✗ Compilation failed"
    exit 1
fi
echo ""

# Generate synthetic graphs
echo "Step 2: Generating synthetic test graphs..."
python3 generate_synthetic_graphs.py
echo ""

# Convert real datasets
echo "Step 3: Converting real datasets to standard format..."
python3 convert_datasets.py
echo ""

# Run experiments on synthetic graphs
echo "Step 4: Running experiments on synthetic graphs..."
echo "----------------------------------------------------------------------"

# Verification graphs (small, known structure)
echo "4.1 Verification Graphs:"
for graph in synthetic_graphs/verify_*.txt; do
    if [ -f "$graph" ]; then
        basename=$(basename "$graph" .txt)
        echo "  Running: $basename"
        ./kcore "$graph" "results/synthetic" "$basename"
    fi
done
echo ""

# Small graphs
echo "4.2 Small Test Graphs (100-1000 nodes):"
for graph in synthetic_graphs/er_*_*.txt synthetic_graphs/ba_1k_*.txt synthetic_graphs/ws_1k_*.txt; do
    if [ -f "$graph" ]; then
        basename=$(basename "$graph" .txt)
        echo "  Running: $basename"
        ./kcore "$graph" "results/synthetic" "$basename"
    fi
done
echo ""

# Medium graphs
echo "4.3 Medium Test Graphs (5000-10000 nodes):"
for graph in synthetic_graphs/er_5k_*.txt synthetic_graphs/er_10k_*.txt synthetic_graphs/ba_5k_*.txt synthetic_graphs/ba_10k_*.txt synthetic_graphs/ws_5k_*.txt; do
    if [ -f "$graph" ]; then
        basename=$(basename "$graph" .txt)
        echo "  Running: $basename"
        ./kcore "$graph" "results/synthetic" "$basename"
    fi
done
echo ""

# Clique-based graphs
echo "4.4 Clique-Based Graphs:"
for graph in synthetic_graphs/cliques_*.txt; do
    if [ -f "$graph" ]; then
        basename=$(basename "$graph" .txt)
        echo "  Running: $basename"
        ./kcore "$graph" "results/synthetic" "$basename"
    fi
done
echo ""

# Power-law cluster graphs
echo "4.5 Power-Law Cluster Graphs:"
for graph in synthetic_graphs/plc_*.txt; do
    if [ -f "$graph" ]; then
        basename=$(basename "$graph" .txt)
        echo "  Running: $basename"
        ./kcore "$graph" "results/synthetic" "$basename"
    fi
done
echo ""

# Run experiments on real datasets
echo "Step 5: Running experiments on real datasets..."
echo "----------------------------------------------------------------------"

# cit-DBLP (converted)
if [ -f "converted_datasets/cit-DBLP.txt" ]; then
    echo "5.1 Running on cit-DBLP..."
    ./kcore "converted_datasets/cit-DBLP.txt" "results/real_datasets" "cit-DBLP"
    echo ""
else
    echo "5.1 Skipping cit-DBLP (not found)"
    echo ""
fi

# cit-HepTh (converted)
if [ -f "converted_datasets/cit-HepTh.txt" ]; then
    echo "5.2 Running on cit-HepTh..."
    ./kcore "converted_datasets/cit-HepTh.txt" "results/real_datasets" "cit-HepTh"
    echo ""
else
    echo "5.2 Skipping cit-HepTh (not found)"
    echo ""
fi

# CiteSeer (converted)
if [ -f "converted_datasets/citeseer.txt" ]; then
    echo "5.3 Running on CiteSeer..."
    ./kcore "converted_datasets/citeseer.txt" "results/real_datasets" "citeseer"
    echo ""
else
    echo "5.3 Skipping CiteSeer (not found)"
    echo ""
fi

# Cora (converted)
if [ -f "converted_datasets/cora.txt" ]; then
    echo "5.4 Running on Cora..."
    ./kcore "converted_datasets/cora.txt" "results/real_datasets" "cora"
    echo ""
else
    echo "5.4 Skipping Cora (not found)"
    echo ""
fi

echo "======================================================================"
echo "All experiments completed!"
echo "======================================================================"
echo ""
echo "Results are available in:"
echo "  - results/synthetic/        (synthetic graph results)"
echo "  - results/real_datasets/    (real dataset results)"
echo ""
echo "Summary files:"
echo "  - results/synthetic/summary.csv"
echo "  - results/real_datasets/summary.csv"
echo ""
echo "Next step: Run visualization script to analyze results"
echo "  python3 visualize_results.py"
echo ""
