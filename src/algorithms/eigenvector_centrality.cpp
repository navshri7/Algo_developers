/**
 * Eigenvector Centrality Algorithm Implementation for Undirected Graphs
 * 
 * This program computes eigenvector centrality for all vertices in an undirected graph
 * using the power iteration method. Eigenvector centrality is a measure of node
 * importance based on the principle that connections to high-scoring nodes contribute
 * more to a node's score than connections to low-scoring nodes.
 * 
 * Mathematically, eigenvector centrality is defined by the eigenvector equation:
 * Ax = λx
 * 
 * where:
 * - A is the adjacency matrix
 * - x is the eigenvector (centrality scores)
 * - λ is the largest eigenvalue
 * 
 * The centrality of node i is: x_i = (1/λ) × Σ(x_j) for all neighbors j
 * 
 * This means a node's centrality is proportional to the sum of its neighbors' centralities.
 * 
 * Applications:
 * - Google's PageRank is a variant of eigenvector centrality
 * - Identifying influential nodes in social networks
 * - Finding authoritative papers in citation networks
 * - Detecting key proteins in biological networks
 * 
 * Date: December 2, 2025
 * 
 * Time Complexity: O(iterations × m) where m = edges, typically iterations ≈ 100-10000
 * Space Complexity: O(n + m) where n = vertices
 * 
 * Input Format: 
 *   - First line: n (vertices) m (edges)
 *   - Following lines: u v (edge between vertices u and v)
 *   - Vertex IDs should be 1-indexed
 * 
 * Output:
 *   - Detailed text file with statistics and top vertices by eigenvector centrality
 *   - CSV summary file with performance metrics and largest eigenvalue
 * 
 * Reference: Bonacich, P. (1987). "Power and Centrality: A Family of Measures"
 */

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
  * EigenvectorCentrality Class
  * 
  * Implements power iteration method to compute the dominant eigenvector of the
  * adjacency matrix (or its transpose for directed graphs).
  * 
  * The power iteration method:
  * 1. Start with a random vector x₀
  * 2. Repeatedly compute x_{k+1} = A^T × x_k
  * 3. Normalize after each iteration
  * 4. Continue until convergence
  * 
  * Why A^T (transpose)?
  * For undirected graphs, A = A^T, so it doesn't matter.
  * For directed graphs, A^T gives "authority" scores (based on incoming edges),
  * while A gives "hub" scores (based on outgoing edges).
  * 
  * Convergence:
  * By the Perron-Frobenius theorem, for connected graphs with non-negative edges,
  * the power iteration converges to the eigenvector corresponding to the largest
  * eigenvalue (spectral radius).
  */
 class EigenvectorCentrality {
 private:
     int n;                      // Number of vertices
     vector<vector<int>> adj;    // Adjacency list
     vector<double> eigen;       // Eigenvector centrality scores
     long long memoryUsed;       // Estimated memory usage in bytes
     double lambda;              // Largest eigenvalue (spectral radius)
     
 public:
     /**
      * Constructor: Initialize the EigenvectorCentrality object
      * 
      * @param vertices Number of vertices in the graph
      * 
      * Initializes data structures for storing the graph and centrality scores.
      * All centrality scores start at 0.0 and will be computed by power iteration.
      */
     EigenvectorCentrality(int vertices) 
         : n(vertices), adj(vertices), eigen(vertices, 0.0), memoryUsed(0), lambda(0.0) {
         // Estimate initial memory usage
         memoryUsed = vertices * (sizeof(vector<int>) + sizeof(double));
     }
     
     /**
      * Add an edge to the graph
      * 
      * @param u First vertex (0-indexed)
      * @param v Second vertex (0-indexed)
      * 
      * Adds an undirected edge between vertices u and v.
      * Self-loops are ignored. Updates memory usage estimate.
      */
     void addEdge(int u, int v) {
         // Ignore self-loops (they don't affect eigenvector centrality in most contexts)
         if (u == v) return;
         
         // Add edge in both directions (undirected graph)
         adj[u].push_back(v);
         adj[v].push_back(u);
         
         // Update memory usage for two integers (bidirectional edge)
         memoryUsed += 2 * sizeof(int);
     }
     
     /**
      * Compute eigenvector centrality using power iteration method
      * 
      * @return Vector containing eigenvector centrality for each vertex, normalized to [0,1]
      * 
      * Algorithm: Power Iteration Method
      * 
      * The power iteration finds the dominant eigenvector by repeatedly multiplying
      * a starting vector by the adjacency matrix (or its transpose).
      * 
      * Steps:
      * 1. Initialize x to uniform vector (1/√n, 1/√n, ..., 1/√n)
      * 2. Repeat until convergence:
      *    a. Compute y = A^T × x (matrix-vector multiplication)
      *    b. Normalize: x = y / ||y||₂
      *    c. Compute eigenvalue estimate (Rayleigh quotient)
      *    d. Check convergence: |λ_new - λ_old| < tolerance
      * 3. Scale final vector to [0, 1] range
      * 
      * Matrix-Vector Multiplication:
      * For undirected graphs, y[v] = Σ x[u] for all neighbors u of v
      * This is equivalent to A^T × x since A = A^T for undirected graphs
      * 
      * Rayleigh Quotient:
      * λ ≈ (x^T A^T x) / (x^T x) = x^T (A^T x)
      * Since x is normalized, x^T x = 1, so λ ≈ x^T (A^T x)
      * 
      * Convergence Criteria:
      * - Maximum iterations: 10,000 (typically converges in 100-1000)
      * - Tolerance: 1e-9 (eigenvalue change between iterations)
      * 
      * Why This Works:
      * By the power iteration theorem, repeated multiplication by A amplifies
      * the component of x in the direction of the dominant eigenvector, causing
      * convergence to that eigenvector.
      * 
      * Time Complexity: O(iterations × m) where m = number of edges
      * Space Complexity: O(n) for temporary vectors
      */
     vector<double> computeEigenvector() {
         // Initialize x to normalized uniform vector
         // Starting value: 1/√n for each component (unit vector)
         vector<double> x(n, 1.0 / sqrt(max(1, n)));
         vector<double> y(n);  // Temporary vector for matrix-vector product
         lambda = 0.0;
         
         const int max_iter = 10000;   // Maximum iterations before stopping
         const double tol = 1e-9;       // Convergence tolerance for eigenvalue
         
         // Power iteration loop
         for (int it = 0; it < max_iter; ++it) {
             // Step 1: Compute y = A^T × x
             // For undirected graphs: y[v] = sum of x[u] for all neighbors u
             // This accumulates scores from incoming edges (A^T operation)
             fill(y.begin(), y.end(), 0.0);
             for (int u = 0; u < n; ++u) {
                 for (int v : adj[u]) {
                     // Edge u->v contributes x[u] to y[v]
                     // In undirected graphs, we store edges both ways
                     y[v] += x[u];
                 }
             }
             
             // Step 2: Normalize y to get unit vector
             // ||y||₂ = √(y₁² + y₂² + ... + yₙ²)
             double norm = 0.0;
             for (double v : y) norm += v * v;
             norm = sqrt(norm);
             
             // Handle zero vector (disconnected graph or all-zero start)
             if (norm == 0.0) break;
             
             // x = y / ||y||  (make x a unit vector)
             for (int i = 0; i < n; ++i) x[i] = y[i] / norm;
             
             // Step 3: Compute eigenvalue estimate using Rayleigh quotient
             // λ = x^T (A^T x) = x^T y_new
             // where y_new = A^T x (recompute to get accurate eigenvalue)
             double rq = 0.0;
             fill(y.begin(), y.end(), 0.0);
             for (int u = 0; u < n; ++u) {
                 for (int v : adj[u]) {
                     y[v] += x[u];
                 }
             }
             // Dot product: x^T × y
             for (int i = 0; i < n; ++i) rq += x[i] * y[i];
             
             // Step 4: Check convergence
             // If eigenvalue estimate hasn't changed much, we've converged
             if (it > 0 && abs(rq - lambda) < tol) {
                 lambda = rq;
                 break;
             }
             lambda = rq;
         }
         
         // Final normalization: Scale to [0, 1] range for interpretability
         // Find maximum value and divide all values by it
         double emax = 0.0;
         for (double v : x) if (v > emax) emax = v;
         if (emax > 0.0) {
             for (double &v : x) v /= emax;
         }
         
         eigen = x;
         return eigen;
     }
     
     /**
      * Get the maximum eigenvector centrality value
      * 
      * @return Maximum centrality score (should be 1.0 after normalization)
      * 
      * The node with maximum eigenvector centrality is the most "important"
      * node according to the network structure. After normalization to [0,1],
      * this value should be exactly 1.0.
      */
     double getMaxEigen() {
         return *max_element(eigen.begin(), eigen.end());
     }
     
     /**
      * Get the largest eigenvalue (spectral radius)
      * 
      * @return Largest eigenvalue λ of the adjacency matrix
      * 
      * The largest eigenvalue provides information about the graph structure:
      * - For regular graphs: λ = degree
      * - For complete graphs: λ = n - 1
      * - Generally: λ ≤ maximum degree
      * - Larger λ indicates more connectivity/clustering
      * 
      * This value is also useful for:
      * - Estimating convergence speed (larger λ means faster convergence)
      * - Bounding other spectral properties
      * - Network resilience analysis
      */
     double getLambda() {
         return lambda;
     }
     
     /**
      * Get estimated memory usage of the algorithm
      * 
      * @return Estimated memory usage in bytes
      * 
      * Provides an approximation of memory consumed by the data structures.
      */
     long long getMemoryUsage() {
         return memoryUsed;
     }
     
     /**
      * Get the complete eigenvector centrality vector
      * 
      * @return Vector of centrality values for all vertices, normalized to [0,1]
      * 
      * Useful for further analysis or comparison with other centrality measures.
      */
     vector<double> getEigen() {
         return eigen;
     }
 };
 
 /**
  * Write detailed results to a text file
  * 
  * @param outputFile Path to the output file
  * @param datasetName Name of the dataset
  * @param n Number of vertices
  * @param m Number of edges
  * @param maxEigen Maximum eigenvector centrality (should be 1.0)
  * @param runtime Computation time in seconds
  * @param memory Memory usage in bytes
  * @param lambda Largest eigenvalue of the adjacency matrix
  * @param eigen Vector of eigenvector centrality values
  * 
  * Generates a comprehensive report including:
  * - Dataset statistics
  * - Performance metrics
  * - Largest eigenvalue (spectral radius)
  * - Top 100 vertices by eigenvector centrality
  * 
  * The largest eigenvalue is reported because it provides valuable information
  * about the graph structure and the convergence properties of the algorithm.
  */
 void writeDetailedResults(const string& outputFile, const string& datasetName,
                          int n, int m, double maxEigen, double runtime, 
                          long long memory, double lambda, const vector<double>& eigen) {
     ofstream out(outputFile);
     
     // Write header and statistics
     out << "Dataset: " << datasetName << "\n";
     out << "Vertices: " << n << "\n";
     out << "Edges: " << m << "\n";
     out << "Max Eigenvector Centrality: " << fixed << setprecision(6) << maxEigen << "\n";
     out << "Largest Eigenvalue (Lambda): " << fixed << setprecision(6) << lambda << "\n";
     out << "Runtime (seconds): " << fixed << setprecision(6) << runtime << "\n";
     out << "Memory Usage (MB): " << fixed << setprecision(2) << (memory / 1048576.0) << "\n";
     
     // Write top vertices by eigenvector centrality
     out << "\n=== Top 100 Vertices by Eigenvector Centrality ===\n";
     out << "Rank\tVertex_ID\tEigen_Centrality\n";
     
     // Create ranking by sorting (centrality, vertex_id) pairs
     vector<pair<double, int>> ranked;
     for (int i = 0; i < n; i++) {
         ranked.push_back({eigen[i], i});
     }
     
     // Sort by centrality (descending), then by vertex ID (ascending) for ties
     sort(ranked.begin(), ranked.end(), [](auto& a, auto& b) {
         if (a.first != b.first) return a.first > b.first;
         return a.second < b.second;
     });
     
     // Output top 100 vertices (convert to 1-indexed)
     for (int i = 0; i < min(100, (int)ranked.size()); i++) {
         out << (i+1) << "\t" << (ranked[i].second + 1) << "\t" 
             << fixed << setprecision(6) << ranked[i].first << "\n";
     }
     
     out.close();
 }
 
 /**
  * Write summary statistics to CSV file
  * 
  * @param csvFile Path to the CSV file
  * @param datasetName Name of the dataset
  * @param n Number of vertices
  * @param m Number of edges
  * @param maxEigen Maximum eigenvector centrality
  * @param runtime Computation time in seconds
  * @param memory Memory usage in bytes
  * @param avgDegree Average degree of vertices
  * @param density Graph density
  * @param lambda Largest eigenvalue
  * 
  * Appends a row to the CSV summary file with key metrics including the
  * largest eigenvalue, which is useful for comparing graph structures.
  * Creates the file with headers if it doesn't exist.
  */
 void writeCSVSummary(const string& csvFile, const string& datasetName,
                     int n, int m, double maxEigen, double runtime, long long memory,
                     double avgDegree, double density, double lambda) {
     // Check if file exists to determine if we need headers
     bool fileExists = ifstream(csvFile).good();
     ofstream out(csvFile, ios::app);
     
     // Write header row if this is a new file
     if (!fileExists) {
         out << "Dataset,Vertices,Edges,MaxEigen,Runtime_sec,Memory_MB,AvgDegree,Density,Lambda\n";
     }
     
     // Write data row with appropriate formatting
     out << datasetName << "," << n << "," << m << "," 
         << fixed << setprecision(6) << maxEigen << ","
         << fixed << setprecision(6) << runtime << ","
         << fixed << setprecision(2) << (memory / 1048576.0) << ","
         << fixed << setprecision(4) << avgDegree << ","
         << scientific << setprecision(6) << density << ","
         << fixed << setprecision(6) << lambda << "\n";
     
     out.close();
 }
 
 /**
  * Main function: Orchestrates eigenvector centrality computation
  * 
  * @param argc Number of command-line arguments
  * @param argv Array of command-line arguments
  * @return 0 on success, 1 on error
  * 
  * Usage: ./program <input_file> <output_dir> [dataset_name]
  * 
  * Process:
  * 1. Parse command-line arguments
  * 2. Read undirected graph from input file
  * 3. Compute eigenvector centrality using power iteration
  * 4. Calculate graph statistics
  * 5. Write results to detailed text file and CSV summary
  */
 int main(int argc, char* argv[]) {
     // Validate command-line arguments
     if (argc < 3) {
         cerr << "Usage: " << argv[0] << " <input_file> <output_dir> [dataset_name]\n";
         return 1;
     }
     
     // Parse arguments
     string inputFile = argv[1];
     string outputDir = argv[2];
     string datasetName = (argc >= 4) ? argv[3] : inputFile;
     
     // Create output directory if needed
     system(("mkdir -p " + outputDir).c_str());
     
     // Open input file
     ifstream inFile(inputFile);
     if (!inFile) {
         cerr << "Error: Cannot open input file " << inputFile << "\n";
         return 1;
     }
     
     // Skip comment lines starting with #
     string line;
     while (getline(inFile, line)) {
         if (line.empty() || line[0] == '#') continue;
         break;
     }
     
     // Parse first data line: n (vertices) and m (edges)
     istringstream iss(line);
     int n, m;
     iss >> n >> m;
     
     cout << "Dataset: " << datasetName << "\n";
     cout << "Vertices: " << n << ", Edges: " << m << "\n";
     
     // Start timing graph loading
     auto readStart = high_resolution_clock::now();
     EigenvectorCentrality eigen(n);
     
     int edgeCount = 0;
     set<pair<int,int>> uniqueEdges;  // Track unique edges to avoid duplicates
     
     // Read edges from input file
     int u, v;
     while (inFile >> u >> v) {
         // Skip invalid edges
         if (u == v) continue;                          // Ignore self-loops
         if (u < 1 || u > n || v < 1 || v > n) continue;  // Ignore out-of-range
         
         // Ensure we don't double-count edges (store in canonical form)
         int minV = min(u, v);
         int maxV = max(u, v);
         if (uniqueEdges.find({minV, maxV}) == uniqueEdges.end()) {
             uniqueEdges.insert({minV, maxV});
             eigen.addEdge(u - 1, v - 1);  // Convert to 0-indexed
             edgeCount++;
         }
     }
     inFile.close();
     
     // Calculate and display graph loading time
     auto readEnd = high_resolution_clock::now();
     double readTime = duration_cast<milliseconds>(readEnd - readStart).count() / 1000.0;
     
     cout << "Graph loaded in " << fixed << setprecision(3) << readTime << " seconds\n";
     cout << "Unique edges: " << edgeCount << "\n";
     
     // Compute eigenvector centrality using power iteration
     cout << "Computing eigenvector centrality...\n";
     auto computeStart = high_resolution_clock::now();
     vector<double> eigenVec = eigen.computeEigenvector();
     auto computeEnd = high_resolution_clock::now();
     
     // Calculate computation time and memory usage
     double computeTime = duration_cast<milliseconds>(computeEnd - computeStart).count() / 1000.0;
     long long memoryUsage = eigen.getMemoryUsage();
     
     cout << "Computation complete in " << fixed << setprecision(6) << computeTime << " seconds\n";
     
     // Get results
     double maxEigen = eigen.getMaxEigen();
     double lambda = eigen.getLambda();
     
     cout << "Maximum eigenvector centrality: " << fixed << setprecision(6) << maxEigen << "\n";
     cout << "Largest eigenvalue: " << fixed << setprecision(6) << lambda << "\n";
     cout << "Memory usage: " << fixed << setprecision(2) << (memoryUsage / 1048576.0) << " MB\n";
     
     // Calculate graph metrics
     double avgDegree = (2.0 * edgeCount) / n;  // Each edge contributes to two vertices
     double density = (2.0 * edgeCount) / (n * (n - 1.0));  // Ratio of actual to possible edges
     
     // Construct output file paths
     string detailedOutput = outputDir + "/" + datasetName + "_detailed.txt";
     string csvOutput = outputDir + "/summary.csv";
     
     // Write results
     writeDetailedResults(detailedOutput, datasetName, n, edgeCount, maxEigen,
                         computeTime, memoryUsage, lambda, eigenVec);
     writeCSVSummary(csvOutput, datasetName, n, edgeCount, maxEigen,
                    computeTime, memoryUsage, avgDegree, density, lambda);
     
     // Display output file locations
     cout << "\nResults written to:\n";
     cout << "  - " << detailedOutput << "\n";
     cout << "  - " << csvOutput << "\n";
     
     return 0;
 }