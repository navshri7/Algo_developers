/**
 * K-Core Decomposition Algorithm Implementation
 * 
 * This program computes the k-core decomposition of a graph using an efficient
 * O(n + m) algorithm based on vertex ordering by degree. The k-core of a graph
 * is the maximal subgraph where each vertex has at least k neighbors within the subgraph.
 * 
 * Date: December 2, 2025
 * 
 * Input Format: 
 *   - First line: n (vertices) m (edges)
 *   - Following lines: u v (edge between vertices u and v)
 *   - Vertex IDs should be 1-indexed
 * 
 * Output:
 *   - Detailed text file with statistics and top vertices
 *   - CSV summary file with performance metrics
 *   - CSV file mapping each node to its core number
 */

 #include <iostream>
 #include <fstream>
 #include <vector>
 #include <queue>
 #include <algorithm>
 #include <map>
 #include <chrono>
 #include <iomanip>
 #include <sstream>
 #include <set>
 
 using namespace std;
 using namespace std::chrono;
 
 /**
  * KCore Class
  * 
  * Implements the k-core decomposition algorithm for undirected graphs.
  * Uses the efficient O(n + m) algorithm by Batagelj and Zaversnik (2003).
  * 
  * The algorithm works by:
  * 1. Computing vertex degrees
  * 2. Ordering vertices by degree using bin-sort
  * 3. Iteratively removing vertices with minimum degree
  * 4. Updating neighbor degrees accordingly
  */
 class KCore {
 private:
     int n;                          // Number of vertices in the graph
     vector<vector<int>> adj;        // Adjacency list representation of the graph
     vector<int> coreness;           // Coreness value for each vertex
     long long memoryUsed;           // Estimated memory usage in bytes
     
 public:
     /**
      * Constructor: Initialize the KCore object
      * 
      * @param vertices Number of vertices in the graph
      * 
      * Initializes data structures and estimates initial memory usage
      * based on the number of vertices.
      */
     KCore(int vertices) : n(vertices), adj(vertices), coreness(vertices, 0), memoryUsed(0) {
         // Estimate memory usage for adjacency list and coreness array
         memoryUsed = vertices * (sizeof(vector<int>) + sizeof(int));
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
         // Ignore self-loops
         if (u == v) return;
         
         // Add edge in both directions (undirected graph)
         adj[u].push_back(v);
         adj[v].push_back(u);
         
         // Update memory usage for two integers (bidirectional edge)
         memoryUsed += 2 * sizeof(int);
     }
     
     /**
      * Compute k-core decomposition of the graph
      * 
      * @return Vector containing the coreness value for each vertex
      * 
      * Implements the efficient O(n + m) k-core decomposition algorithm:
      * 
      * Algorithm Overview:
      * 1. Initialize degree array for all vertices
      * 2. Use bin-sort to organize vertices by degree
      * 3. Process vertices in non-decreasing degree order
      * 4. For each vertex v being removed:
      *    - For each neighbor u with higher degree:
      *      - Decrease u's degree
      *      - Move u to appropriate bin
      * 5. The degree when a vertex is removed becomes its coreness
      * 
      * Time Complexity: O(n + m) where n = vertices, m = edges
      * Space Complexity: O(n + maxDegree)
      */
     vector<int> computeKCore() {
         auto start = high_resolution_clock::now();
         
         // degree[i] = current degree of vertex i
         vector<int> degree(n);
         
         // pos[i] = position of vertex i in the vert array
         vector<int> pos(n);
         
         // vert[i] = vertex at position i (ordered by degree)
         vector<int> vert(n);
         
         // Update memory usage estimate
         memoryUsed += 3 * n * sizeof(int);
         
         // Step 1: Compute initial degrees and find maximum degree
         int maxDegree = 0;
         for (int i = 0; i < n; i++) {
             degree[i] = adj[i].size();
             if (degree[i] > maxDegree) {
                 maxDegree = degree[i];
             }
         }
         
         // Handle empty graph case
         if (maxDegree == 0) {
             return coreness;
         }
         
         // Step 2: Bin-sort initialization
         // bin[d] = starting position of vertices with degree d
         vector<int> bin(maxDegree + 1, 0);
         memoryUsed += (maxDegree + 1) * sizeof(int);
         
         // Count vertices with each degree
         for (int i = 0; i < n; i++) {
             bin[degree[i]]++;
         }
         
         // Convert counts to starting positions
         // After this loop, bin[d] contains the starting index for degree d vertices
         int start_pos = 0;
         for (int d = 0; d <= maxDegree; d++) {
             int num = bin[d];
             bin[d] = start_pos;
             start_pos += num;
         }
         
         // Step 3: Place vertices into bins based on their degree
         for (int i = 0; i < n; i++) {
             pos[i] = bin[degree[i]];          // Position of vertex i
             vert[pos[i]] = i;                 // Vertex at this position
             bin[degree[i]]++;                 // Move to next position in bin
         }
         
         // Step 4: Restore bin array to contain starting positions
         // (it was incremented in the previous loop)
         for (int d = maxDegree; d > 0; d--) {
             bin[d] = bin[d - 1];
         }
         bin[0] = 0;
         
         // Step 5: Process vertices in non-decreasing degree order
         // This is the main k-core computation loop
         for (int i = 0; i < n; i++) {
             int v = vert[i];  // Get vertex with minimum current degree
             
             // Process all neighbors of v
             for (int u : adj[v]) {
                 // Only process neighbors with higher degree
                 // (neighbors with lower degree have already been processed)
                 if (degree[u] > degree[v]) {
                     int du = degree[u];           // Current degree of u
                     int pu = pos[u];              // Current position of u
                     int pw = bin[du];             // First position of vertices with degree du
                     int w = vert[pw];             // Vertex at that position
                     
                     // Swap u with the first vertex in its degree bin
                     // This maintains the invariant that vertices are ordered by degree
                     if (u != w) {
                         pos[u] = pw;              // u moves to position pw
                         vert[pu] = w;             // w moves to position pu
                         pos[w] = pu;              // Update w's position
                         vert[pw] = u;             // Update position pw to contain u
                     }
                     
                     // Move bin start pointer forward (u no longer has degree du)
                     bin[du]++;
                     
                     // Decrease u's degree (v is being removed from the graph)
                     degree[u]--;
                 }
             }
         }
         
         // Step 6: The final degree of each vertex is its coreness
         // (the degree at which it was removed from the graph)
         for (int i = 0; i < n; i++) {
             coreness[i] = degree[i];
         }
         
         return coreness;
     }
     
     /**
      * Get the maximum k-core value in the graph
      * 
      * @return Maximum coreness value across all vertices
      * 
      * The maximum k-core indicates the densest subgraph in terms of
      * minimum degree constraint.
      */
     int getMaxKCore() {
         return *max_element(coreness.begin(), coreness.end());
     }
     
     /**
      * Get all vertices that belong to the k-core
      * 
      * @param k The k value for which to find the k-core vertices
      * @return Vector of vertex IDs (0-indexed) that have coreness >= k
      * 
      * A vertex belongs to the k-core if its coreness value is at least k.
      * The k-core is the maximal subgraph where every vertex has degree >= k.
      */
     vector<int> getVerticesInKCore(int k) {
         vector<int> vertices;
         for (int i = 0; i < n; i++) {
             if (coreness[i] >= k) {
                 vertices.push_back(i);
             }
         }
         return vertices;
     }
     
     /**
      * Get estimated memory usage of the algorithm
      * 
      * @return Estimated memory usage in bytes
      * 
      * Provides an approximation of memory consumed by the data structures
      * used in the k-core computation.
      */
     long long getMemoryUsage() {
         return memoryUsed;
     }
     
     /**
      * Get the distribution of coreness values
      * 
      * @return Map from coreness value to count of vertices with that coreness
      * 
      * Useful for understanding the structure of the graph and how vertices
      * are distributed across different k-core levels.
      */
     map<int, int> getCoreDistribution() {
         map<int, int> dist;
         for (int i = 0; i < n; i++) {
             dist[coreness[i]]++;
         }
         return dist;
     }
 };
 
 /**
  * Write detailed results to a text file
  * 
  * @param outputFile Path to the output file
  * @param datasetName Name of the dataset
  * @param n Number of vertices
  * @param m Number of edges
  * @param maxCore Maximum k-core value
  * @param dist Distribution of coreness values
  * @param runtime Computation time in seconds
  * @param memory Memory usage in bytes
  * @param coreness Vector of coreness values for each vertex
  * 
  * Generates a comprehensive text report including:
  * - Dataset statistics
  * - Performance metrics
  * - Core distribution table
  * - Top 100 vertices by coreness
  */
 void writeDetailedResults(const string& outputFile, const string& datasetName, 
                          int n, int m, int maxCore, const map<int, int>& dist,
                          double runtime, long long memory, const vector<int>& coreness) {
     ofstream out(outputFile);
     
     // Write header information
     out << "Dataset: " << datasetName << "\n";
     out << "Vertices: " << n << "\n";
     out << "Edges: " << m << "\n";
     out << "Max K-Core: " << maxCore << "\n";
     out << "Runtime (seconds): " << fixed << setprecision(6) << runtime << "\n";
     out << "Memory Usage (MB): " << fixed << setprecision(2) << (memory / 1048576.0) << "\n";
     
     // Write core distribution table
     out << "\n=== Core Distribution ===\n";
     out << "Core\tCount\tPercentage\n";
     
     for (auto& [core, count] : dist) {
         out << core << "\t" << count << "\t" 
             << fixed << setprecision(2) << (100.0 * count / n) << "%\n";
     }
     
     // Write top vertices by coreness
     out << "\n=== Top 100 Vertices by Coreness ===\n";
     out << "Rank\tVertex_ID\tCoreness\n";
     
     // Create vector of (coreness, vertex_id) pairs for sorting
     vector<pair<int, int>> ranked;
     for (int i = 0; i < n; i++) {
         ranked.push_back({coreness[i], i});
     }
     
     // Sort by coreness (descending), then by vertex ID (ascending)
     sort(ranked.begin(), ranked.end(), [](auto& a, auto& b) {
         if (a.first != b.first) return a.first > b.first;
         return a.second < b.second;
     });
     
     // Output top 100 vertices (convert to 1-indexed)
     for (int i = 0; i < min(100, (int)ranked.size()); i++) {
         out << (i+1) << "\t" << (ranked[i].second + 1) << "\t" << ranked[i].first << "\n";
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
  * @param maxCore Maximum k-core value
  * @param runtime Computation time in seconds
  * @param memory Memory usage in bytes
  * @param avgDegree Average degree of vertices
  * @param density Graph density
  * 
  * Appends a row to the CSV summary file with key metrics.
  * Creates the file with headers if it doesn't exist.
  * Useful for comparing multiple datasets.
  */
 void writeCSVSummary(const string& csvFile, const string& datasetName,
                     int n, int m, int maxCore, double runtime, long long memory,
                     double avgDegree, double density) {
     // Check if file exists to determine if we need to write headers
     bool fileExists = ifstream(csvFile).good();
     ofstream out(csvFile, ios::app);
     
     // Write header row if this is a new file
     if (!fileExists) {
         out << "Dataset,Vertices,Edges,MaxCore,Runtime_sec,Memory_MB,AvgDegree,Density\n";
     }
     
     // Write data row with appropriate formatting
     out << datasetName << "," << n << "," << m << "," << maxCore << ","
         << fixed << setprecision(6) << runtime << ","
         << fixed << setprecision(2) << (memory / 1048576.0) << ","
         << fixed << setprecision(4) << avgDegree << ","
         << scientific << setprecision(6) << density << "\n";
     
     out.close();
 }
 
 /**
  * Write node-to-coreness mapping to CSV file
  * 
  * @param csvFile Path to the output CSV file
  * @param datasetName Name of the dataset (for error messages)
  * @param coreness Vector of coreness values for each vertex
  * 
  * Creates a CSV file with two columns: Node (1-indexed) and CoreNumber.
  * This format is useful for importing into graph visualization tools
  * or further analysis in other software.
  */
 void writeNodeCSV(const string& csvFile, const string& datasetName,
                   const vector<int>& coreness) {
     ofstream out(csvFile);
     if (!out) {
         cerr << "Error: Cannot create CSV file " << csvFile << "\n";
         return;
     }
     
     // Write header
     out << "Node,CoreNumber\n";
     
     // Write each node with its core number (convert to 1-indexed)
     for (int i = 0; i < (int)coreness.size(); i++) {
         out << (i + 1) << "," << coreness[i] << "\n";
     }
     
     out.close();
 }
 
 /**
  * Main function: Orchestrates the k-core decomposition process
  * 
  * @param argc Number of command-line arguments
  * @param argv Array of command-line arguments
  * @return 0 on success, 1 on error
  * 
  * Usage: ./program <input_file> <output_dir> [dataset_name]
  * 
  * Process:
  * 1. Parse command-line arguments
  * 2. Read graph from input file
  * 3. Compute k-core decomposition
  * 4. Calculate graph statistics
  * 5. Write results to multiple output files
  */
 int main(int argc, char* argv[]) {
     // Validate command-line arguments
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
     
     // Skip comment lines starting with #
     string line;
     while (getline(inFile, line)) {
         if (line.empty() || line[0] == '#') continue;
         break;  // Found first non-comment line
     }
     
     // Parse first data line: n (vertices) and m (edges)
     istringstream iss(line);
     int n, m;
     iss >> n >> m;
     
     cout << "Dataset: " << datasetName << "\n";
     cout << "Vertices: " << n << ", Edges: " << m << "\n";
     
     // Start timing the graph reading process
     auto readStart = high_resolution_clock::now();
     KCore kcore(n);
     
     int edgeCount = 0;
     set<pair<int,int>> uniqueEdges;  // Track unique edges to avoid duplicates
     
     // Read edges from input file
     int u, v;
     while (inFile >> u >> v) {
         // Skip invalid edges
         if (u == v) continue;                          // Ignore self-loops
         if (u < 1 || u > n || v < 1 || v > n) continue;  // Ignore out-of-range vertices
         
         // Ensure we don't double-count edges
         // Store edges in canonical form (smaller vertex first)
         int minV = min(u, v);
         int maxV = max(u, v);
         if (uniqueEdges.find({minV, maxV}) == uniqueEdges.end()) {
             uniqueEdges.insert({minV, maxV});
             kcore.addEdge(u - 1, v - 1);  // Convert to 0-indexed
             edgeCount++;
         }
     }
     inFile.close();
     
     // Calculate and display graph loading time
     auto readEnd = high_resolution_clock::now();
     double readTime = duration_cast<milliseconds>(readEnd - readStart).count() / 1000.0;
     
     cout << "Graph loaded in " << fixed << setprecision(3) << readTime << " seconds\n";
     cout << "Unique edges: " << edgeCount << "\n";
     
     // Compute k-core decomposition
     cout << "Computing k-core decomposition...\n";
     auto computeStart = high_resolution_clock::now();
     vector<int> coreness = kcore.computeKCore();
     auto computeEnd = high_resolution_clock::now();
     
     // Calculate computation time and memory usage
     double computeTime = duration_cast<milliseconds>(computeEnd - computeStart).count() / 1000.0;
     long long memoryUsage = kcore.getMemoryUsage();
     
     cout << "Computation complete in " << fixed << setprecision(6) << computeTime << " seconds\n";
     
     // Get results
     int maxCore = kcore.getMaxKCore();
     map<int, int> dist = kcore.getCoreDistribution();
     
     cout << "Maximum k-core: " << maxCore << "\n";
     cout << "Memory usage: " << fixed << setprecision(2) << (memoryUsage / 1048576.0) << " MB\n";
     
     // Calculate graph metrics
     double avgDegree = (2.0 * edgeCount) / n;  // Each edge contributes to two vertices
     double density = (2.0 * edgeCount) / (n * (n - 1.0));  // Ratio of actual to possible edges
     
     // Construct output file paths
     string detailedOutput = outputDir + "/" + datasetName + "_detailed.txt";
     string csvOutput = outputDir + "/summary.csv";
     string nodeCSVOutput = outputDir + "/" + datasetName + ".csv";
     
     // Write all output files
     writeDetailedResults(detailedOutput, datasetName, n, edgeCount, maxCore, 
                         dist, computeTime, memoryUsage, coreness);
     writeCSVSummary(csvOutput, datasetName, n, edgeCount, maxCore, 
                    computeTime, memoryUsage, avgDegree, density);
     writeNodeCSV(nodeCSVOutput, datasetName, coreness);
     
     // Display output file locations
     cout << "\nResults written to:\n";
     cout << "  - " << detailedOutput << "\n";
     cout << "  - " << csvOutput << "\n";
     cout << "  - " << nodeCSVOutput << "\n";
     
     return 0;
 }