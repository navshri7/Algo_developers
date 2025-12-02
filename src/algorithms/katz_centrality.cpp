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
 * Computes Katz centrality for undirected graphs.
 * 
 * Katz centrality measures the influence of a node in a network by considering
 * both direct connections and indirect connections through paths of varying lengths.
 * The centrality is computed using the formula: x = (I - alpha*A^T)^(-1) * beta
 */
class KatzCentrality {
private:
    int n;                          // Number of vertices
    vector<vector<int>> adj;        // Adjacency list representation
    vector<double> katz;            // Computed Katz centrality values
    long long memoryUsed;           // Memory usage in bytes
    double alpha;                   // Attenuation factor (controls path weight decay)
    double beta;                    // Base centrality value for each node
    
public:
    /**
     * Constructor for KatzCentrality.
     * 
     * @param vertices Number of vertices in the graph
     * @param alpha_param Attenuation factor (if <= 0, will be auto-computed)
     */
    KatzCentrality(int vertices, double alpha_param = -1.0) 
        : n(vertices), adj(vertices), katz(vertices, 0.0), memoryUsed(0), 
          alpha(alpha_param), beta(1.0) {
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
        adj[v].push_back(u);
        memoryUsed += 2 * sizeof(int);
    }
    
    /**
     * Estimates the spectral radius (largest eigenvalue) of the adjacency matrix
     * using the power iteration method.
     * 
     * @return Estimated largest eigenvalue
     * 
     * The spectral radius is needed to determine a valid alpha parameter that
     * ensures convergence (alpha must be < 1/spectral_radius).
     */
    double estimateSpectralRadius() {
        // Initialize with normalized random vector
        vector<double> x(n, 1.0 / sqrt(max(1, n)));
        vector<double> y(n);
        double lambda = 0.0;
        
        // Power iteration: repeatedly multiply by A^T and normalize
        for (int it = 0; it < 1000; ++it) {
            // y = A^T * x
            fill(y.begin(), y.end(), 0.0);
            for (int u = 0; u < n; ++u) {
                for (int v : adj[u]) {
                    y[v] += x[u];
                }
            }
            
            // Normalize y to unit vector
            double norm = 0.0;
            for (double v : y) norm += v * v;
            norm = sqrt(norm);
            if (norm == 0.0) break;
            
            for (int i = 0; i < n; ++i) x[i] = y[i] / norm;
            
            // Compute Rayleigh quotient: x^T * A * x
            double rq = 0.0;
            fill(y.begin(), y.end(), 0.0);
            for (int u = 0; u < n; ++u) {
                for (int v : adj[u]) {
                    y[v] += x[u];
                }
            }
            for (int i = 0; i < n; ++i) rq += x[i] * y[i];
            
            // Check for convergence
            if (it > 0 && abs(rq - lambda) < 1e-9) {
                lambda = rq;
                break;
            }
            lambda = rq;
        }
        
        return lambda;
    }
    
    /**
     * Computes Katz centrality for all nodes using iterative method.
     * 
     * @return Vector of Katz centrality values (normalized to [0,1])
     * 
     * Uses the iterative formula: x_{t+1} = alpha * A^T * x_t + beta
     * Converges when ||x_{t+1} - x_t|| < tolerance
     */
    vector<double> computeKatz() {
        auto start = high_resolution_clock::now();
        
        // Estimate alpha if not provided
        if (alpha <= 0.0) {
            double lambda_max = estimateSpectralRadius();
            if (lambda_max > 0.0) {
                // Set alpha to 85% of maximum safe value for convergence
                alpha = 0.85 / lambda_max;
            } else {
                alpha = 0.01;  // Fallback for disconnected graphs
            }
        }
        
        // Initialize centrality vectors
        vector<double> x(n, 0.0);
        vector<double> xnext(n, 0.0);
        const int max_iter = 10000;
        const double tol = 1e-9;
        
        // Iterative computation: x_{t+1} = alpha * A^T * x_t + beta
        for (int it = 0; it < max_iter; ++it) {
            // xnext = alpha * A^T * x + beta
            fill(xnext.begin(), xnext.end(), beta);
            for (int u = 0; u < n; ++u) {
                if (x[u] != 0.0) {
                    for (int v : adj[u]) {
                        xnext[v] += alpha * x[u];
                    }
                }
            }
            
            // Check convergence using L2 norm of difference
            double diff = 0.0;
            for (int i = 0; i < n; ++i) {
                double d = xnext[i] - x[i];
                diff += d * d;
            }
            diff = sqrt(diff);
            
            x.swap(xnext);
            
            if (diff < tol) break;
        }
        
        // Normalize to [0, 1] range
        double kmax = 0.0;
        for (double v : x) if (v > kmax) kmax = v;
        if (kmax > 0.0) {
            for (double &v : x) v /= kmax;
        }
        
        katz = x;
        return katz;
    }
    
    /**
     * Returns the maximum Katz centrality value.
     * 
     * @return Maximum centrality value in the graph
     */
    double getMaxKatz() {
        return *max_element(katz.begin(), katz.end());
    }
    
    /**
     * Returns the alpha parameter used in computation.
     * 
     * @return Alpha (attenuation factor)
     */
    double getAlpha() {
        return alpha;
    }
    
    /**
     * Returns the total memory usage in bytes.
     * 
     * @return Memory usage in bytes
     */
    long long getMemoryUsage() {
        return memoryUsed;
    }
    
    /**
     * Returns the computed Katz centrality values.
     * 
     * @return Vector of centrality values for all nodes
     */
    vector<double> getKatz() {
        return katz;
    }
};

/**
 * Writes detailed analysis results to a text file.
 * 
 * @param outputFile Output file path
 * @param datasetName Name of the dataset
 * @param n Number of vertices
 * @param m Number of edges
 * @param maxKatz Maximum Katz centrality value
 * @param runtime Computation time in seconds
 * @param memory Memory usage in bytes
 * @param alpha Alpha parameter used
 * @param katz Vector of all Katz centrality values
 * 
 * Output includes graph statistics, performance metrics, and top 100 nodes by centrality.
 */
void writeDetailedResults(const string& outputFile, const string& datasetName,
                         int n, int m, double maxKatz, double runtime, 
                         long long memory, double alpha, const vector<double>& katz) {
    ofstream out(outputFile);
    
    out << "Dataset: " << datasetName << "\n";
    out << "Vertices: " << n << "\n";
    out << "Edges: " << m << "\n";
    out << "Max Katz Centrality: " << fixed << setprecision(6) << maxKatz << "\n";
    out << "Alpha Parameter: " << fixed << setprecision(6) << alpha << "\n";
    out << "Runtime (seconds): " << fixed << setprecision(6) << runtime << "\n";
    out << "Memory Usage (MB): " << fixed << setprecision(2) << (memory / 1048576.0) << "\n";
    
    out << "\n=== Top 100 Vertices by Katz Centrality ===\n";
    out << "Rank\tVertex_ID\tKatz_Centrality\n";
    
    // Sort nodes by centrality (descending)
    vector<pair<double, int>> ranked;
    for (int i = 0; i < n; i++) {
        ranked.push_back({katz[i], i});
    }
    sort(ranked.begin(), ranked.end(), [](auto& a, auto& b) {
        if (a.first != b.first) return a.first > b.first;
        return a.second < b.second;  // Tie-break by vertex ID
    });
    
    // Write top 100 nodes
    for (int i = 0; i < min(100, (int)ranked.size()); i++) {
        out << (i+1) << "\t" << (ranked[i].second + 1) << "\t" 
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
 * @param maxKatz Maximum Katz centrality value
 * @param runtime Computation time in seconds
 * @param memory Memory usage in bytes
 * @param avgDegree Average degree of the graph
 * @param density Edge density of the graph
 * @param alpha Alpha parameter used
 * 
 * Creates CSV header if file doesn't exist, otherwise appends data.
 */
void writeCSVSummary(const string& csvFile, const string& datasetName,
                    int n, int m, double maxKatz, double runtime, long long memory,
                    double avgDegree, double density, double alpha) {
    bool fileExists = ifstream(csvFile).good();
    ofstream out(csvFile, ios::app);
    
    // Write header if file is new
    if (!fileExists) {
        out << "Dataset,Vertices,Edges,MaxKatz,Runtime_sec,Memory_MB,AvgDegree,Density,Alpha\n";
    }
    
    // Append data row
    out << datasetName << "," << n << "," << m << "," 
        << fixed << setprecision(6) << maxKatz << ","
        << fixed << setprecision(6) << runtime << ","
        << fixed << setprecision(2) << (memory / 1048576.0) << ","
        << fixed << setprecision(4) << avgDegree << ","
        << scientific << setprecision(6) << density << ","
        << fixed << setprecision(6) << alpha << "\n";
    
    out.close();
}

/**
 * Main function: Computes Katz centrality from an edge list file.
 * 
 * Usage: program <input_file> <output_dir> [dataset_name]
 * 
 * Input file format:
 *   First line: n m (number of vertices and edges)
 *   Following lines: u v (edge from vertex u to vertex v, 1-indexed)
 * 
 * @param argc Number of command-line arguments
 * @param argv Command-line arguments
 * @return 0 on success, 1 on error
 */
int main(int argc, char* argv[]) {
    if (argc < 3) {
        cerr << "Usage: " << argv[0] << " <input_file> <output_dir> [dataset_name]\n";
        return 1;
    }
    
    // Parse command-line arguments
    string inputFile = argv[1];
    string outputDir = argv[2];
    string datasetName = (argc >= 4) ? argv[3] : inputFile;
    
    // Create output directory if it doesn't exist
    system(("mkdir -p " + outputDir).c_str());
    
    // Open input file
    ifstream inFile(inputFile);
    if (!inFile) {
        cerr << "Error: Cannot open input file " << inputFile << "\n";
        return 1;
    }
    
    // Skip comment lines and read graph dimensions
    string line;
    while (getline(inFile, line)) {
        if (line.empty() || line[0] == '#') continue;
        break;
    }
    
    istringstream iss(line);
    int n, m;
    iss >> n >> m;
    
    cout << "Dataset: " << datasetName << "\n";
    cout << "Vertices: " << n << ", Edges: " << m << "\n";
    
    // Read edges and build graph
    auto readStart = high_resolution_clock::now();
    KatzCentrality katz(n);
    
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
            katz.addEdge(u - 1, v - 1);  // Convert to 0-indexed
            edgeCount++;
        }
    }
    inFile.close();
    
    auto readEnd = high_resolution_clock::now();
    double readTime = duration_cast<milliseconds>(readEnd - readStart).count() / 1000.0;
    
    cout << "Graph loaded in " << fixed << setprecision(3) << readTime << " seconds\n";
    cout << "Unique edges: " << edgeCount << "\n";
    
    // Compute Katz centrality
    cout << "Computing Katz centrality...\n";
    auto computeStart = high_resolution_clock::now();
    vector<double> katzVec = katz.computeKatz();
    auto computeEnd = high_resolution_clock::now();
    
    double computeTime = duration_cast<milliseconds>(computeEnd - computeStart).count() / 1000.0;
    long long memoryUsage = katz.getMemoryUsage();
    
    cout << "Computation complete in " << fixed << setprecision(6) << computeTime << " seconds\n";
    
    // Get results and statistics
    double maxKatz = katz.getMaxKatz();
    double alpha = katz.getAlpha();
    cout << "Maximum Katz centrality: " << fixed << setprecision(6) << maxKatz << "\n";
    cout << "Alpha parameter: " << fixed << setprecision(6) << alpha << "\n";
    cout << "Memory usage: " << fixed << setprecision(2) << (memoryUsage / 1048576.0) << " MB\n";
    
    // Calculate graph statistics
    double avgDegree = (2.0 * edgeCount) / n;
    double density = (2.0 * edgeCount) / (n * (n - 1.0));
    
    // Define output file paths
    string detailedOutput = outputDir + "/" + datasetName + "_detailed.txt";
    string csvOutput = outputDir + "/summary.csv";
    
    // Write results
    writeDetailedResults(detailedOutput, datasetName, n, edgeCount, maxKatz,
                        computeTime, memoryUsage, alpha, katzVec);
    writeCSVSummary(csvOutput, datasetName, n, edgeCount, maxKatz,
                   computeTime, memoryUsage, avgDegree, density, alpha);
    
    cout << "\nResults written to:\n";
    cout << "  - " << detailedOutput << "\n";
    cout << "  - " << csvOutput << "\n";
    
    return 0;
}