.PHONY: all clean build algorithms help setup

# Compiler settings
CXX = g++
CXXFLAGS = -std=c++17 -O3 -Wall
SRC_DIR = src/algorithms
BIN_DIR = bin

# Algorithms to build
ALGORITHMS = kcore betweenness_exact betweenness_approx katz_centrality eigenvector_centrality

# Default target
all: setup build

# Setup directories
setup:
	@echo "Setting up directories..."
	@mkdir -p $(BIN_DIR)
	@mkdir -p data/converted_datasets
	@mkdir -p data/synthetic_graphs
	@mkdir -p results
	@echo "✓ Directories created"

# Build all algorithms
build: $(addprefix $(BIN_DIR)/, $(ALGORITHMS))
	@echo "✓ All algorithms compiled successfully"

# Individual algorithm builds
$(BIN_DIR)/kcore: $(SRC_DIR)/kcore.cpp
	@echo "Compiling k-core..."
	@$(CXX) $(CXXFLAGS) -o $@ $<
	@echo "✓ k-core compiled"

$(BIN_DIR)/betweenness_exact: $(SRC_DIR)/betweenness_exact.cpp
	@echo "Compiling betweenness (exact)..."
	@$(CXX) $(CXXFLAGS) -o $@ $<
	@echo "✓ Betweenness (exact) compiled"

$(BIN_DIR)/betweenness_approx: $(SRC_DIR)/betweenness_approx.cpp
	@echo "Compiling betweenness (approximate)..."
	@$(CXX) $(CXXFLAGS) -o $@ $<
	@echo "✓ Betweenness (approximate) compiled"

$(BIN_DIR)/katz_centrality: $(SRC_DIR)/katz_centrality.cpp
	@echo "Compiling Katz centrality..."
	@$(CXX) $(CXXFLAGS) -o $@ $<
	@echo "✓ Katz centrality compiled"

$(BIN_DIR)/eigenvector_centrality: $(SRC_DIR)/eigenvector_centrality.cpp
	@echo "Compiling eigenvector centrality..."
	@$(CXX) $(CXXFLAGS) -o $@ $<
	@echo "✓ Eigenvector centrality compiled"

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	@rm -rf $(BIN_DIR)/*
	@echo "✓ Cleaned"

# Full clean (including results)
distclean: clean
	@echo "Cleaning all generated files..."
	@rm -rf results/*
	@rm -rf data/synthetic_graphs/*
	@rm -rf data/converted_datasets/*
	@echo "✓ Full clean complete"

# Help
help:
	@echo "Makefile targets:"
	@echo "  make setup              - Create necessary directories"
	@echo "  make build              - Compile all algorithms"
	@echo "  make all                - Setup and build (default)"
	@echo "  make clean              - Remove compiled binaries"
	@echo "  make distclean          - Remove all generated files"
	@echo "  make help               - Show this help message"
	@echo ""
	@echo "Usage:"
	@echo "  make                    - Build everything"
	@echo "  make clean              - Clean binaries"
	@echo "  make distclean          - Clean everything"
