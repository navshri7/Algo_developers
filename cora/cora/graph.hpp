// graph.hpp
// Small, self-contained graph loader and helpers for the Cora citation dataset.
// Provides functions to load `cora.cites` into an adjacency list and basic
// linear-algebra helpers (matrix-vector multiply for A and A^T and power
// iteration). Implemented using only the C++ standard library.

#ifndef GRAPH_HPP
#define GRAPH_HPP

#include <string>
#include <vector>
#include <unordered_map>
#include <fstream>
#include <sstream>
#include <iostream>
#include <cmath>

// Load a directed graph from an edge list file where each line contains
// two integer ids: `source\t target`. Node ids in the dataset are arbitrary
// integers; this function remaps them to contiguous indices [0..n-1].
// Parameters:
// - path: path to the `cora.cites` file
// - adj: output adjacency list (adj[u] contains v for an edge u->v)
// - idx2id: output mapping from internal index -> original node id
// Returns true on success.
inline bool load_cora_cites(const std::string &path,
                            std::vector<std::vector<int>> &adj,
                            std::vector<int> &idx2id) {
    std::ifstream in(path);
    if (!in) return false;

    std::unordered_map<int,int> id2idx;
    std::vector<std::pair<int,int>> edges;
    edges.reserve(6000);

    std::string line;
    while (std::getline(in, line)) {
        if (line.empty()) continue;
        std::istringstream iss(line);
        int u, v;
        if (!(iss >> u >> v)) continue;
        auto it = id2idx.find(u);
        if (it == id2idx.end()) {
            int idx = (int)id2idx.size();
            id2idx[u] = idx;
            idx2id.push_back(u);
        }
        it = id2idx.find(v);
        if (it == id2idx.end()) {
            int idx = (int)id2idx.size();
            id2idx[v] = idx;
            idx2id.push_back(v);
        }
        // In the Cora `cora.cites` format the first id is the cited paper and
        // the second id is the citing paper. The directed link is from the
        // citing paper -> cited paper (right-to-left in the file). We store
        // adjacency as outgoing edges, so push (citing -> cited).
        edges.emplace_back(id2idx[v], id2idx[u]);
    }

    adj.assign(id2idx.size(), std::vector<int>());
    for (auto &e : edges) adj[e.first].push_back(e.second);
    return true;
}

// Multiply y = A * x where A is the adjacency matrix represented by
// `adj` (rows are outgoing edges): (A*x)_u = sum_{v in adj[u]} x[v]
inline void multiply_A_vec(const std::vector<std::vector<int>> &adj,
                           const std::vector<double> &x,
                           std::vector<double> &y) {
    int n = (int)adj.size();
    y.assign(n, 0.0);
    for (int u = 0; u < n; ++u) {
        double sum = 0.0;
        for (int v : adj[u]) sum += x[v];
        y[u] = sum;
    }
}

// Multiply y = A^T * x (accumulate contributions from incoming edges)
// A^T multiplication can be implemented by iterating each edge u->v and
// adding x[u] to y[v]: (A^T*x)_v = sum_{u: u->v} x[u]
inline void multiply_AT_vec(const std::vector<std::vector<int>> &adj,
                            const std::vector<double> &x,
                            std::vector<double> &y) {
    int n = (int)adj.size();
    y.assign(n, 0.0);
    for (int u = 0; u < n; ++u) {
        double xu = x[u];
        if (xu == 0.0) continue;
        for (int v : adj[u]) y[v] += xu;
    }
}

// Power iteration to estimate the largest eigenvalue of A and optionally
// return the principal eigenvector for A or A^T.
// - if use_transpose==true uses A^T multiplies (useful for citation incoming centrality)
// Returns pair(eigenvalue, eigenvector)
inline std::pair<double, std::vector<double>> power_iteration(
    const std::vector<std::vector<int>> &adj,
    bool use_transpose = false,
    int max_iter = 1000,
    double tol = 1e-6) {
    int n = (int)adj.size();
    std::vector<double> x(n, 1.0 / std::sqrt((double)std::max(1, n))); // init normalized
    std::vector<double> y(n);
    double lambda = 0.0;
    for (int it = 0; it < max_iter; ++it) {
        if (use_transpose) multiply_AT_vec(adj, x, y);
        else multiply_A_vec(adj, x, y);
        // norm
        double norm = 0.0;
        for (double v : y) norm += v*v;
        norm = std::sqrt(norm);
        if (norm == 0.0) break;
        for (int i = 0; i < n; ++i) x[i] = y[i] / norm;
        // Rayleigh quotient for eigenvalue estimate: lambda = x^T (A x)
        if (use_transpose) multiply_AT_vec(adj, x, y);
        else multiply_A_vec(adj, x, y);
        double rq = 0.0;
        for (int i = 0; i < n; ++i) rq += x[i] * y[i];
        if (it > 0 && std::abs(rq - lambda) < tol) { lambda = rq; break; }
        lambda = rq;
    }
    return {lambda, x};
}

// Compute in-degree and out-degree vectors
inline void compute_degrees(const std::vector<std::vector<int>> &adj,
                            std::vector<int> &indeg,
                            std::vector<int> &outdeg) {
    int n = (int)adj.size();
    indeg.assign(n, 0);
    outdeg.assign(n, 0);
    for (int u = 0; u < n; ++u) {
        outdeg[u] = (int)adj[u].size();
        for (int v : adj[u]) indeg[v]++;
    }
}

#endif // GRAPH_HPP
