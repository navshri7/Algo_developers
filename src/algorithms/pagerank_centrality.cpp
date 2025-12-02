#include <iostream>
#include <fstream>
#include <vector>
#include <algorithm>
#include <map>
#include <chrono>
#include <iomanip>
#include <sstream>
#include <set>
#include <cmath>

using namespace std;
using namespace std::chrono;

/**
 * Computes PageRank centrality for undirected graphs.
 * 
 * PageRank measures the importance of nodes based on the link structure of the graph.
 * Originally developed by Google for ranking web pages, it simulates a random walker
 * that follows edges with probability d (damping factor) or teleports to a random
 * node with probability (1-d).
 */
class PageRankCentrality {
private:
    int n;                          // Number of vertices
    vector<vector<int>> adj;        // Adjacency list representation
    vector<double> pagerank;        // Computed PageRank values
    long long memoryUsed;           // Memory usage in bytes
    double damping;                 // Damping factor (typically 0.85)
    double tol;                     // Convergence tolerance
    int maxIter;                    // Maximum iterations

public:
    /**
     * Constructor for PageRankCentrality.
     * 
     * @param vertices Number of vertices in the graph
     * @param damping_param Damping factor controlling random walk vs teleportation (default: 0.85)
     * @param tol_param Convergence tolerance (default: 1e-9)
     * @param max_iter_param Maximum number of iterations (default: 10000)
     */
    PageRankCentrality(int vertices,
                       double damping_param = 0.85,
                       double tol_param = 1e-9,
                       int max_iter_param = 10000)
        : n(vertices),
          adj(vertices),
          pagerank(vertices, 0.0),
          memoryUsed(0),
          damping(damping_param),
          tol(tol_param),
          maxIter(max_iter_param) {
        memoryUsed = vertices * (sizeof(vector<int>) + sizeof(double));
    }

    /**
     * Adds an undirected edge to the graph.
     * 
     * @param u First vertex (0-indexed)
     * @param v Second vertex (0-indexed)
     * 
     * Self-loops are ignored. Each edge is stored bidirectionally.
     */
    void addEdge(int u, int v) {
        if (u == v) return;  // Skip self-loops
        adj[u].push_back(v);
        adj[v].push_back(u);  // Undirected graph
        memoryUsed += 2 * sizeof(int);
    }

    /**
     * Computes PageRank for all nodes using iterative power method.
     * 
     * @return Vector of PageRank values (normalized to [0,1])
     * 
     * Algorithm:
     * - Initialize all nodes with equal PageRank (1/n)
     * - Iteratively update: PR(v) = (1-d)/n + d * sum(PR(u)/deg(u)) for all u->v
     * - Handle dangling nodes (no outgoing edges) by redistributing their PR
     * - Converge when L1 norm of change < tolerance
     * - Normalize final values so max PR = 1
     */
    vector<double> computePageRank() {
        if (n == 0) return pagerank;

        // Initialize with uniform distribution
        vector<double> x(n, 1.0 / n);
        vector<double> xnext(n, 0.0);

        const double d = damping;
        const double one_minus_d = 1.0 - d;

        for (int it = 0; it < maxIter; ++it) {
            // Handle dangling nodes: sum PageRank of nodes with no out-links
            double danglingSum = 0.0;
            for (int i = 0; i < n; ++i) {
                if (adj[i].empty()) {
                    danglingSum += x[i];
                }
            }

            // Base value: teleportation probability + redistributed dangling mass
            double base = one_minus_d / n + d * danglingSum / n;
            fill(xnext.begin(), xnext.end(), base);

            // Distribute PageRank along edges
            for (int u = 0; u < n; ++u) {
                int deg = (int)adj[u].size();
                if (deg == 0) continue;  // Skip dangling nodes (already handled)
                
                // Each neighbor receives equal share of u's PageRank
                double share = d * x[u] / deg;
                for (int v : adj[u]) {
                    xnext[v] += share;
                }
            }

            // Check convergence using L1 norm of difference
            double diff = 0.0;
            for (int i = 0; i < n; ++i) {
                diff += fabs(xnext[i] - x[i]);
            }

            x.swap(xnext);

            if (diff < tol) {
                // Converged
                break;
            }
        }

        // Normalize to [0, 1] range (max PR = 1)
        double maxPR = 0.0;
        for (double v : x) if (v > maxPR) maxPR = v;
        if (maxPR > 0.0) {
            for (double &v : x) v /= maxPR;
        }

        pagerank = x;
        return pagerank;
    }

    /**
     * Returns the maximum PageRank value.
     * 
     * @return Maximum PageRank in the graph
     */
    double getMaxPageRank() const {
        return *max_element(pagerank.begin(), pagerank.end());
    }

    /**
     * Returns the damping factor used in computation.
     * 
     * @return Damping factor
     */
    double getDamping() const {
        return damping;
    }

    /**
     * Returns the total memory usage in bytes.
     * 
     * @return Memory usage in bytes
     */
    long long getMemoryUsage() const {
        return memoryUsed;
    }

    /**
     * Returns the computed PageRank values.
     * 
     * @return Vector of PageRank values for all nodes
     */
    vector<double> getPageRank() const {
        return pagerank;
    }
};

/**
 * Writes detailed analysis results to a text file.
 * 
 * @param outputFile Output file path
 * @param datasetName Name of the dataset
 * @param n Number of vertices
 * @param m Number of edges
 * @param maxPR Maximum PageRank value
 * @param runtime Computation time in seconds
 * @param memory Memory usage in bytes
 * @param damping Damping factor used
 * @param pagerank Vector of all PageRank values
 * 
 * Output includes graph statistics, performance metrics, and top 100 nodes by PageRank.
 */
void writeDetailedResults(const string &outputFile, const string &datasetName,
                          int n, int m, double maxPR, double runtime,
                          long long memory, double damping,
                          const vector<double> &pagerank) {
    ofstream out(outputFile);

    out << "Dataset: " << datasetName << "\n";
    out << "Vertices: " << n << "\n";
    out << "Edges: " << m << "\n";
    out << "Max PageRank Centrality (normalized): " << fixed << setprecision(6) << maxPR << "\n";
    out << "Damping Factor: " << fixed << setprecision(6) << damping << "\n";
    out << "Runtime (seconds): " << fixed << setprecision(6) << runtime << "\n";
    out << "Memory Usage (MB): " << fixed << setprecision(2) << (memory / 1048576.0) << "\n";

    out << "\n=== Top 100 Vertices by PageRank Centrality ===\n";
    out << "Rank\tVertex_ID\tPageRank\n";

    // Sort nodes by PageRank (descending)
    vector<pair<double,int>> ranked;
    ranked.reserve(n);
    for (int i = 0; i < n; ++i) {
        ranked.push_back({pagerank[i], i});
    }
    sort(ranked.begin(), ranked.end(),
         [](const pair<double,int> &a, const pair<double,int> &b) {
             if (a.first != b.first) return a.first > b.first;
             return a.second < b.second;  // Tie-break by vertex ID
         });

    // Write top 100 nodes
    int limit = min(100, (int)ranked.size());
    for (int i = 0; i < limit; ++i) {
        out << (i + 1) << "\t" << (ranked[i].second + 1) << "\t"
            << fixed << setprecision(6) << ranked[i].first << "\n";
    }

    out.close();
}

/**
 * Writes or appends summary statistics to a CSV file.
 * 
 * @param csvFile CSV file path
 * @param datasetName Name of the dataset
 * @param n Number of vertices
 * @param m Number of edges
 * @param maxPR Maximum PageRank value
 * @param runtime Computation time in seconds
 * @param memory Memory usage in bytes
 * @param avgDegree Average degree of the graph
 * @param density Edge density of the graph
 * @param damping Damping factor used
 * 
 * Creates CSV header if file doesn't exist, otherwise appends data.
 */
void writeCSVSummary(const string &csvFile, const string &datasetName,
                     int n, int m, double maxPR, double runtime,
                     long long memory, double avgDegree, double density,
                     double damping) {
    bool fileExists = ifstream(csvFile).good();
    ofstream out(csvFile, ios::app);

    // Write header if file is new
    if (!fileExists) {
        out << "Dataset,Vertices,Edges,MaxPageRank,Runtime_sec,Memory_MB,"
               "AvgDegree,Density,Damping\n";
    }

    // Append data row
    out << datasetName << "," << n << "," << m << ","
        << fixed << setprecision(6) << maxPR << ","
        << fixed << setprecision(6) << runtime << ","
        << fixed << setprecision(2) << (memory / 1048576.0) << ","
        << fixed << setprecision(4) << avgDegree << ","
        << scientific << setprecision(6) << density << ","
        << fixed << setprecision(6) << damping << "\n";

    out.close();
}

/**
 * Main function: Computes PageRank centrality from an edge list file.
 * 
 * Usage: program <input_file> <output_dir> [dataset_name] [damping]
 * 
 * Input file format:
 *   First line: n m (number of vertices and edges)
 *   Following lines: u v (edge from vertex u to vertex v, 1-indexed)
 * 
 * @param argc Number of command-line arguments
 * @param argv Command-line arguments
 * @return 0 on success, 1 on error
 */
int main(int argc, char *argv[]) {
    if (argc < 3) {
        cerr << "Usage: " << argv[0]
             << " <input_file> <output_dir> [dataset_name] [damping]\n";
        return 1;
    }

    // Parse command-line arguments
    string inputFile  = argv[1];
    string outputDir  = argv[2];
    string datasetName = (argc >= 4) ? argv[3] : inputFile;

    // Parse optional damping factor
    double damping = 0.85;
    if (argc >= 5) {
        damping = stod(argv[4]);
        if (damping <= 0.0 || damping >= 1.0) {
            cerr << "Warning: damping factor should be in (0,1). Using default 0.85.\n";
            damping = 0.85;
        }
    }

    // Create output directory if needed
    system(("mkdir -p " + outputDir).c_str());

    // Open input file
    ifstream inFile(inputFile);
    if (!inFile) {
        cerr << "Error: Cannot open input file " << inputFile << "\n";
        return 1;
    }

    // Skip comment lines starting with '#'
    string line;
    while (getline(inFile, line)) {
        if (line.empty() || line[0] == '#') continue;
        break;
    }

    // First non-comment line contains graph dimensions
    istringstream iss(line);
    int n, m;
    iss >> n >> m;

    cout << "Dataset: " << datasetName << "\n";
    cout << "Vertices: " << n << ", Edges: " << m << "\n";

    // Read edges and build graph
    auto readStart = high_resolution_clock::now();
    PageRankCentrality pr(n, damping);

    int edgeCount = 0;
    set<pair<int,int>> uniqueEdges;  // Track unique edges to avoid duplicates

    int u, v;
    while (inFile >> u >> v) {
        // Validate edge
        if (u == v) continue;  // Skip self-loops
        if (u < 1 || u > n || v < 1 || v > n) continue;  // Skip out-of-range vertices

        // Ensure undirected edges are stored once
        int minV = min(u, v);
        int maxV = max(u, v);
        if (uniqueEdges.find({minV, maxV}) == uniqueEdges.end()) {
            uniqueEdges.insert({minV, maxV});
            pr.addEdge(u - 1, v - 1);  // Convert to 0-indexed
            edgeCount++;
        }
    }
    inFile.close();

    auto readEnd = high_resolution_clock::now();
    double readTime = duration_cast<milliseconds>(readEnd - readStart).count() / 1000.0;

    cout << "Graph loaded in " << fixed << setprecision(3) << readTime << " seconds\n";
    cout << "Unique edges: " << edgeCount << "\n";

    // Compute PageRank centrality
    cout << "Computing PageRank centrality...\n";
    auto computeStart = high_resolution_clock::now();
    vector<double> prVec = pr.computePageRank();
    auto computeEnd = high_resolution_clock::now();

    double computeTime = duration_cast<milliseconds>(computeEnd - computeStart).count() / 1000.0;
    long long memoryUsage = pr.getMemoryUsage();

    cout << "Computation complete in " << fixed << setprecision(6) << computeTime << " seconds\n";

    // Get results and statistics
    double maxPR = pr.getMaxPageRank();
    cout << "Maximum PageRank (normalized): " << fixed << setprecision(6) << maxPR << "\n";
    cout << "Damping factor: " << fixed << setprecision(6) << damping << "\n";
    cout << "Memory usage: " << fixed << setprecision(2) << (memoryUsage / 1048576.0) << " MB\n";

    // Calculate graph statistics
    double avgDegree = (2.0 * edgeCount) / n;
    double density   = (2.0 * edgeCount) / (n * (n - 1.0));

    // Define output file paths
    string detailedOutput = outputDir + "/" + datasetName + "_pagerank_detailed.txt";
    string csvOutput      = outputDir + "/summary_pagerank.csv";

    // Write results
    writeDetailedResults(detailedOutput, datasetName, n, edgeCount,
                         maxPR, computeTime, memoryUsage, damping, prVec);
    writeCSVSummary(csvOutput, datasetName, n, edgeCount,
                    maxPR, computeTime, memoryUsage, avgDegree, density, damping);

    cout << "\nResults written to:\n";
    cout << "  - " << detailedOutput << "\n";
    cout << "  - " << csvOutput << "\n";

    return 0;
}