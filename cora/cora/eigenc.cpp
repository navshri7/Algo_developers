#// NOTE: auto-created by the course project helper.
#include <iostream>
#include <fstream>
#include <chrono>
#include <vector>
#include <string>
#include <iomanip>
#include <algorithm>
#include "graph.hpp"

// Compute eigenvector centrality using power iteration on A^T (incoming links).
// Outputs CSV: `eigenc_output.csv` with columns: node_id,eigen,indeg,outdeg
// Usage: ./eigenc [path_to_cora.cites]

int main(int argc, char** argv) {
	std::string path = "cora.cites";
	if (argc > 1) path = argv[1];

	std::vector<std::vector<int>> adj;
	std::vector<int> idx2id;
	std::cout << "Loading graph from '" << path << "'...\n";
	if (!load_cora_cites(path, adj, idx2id)) {
		std::cerr << "Failed to open " << path << "\n";
		return 1;
	}
	int n = (int)adj.size();
	std::cout << "Nodes: " << n << ", edges (approx): ";
	long long m = 0;
	for (auto &v : adj) m += v.size();
	std::cout << m << "\n";

	std::vector<int> indeg, outdeg;
	compute_degrees(adj, indeg, outdeg);

	std::cout << "Running power iteration on A^T to compute eigenvector centrality...\n";
	auto t0 = std::chrono::steady_clock::now();
	auto res = power_iteration(adj, /*use_transpose*/ true, 10000, 1e-9);
	auto t1 = std::chrono::steady_clock::now();

	double lambda = res.first;
	std::vector<double> eig = res.second;
	// Normalize so max = 1 for easier comparison
	double mx = 0.0;
	for (double v : eig) if (v > mx) mx = v;
	if (mx > 0.0) for (double &v : eig) v /= mx;

	double elapsed = std::chrono::duration<double>(t1 - t0).count();
	std::cout << "Finished. Time: " << elapsed << " sec, lambda_est=" << lambda << "\n";

	std::ofstream out("eigenc_output.csv");
	out << "node_id,eigen_centrality,in_degree,out_degree\n";
	out << std::fixed << std::setprecision(6);
	for (int i = 0; i < n; ++i) {
		out << idx2id[i] << "," << eig[i] << "," << indeg[i] << "," << outdeg[i] << "\n";
	}
	out.close();

	std::cout << "Wrote 'eigenc_output.csv' (" << n << " rows).\n";
	std::cout << "Top 10 nodes by eigenvector centrality:\n";
	std::vector<int> ids(n);
	for (int i = 0; i < n; ++i) ids[i] = i;
	std::sort(ids.begin(), ids.end(), [&](int a, int b){ return eig[a] > eig[b]; });
	for (int k = 0; k < std::min(10, n); ++k) {
		int i = ids[k];
		std::cout << k+1 << ") id=" << idx2id[i] << ", eigen=" << eig[i] << ", indeg=" << indeg[i] << "\n";
	}

	return 0;
}

