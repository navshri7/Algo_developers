#!/bin/bash

# Centrality Measures Experiment Runner
# Runs Katz and Eigenvector centrality on synthetic and real datasets

set -e

echo "======================================================================"
echo "Centrality Measures: Comprehensive Experiment Suite"
echo "======================================================================"
echo ""

# Create directory structure
mkdir -p results/centrality/katz
mkdir -p results/centrality/eigenvector
mkdir -p results/centrality/comparison

# Compile the C++ programs
echo "Step 1: Compiling Centrality implementations..."
g++ -std=c++17 -O3 -o katz_centrality katz_centrality.cpp
if [ $? -eq 0 ]; then
    echo "  ✓ Katz centrality compilation successful"
else
    echo "  ✗ Katz centrality compilation failed"
    exit 1
fi

g++ -std=c++17 -O3 -o eigenvector_centrality eigenvector_centrality.cpp
if [ $? -eq 0 ]; then
    echo "  ✓ Eigenvector centrality compilation successful"
else
    echo "  ✗ Eigenvector centrality compilation failed"
    exit 1
fi
echo ""

# Run experiments on synthetic graphs
echo "Step 2: Running experiments on synthetic graphs..."
echo "----------------------------------------------------------------------"

# Verification graphs
echo "2.1 Verification Graphs:"
for graph in synthetic_graphs/verify_*.txt; do
    if [ -f "$graph" ]; then
        basename=$(basename "$graph" .txt)
        echo "  Running: $basename"
        ./katz_centrality "$graph" "results/centrality/katz" "$basename"
        ./eigenvector_centrality "$graph" "results/centrality/eigenvector" "$basename"
    fi
done
echo ""

# Small graphs
echo "2.2 Small Test Graphs (100-1000 nodes):"
for graph in synthetic_graphs/er_*_*.txt synthetic_graphs/ba_1k_*.txt synthetic_graphs/ws_1k_*.txt; do
    if [ -f "$graph" ]; then
        basename=$(basename "$graph" .txt)
        echo "  Running: $basename"
        ./katz_centrality "$graph" "results/centrality/katz" "$basename"
        ./eigenvector_centrality "$graph" "results/centrality/eigenvector" "$basename"
    fi
done
echo ""

# Medium graphs
echo "2.3 Medium Test Graphs (5000-10000 nodes):"
for graph in synthetic_graphs/er_5k_*.txt synthetic_graphs/er_10k_*.txt synthetic_graphs/ba_5k_*.txt synthetic_graphs/ba_10k_*.txt synthetic_graphs/ws_5k_*.txt; do
    if [ -f "$graph" ]; then
        basename=$(basename "$graph" .txt)
        echo "  Running: $basename"
        ./katz_centrality "$graph" "results/centrality/katz" "$basename"
        ./eigenvector_centrality "$graph" "results/centrality/eigenvector" "$basename"
    fi
done
echo ""

# Run experiments on real datasets
echo "Step 3: Running experiments on real datasets..."
echo "----------------------------------------------------------------------"

# cit-DBLP
if [ -f "converted_datasets/cit-DBLP.txt" ]; then
    echo "3.1 Running on cit-DBLP..."
    ./katz_centrality "converted_datasets/cit-DBLP.txt" "results/centrality/katz" "cit-DBLP"
    ./eigenvector_centrality "converted_datasets/cit-DBLP.txt" "results/centrality/eigenvector" "cit-DBLP"
    echo ""
else
    echo "3.1 Skipping cit-DBLP (not found)"
    echo ""
fi

# cit-HepTh
if [ -f "converted_datasets/cit-HepTh.txt" ]; then
    echo "3.2 Running on cit-HepTh..."
    ./katz_centrality "converted_datasets/cit-HepTh.txt" "results/centrality/katz" "cit-HepTh"
    ./eigenvector_centrality "converted_datasets/cit-HepTh.txt" "results/centrality/eigenvector" "cit-HepTh"
    echo ""
else
    echo "3.2 Skipping cit-HepTh (not found)"
    echo ""
fi

# CiteSeer
if [ -f "converted_datasets/citeseer.txt" ]; then
    echo "3.3 Running on CiteSeer..."
    ./katz_centrality "converted_datasets/citeseer.txt" "results/centrality/katz" "citeseer"
    ./eigenvector_centrality "converted_datasets/citeseer.txt" "results/centrality/eigenvector" "citeseer"
    echo ""
else
    echo "3.3 Skipping CiteSeer (not found)"
    echo ""
fi

# Cora
if [ -f "converted_datasets/cora.txt" ]; then
    echo "3.4 Running on Cora..."
    ./katz_centrality "converted_datasets/cora.txt" "results/centrality/katz" "cora"
    ./eigenvector_centrality "converted_datasets/cora.txt" "results/centrality/eigenvector" "cora"
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
echo "  - results/centrality/katz/        (Katz centrality results)"
echo "  - results/centrality/eigenvector/ (Eigenvector centrality results)"
echo ""
echo "Next step: Run comparison script to analyze results"
echo "  python3 compare_all_algorithms.py"
echo ""
