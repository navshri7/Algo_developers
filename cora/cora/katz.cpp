#// NOTE: auto-created by the course project helper.
#include <iostream>
#include <fstream>
#include <chrono>
#include <vector>
#include <string>
#include <iomanip>
#include <algorithm>
#include <numeric>
#include "graph.hpp"

// Katz centrality implementation (iterative):
// x_{t+1} = alpha * A^T * x_t + beta
// We use A^T to treat incoming citations as contributing centrality.
// Outputs: `katz_output.csv` with columns node_id,katz_centrality,in_degree,out_degree
// Usage: ./katz [path_to_cora.cites] [alpha (optional, default auto)]

int main(int argc, char** argv) {
	std::string path = "cora.cites";
	double alpha_in = -1.0;
	if (argc > 1) path = argv[1];
	if (argc > 2) alpha_in = std::stod(argv[2]);

	std::vector<std::vector<int>> adj;
	std::vector<int> idx2id;
	std::cout << "Loading graph from '" << path << "'...\n";
	if (!load_cora_cites(path, adj, idx2id)) {
		std::cerr << "Failed to open " << path << "\n";
		return 1;
	}
	int n = (int)adj.size();
	long long m = 0; for (auto &v: adj) m += v.size();
	std::cout << "Nodes: " << n << ", edges (approx): " << m << "\n";

	std::vector<int> indeg, outdeg;
	compute_degrees(adj, indeg, outdeg);

	std::cout << "Estimating spectral radius (largest eigenvalue)...\n";
	auto sp0 = std::chrono::steady_clock::now();
	auto pr = power_iteration(adj, /*use_transpose*/ false, 10000, 1e-9);
	double lambda_max = pr.first;
	auto sp1 = std::chrono::steady_clock::now();
	double sp_time = std::chrono::duration<double>(sp1 - sp0).count();
	std::cout << "Estimated spectral radius: " << lambda_max << " (took " << sp_time << "s)\n";

	double alpha = alpha_in;
	if (alpha <= 0.0) {
		if (lambda_max > 0.0) alpha = 0.85 / lambda_max;
		else alpha = 0.01;
	}
	std::cout << "Using alpha=" << alpha << "\n";

	// Katz iteration
	std::vector<double> x(n, 0.0), xnext(n, 0.0);
	const double beta = 1.0;
	const int max_iter = 10000;
	const double tol = 1e-9;

	std::cout << "Running Katz iterations (A^T) ...\n";
	auto t0 = std::chrono::steady_clock::now();
	for (int it = 0; it < max_iter; ++it) {
		// xnext = alpha * A^T * x + beta
		multiply_AT_vec(adj, x, xnext); // xnext = A^T * x
		for (int i = 0; i < n; ++i) xnext[i] = alpha * xnext[i] + beta;
		// check convergence
		double diff = 0.0;
		for (int i = 0; i < n; ++i) {
			double d = xnext[i] - x[i]; diff += d*d;
		}
		diff = std::sqrt(diff);
		x.swap(xnext);
		if (diff < tol) { std::cout << "Converged in " << it+1 << " iterations.\n"; break; }
		if (it == max_iter-1) std::cout << "Reached max iterations (" << max_iter << ").\n";
	}
	auto t1 = std::chrono::steady_clock::now();
	double elapsed = std::chrono::duration<double>(t1 - t0).count();
	std::cout << "Katz runtime: " << elapsed << " sec\n";

	// Normalize Katz centrality by max for easier comparison
	double kmax = 0.0; for (double v : x) if (v > kmax) kmax = v;
	if (kmax > 0.0) for (double &v : x) v /= kmax;

	std::ofstream out("katz_output.csv");
	out << "node_id,katz_centrality,in_degree,out_degree\n";
	out << std::fixed << std::setprecision(6);
	for (int i = 0; i < n; ++i) out << idx2id[i] << "," << x[i] << "," << indeg[i] << "," << outdeg[i] << "\n";
	out.close();
	std::cout << "Wrote 'katz_output.csv' (" << n << " rows).\n";

	std::cout << "Top 10 nodes by Katz centrality:\n";
	std::vector<int> ids(n); for (int i = 0; i < n; ++i) ids[i] = i;
	std::sort(ids.begin(), ids.end(), [&](int a, int b){ return x[a] > x[b]; });
	for (int k = 0; k < std::min(10, n); ++k) {
		int i = ids[k];
		std::cout << k+1 << ") id=" << idx2id[i] << ", katz=" << x[i] << ", indeg=" << indeg[i] << "\n";
	}

	return 0;
}

