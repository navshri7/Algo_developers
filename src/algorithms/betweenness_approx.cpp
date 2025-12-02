/**
 * Approximate Betweenness Centrality Algorithm Implementation
 * 
 * This program computes an approximation of betweenness centrality for all vertices
 * in an undirected graph using a sampling-based approach. Instead of computing shortest
 * paths from all vertices (which is expensive for large graphs), it samples a subset
 * of source vertices and scales the results appropriately.
 * 
 * The approximation provides probabilistic guarantees on the accuracy of the results
 * while significantly reducing computation time for large graphs.
 * 
 * Date: December 2, 2025
 * 
 * Time Complexity: O(k * m) where k = number of samples, m = edges
 * Space Complexity: O(n + m) where n = vertices
 * 
 * The number of samples k is typically much smaller than n, providing speedup
 * proportional to k/n compared to exact betweenness centrality.
 * 
 * Input Format: 
 *   - First line: n (vertices) m (edges)
 *   - Following lines: u v (edge between vertices u and v)
 *   - Vertex IDs should be 1-indexed
 * 
 * Output:
 *   - Detailed text file with statistics and top vertices by approximate betweenness
 *   - CSV summary file with performance metrics
 * 
 * Reference: Brandes, U., & Pich, C. (2007). "Centrality estimation in large networks"
 */

 #include <iostream>
 #include <fstream>
 #include <vector>
 #include <queue>
 #include <stack>
 #include <algorithm>
 #include <map>
 #include <chrono>
 #include <iomanip>
 #include <sstream>
 #include <set>
 #include <cstdlib>
 #include <cmath>
 
 using namespace std;
 using namespace std::chrono;
 
 /**
  * ApproximateBetweenness Class
  * 
  * Implements sampling-based approximation of betweenness centrality.
  * 
  * Instead of computing betweenness by considering all n vertices as sources,
  * this algorithm:
  * 1. Randomly samples k vertices (where k << n for large graphs)
  * 2. Computes exact betweenness contributions from only these k sources
  * 3. Scales the results by n/k to estimate the full betweenness values
  * 
  * The number of samples k is chosen based on desired accuracy (epsilon) and
  * confidence level using the formula:
  * k = (0.5 / epsilon^2) * log(n / delta)
  * where delta is the failure probability (1 - confidence)
  * 
  * This provides probabilistic guarantees that the approximation error is bounded
  * by epsilon with probability at least (1 - delta).
  */
 class ApproximateBetweenness {
 private:
     int n;                          // Number of vertices in the graph
     vector<vector<int>> adj;        // Adjacency list representation of the graph
     vector<double> betweenness;     // Approximate betweenness centrality for each vertex
     long long memoryUsed;           // Estimated memory usage in bytes
     int numSamples;                 // Number of sampled vertices to use as sources
     
 public:
     /**
      * Constructor: Initialize the ApproximateBetweenness object
      * 
      * @param vertices Number of vertices in the graph
      * @param samples Number of samples to use (default: -1 for automatic calculation)
      * 
      * If samples < 0, automatically calculates the number of samples needed
      * based on theoretical accuracy requirements:
      * - epsilon = 0.1 (10% error bound)
      * - confidence = 0.9 (90% probability that error is within epsilon)
      * 
      * The formula k = (0.5 / eps^2) * log(n / delta) ensures that with
      * high probability, the approximation error is small.
      * 
      * Additional constraints:
      * - At least n/10 samples (minimum 10% of vertices)
      * - At most n samples (cannot sample more than total vertices)
      */
     ApproximateBetweenness(int vertices, int samples = -1) 
         : n(vertices), adj(vertices), betweenness(vertices, 0.0), memoryUsed(0) {
         // Estimate initial memory usage
         memoryUsed = vertices * (sizeof(vector<int>) + sizeof(double));
         
         if (samples < 0) {
             // Calculate samples based on theoretical accuracy requirements
             double eps = 0.1;        // Target approximation error (10%)
             double conf = 0.1;       // Failure probability (10%, so 90% confidence)
             
             // Formula from sampling theory for approximation guarantees
             numSamples = (int)ceil((0.5 / (eps * eps)) * log(vertices / conf));
             
             // Ensure numSamples is within reasonable bounds
             numSamples = min(numSamples, vertices);     // Cannot sample more than n vertices
             numSamples = max(numSamples, vertices / 10); // Use at least 10% of vertices
         } else {
             // Use user-specified number of samples (capped at total vertices)
             numSamples = min(samples, vertices);
         }
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
         // Ignore self-loops as they don't affect betweenness centrality
         if (u == v) return;
         
         // Add edge in both directions (undirected graph)
         adj[u].push_back(v);
         adj[v].push_back(u);
         
         // Update memory usage for two integers (bidirectional edge)
         memoryUsed += 2 * sizeof(int);
     }
     
     /**
      * Compute approximate betweenness centrality for all vertices
      * 
      * @return Vector containing approximate betweenness centrality for each vertex
      * 
      * Algorithm Overview:
      * 1. SAMPLING PHASE:
      *    - Randomly select k vertices from the graph (without replacement)
      *    - Use fixed seed (42) for reproducibility
      * 
      * 2. COMPUTATION PHASE (for each sampled source):
      *    - Perform BFS to find shortest paths (same as exact algorithm)
      *    - Count number of shortest paths to each vertex
      *    - Accumulate dependencies by backtracking
      *    - Scale contributions by n/k to estimate full betweenness
      * 
      * 3. SCALING:
      *    - Each sampled source contributes (n/k) times its normal contribution
      *    - This unbiased estimator ensures expected value equals true betweenness
      *    - Variance decreases as O(1/k), providing concentration guarantees
      * 
      * The scaling factor n/k accounts for the fact that we're only sampling
      * k sources instead of using all n sources. This makes the estimate unbiased:
      * E[approximate BC] = exact BC
      * 
      * Time Complexity: O(k * m) where k = numSamples, m = edges
      *   - Compare to O(n * m) for exact algorithm
      *   - Speedup factor: approximately k/n
      * 
      * Space Complexity: O(n + m) same as exact algorithm
      */
     vector<double> computeApproximateBetweenness() {
         // PHASE 1: Select random sample of vertices
         
         // Create list of all vertex indices
         vector<int> allNodes;
         for (int i = 0; i < n; i++) {
             allNodes.push_back(i);
         }
         
         // Set fixed random seed for reproducibility
         srand(42);
         
         // Sample without replacement using shuffle-and-take approach
         vector<int> sampledNodes;
         vector<int> available = allNodes;
         for (int i = 0; i < numSamples; i++) {
             // Pick random index from remaining vertices
             int idx = rand() % available.size();
             sampledNodes.push_back(available[idx]);
             // Remove selected vertex to ensure no duplicates
             available.erase(available.begin() + idx);
         }
         
         // Calculate scaling factor to extrapolate from sample to full graph
         // Since we're using k samples instead of n sources, multiply by n/k
         double scalingFactor = (double)n / (double)numSamples;
         
         // PHASE 2: Compute betweenness contributions from sampled sources
         
         // Process each sampled node as a source (same as exact algorithm)
         for (int source : sampledNodes) {
             // Stack to store vertices in order of non-increasing distance from source
             stack<int> traversal_stack;
             
             // Distance from source to each vertex (-1 means not reached yet)
             vector<int> distance(n, -1);
             
             // Number of shortest paths from source to each vertex
             vector<double> path_count(n, 0.0);
             
             // List of predecessors for each vertex on shortest paths from source
             vector<vector<int>> predecessors(n);
             
             // Queue for BFS traversal
             queue<int> bfs_queue;
             
             // Initialize BFS from source
             path_count[source] = 1.0;  // One path to source (the empty path)
             distance[source] = 0;       // Distance to itself is 0
             bfs_queue.push(source);
             
             // FORWARD PHASE: BFS to find shortest paths and count them
             while (!bfs_queue.empty()) {
                 int current = bfs_queue.front();
                 bfs_queue.pop();
                 
                 // Store vertex in stack for later processing in reverse order
                 traversal_stack.push(current);
                 
                 // Explore all neighbors of current vertex
                 for (int neighbor : adj[current]) {
                     // First time reaching this neighbor - set its distance
                     if (distance[neighbor] < 0) {
                         bfs_queue.push(neighbor);
                         distance[neighbor] = distance[current] + 1;
                     }
                     
                     // If neighbor is on a shortest path through current
                     if (distance[neighbor] == distance[current] + 1) {
                         // Add current's shortest paths to neighbor's count
                         path_count[neighbor] += path_count[current];
                         
                         // Current is a predecessor of neighbor on shortest paths
                         predecessors[neighbor].push_back(current);
                     }
                 }
             }
             
             // BACKWARD PHASE: Accumulate dependencies with scaling
             vector<double> dependency(n, 0.0);
             
             while (!traversal_stack.empty()) {
                 int node = traversal_stack.top();
                 traversal_stack.pop();
                 
                 // For each predecessor of this node on shortest paths from source
                 for (int pred : predecessors[node]) {
                     // Standard dependency accumulation formula
                     dependency[pred] += (path_count[pred] / path_count[node]) * (1.0 + dependency[node]);
                 }
                 
                 // Add scaled contribution to betweenness
                 // Scaling by n/k accounts for using only k samples instead of n sources
                 if (node != source) {
                     // Divide by 2 for undirected graphs (count each path once)
                     // Multiply by scalingFactor to extrapolate from sample
                     betweenness[node] += (dependency[node] / 2.0) * scalingFactor;
                 }
             }
         }
         
         return betweenness;
     }
     
     /**
      * Get the maximum approximate betweenness centrality value
      * 
      * @return Maximum betweenness centrality across all vertices
      * 
      * Note: This is an approximation of the true maximum betweenness.
      * The vertex with maximum approximate betweenness is likely (but not
      * guaranteed) to be among the vertices with highest true betweenness.
      */
     double getMaxBetweenness() {
         return *max_element(betweenness.begin(), betweenness.end());
     }
     
     /**
      * Get the number of samples used in the approximation
      * 
      * @return Number of sampled vertices used as sources
      * 
      * Useful for understanding the trade-off between accuracy and speed.
      * Larger k provides better approximation but takes more time.
      */
     int getNumSamples() {
         return numSamples;
     }
     
     /**
      * Get estimated memory usage of the algorithm
      * 
      * @return Estimated memory usage in bytes
      * 
      * Memory usage is similar to exact algorithm since the same
      * data structures are used, just with fewer iterations.
      */
     long long getMemoryUsage() {
         return memoryUsed;
     }
     
     /**
      * Get the complete approximate betweenness centrality vector
      * 
      * @return Vector of approximate betweenness values for all vertices
      * 
      * Useful for further analysis or comparison with exact values.
      */
     vector<double> getBetweenness() {
         return betweenness;
     }
 };
 
 void writeDetailedResults(const string& outputFile, const string& datasetName,
                          int n, int m, double maxBC, double runtime, 
                          long long memory, int numSamples, const vector<double>& betweenness) {
     ofstream out(outputFile);
     
     out << "Dataset: " << datasetName << " (APPROXIMATE)\n";
     out << "Vertices: " << n << "\n";
     out << "Edges: " << m << "\n";
     out << "Samples Used: " << numSamples << " (" << fixed << setprecision(2) 
         << (100.0 * numSamples / n) << "%)\n";
     out << "Max Betweenness: " << fixed << setprecision(6) << maxBC << "\n";
     out << "Runtime (seconds): " << fixed << setprecision(6) << runtime << "\n";
     out << "Memory Usage (MB): " << fixed << setprecision(2) << (memory / 1048576.0) << "\n";
     
     out << "\n=== Top 100 Vertices by Betweenness Centrality ===\n";
     out << "Rank\tVertex_ID\tBetweenness\n";
     
     vector<pair<double, int>> ranked;
     for (int i = 0; i < n; i++) {
         ranked.push_back({betweenness[i], i});
     }
     sort(ranked.begin(), ranked.end(), [](auto& a, auto& b) {
         if (a.first != b.first) return a.first > b.first;
         return a.second < b.second;
     });
     
     for (int i = 0; i < min(100, (int)ranked.size()); i++) {
         out << (i+1) << "\t" << (ranked[i].second + 1) << "\t" 
             << fixed << setprecision(6) << ranked[i].first << "\n";
     }
     
     out.close();
 }
 
 void writeCSVSummary(const string& csvFile, const string& datasetName,
                     int n, int m, double maxBC, double runtime, long long memory,
                     double avgDegree, double density, int numSamples) {
     bool fileExists = ifstream(csvFile).good();
     ofstream out(csvFile, ios::app);
     
     if (!fileExists) {
         out << "Dataset,Vertices,Edges,MaxBC,Runtime_sec,Memory_MB,AvgDegree,Density,Samples\n";
     }
     
     out << datasetName << "," << n << "," << m << "," 
         << fixed << setprecision(6) << maxBC << ","
         << fixed << setprecision(6) << runtime << ","
         << fixed << setprecision(2) << (memory / 1048576.0) << ","
         << fixed << setprecision(4) << avgDegree << ","
         << scientific << setprecision(6) << density << ","
         << numSamples << "\n";
     
     out.close();
 }
 
 int main(int argc, char* argv[]) {
     if (argc < 3) {
         cerr << "Usage: " << argv[0] << " <input_file> <output_dir> [dataset_name]\n";
         return 1;
     }
     
     string inputFile = argv[1];
     string outputDir = argv[2];
     string datasetName = (argc >= 4) ? argv[3] : inputFile;
     
     system(("mkdir -p " + outputDir).c_str());
     
     ifstream inFile(inputFile);
     if (!inFile) {
         cerr << "Error: Cannot open input file " << inputFile << "\n";
         return 1;
     }
     
     string line;
     while (getline(inFile, line)) {
         if (line.empty() || line[0] == '#') continue;
         break;
     }
     
     istringstream iss(line);
     int n, m;
     iss >> n >> m;
     
     cout << "Dataset: " << datasetName << " (APPROXIMATE)\n";
     cout << "Vertices: " << n << ", Edges: " << m << "\n";
     
     auto readStart = high_resolution_clock::now();
     ApproximateBetweenness abc(n);
     
     int edgeCount = 0;
     set<pair<int,int>> uniqueEdges;
     
     int u, v;
     while (inFile >> u >> v) {
         if (u == v) continue;
         if (u < 1 || u > n || v < 1 || v > n) continue;
         
         int minV = min(u, v);
         int maxV = max(u, v);
         if (uniqueEdges.find({minV, maxV}) == uniqueEdges.end()) {
             uniqueEdges.insert({minV, maxV});
             abc.addEdge(u - 1, v - 1);
             edgeCount++;
         }
     }
     inFile.close();
     
     auto readEnd = high_resolution_clock::now();
     double readTime = duration_cast<milliseconds>(readEnd - readStart).count() / 1000.0;
     
     cout << "Graph loaded in " << fixed << setprecision(3) << readTime << " seconds\n";
     cout << "Unique edges: " << edgeCount << "\n";
     
     int numSamples = abc.getNumSamples();
     cout << "Using " << numSamples << " samples (" << fixed << setprecision(2) 
          << (100.0 * numSamples / n) << "% of vertices)\n";
     
     cout << "Computing approximate betweenness centrality...\n";
     auto computeStart = high_resolution_clock::now();
     vector<double> betweenness = abc.computeApproximateBetweenness();
     auto computeEnd = high_resolution_clock::now();
     
     double computeTime = duration_cast<milliseconds>(computeEnd - computeStart).count() / 1000.0;
     long long memoryUsage = abc.getMemoryUsage();
     
     cout << "Computation complete in " << fixed << setprecision(6) << computeTime << " seconds\n";
     
     double maxBC = abc.getMaxBetweenness();
     cout << "Maximum betweenness: " << fixed << setprecision(6) << maxBC << "\n";
     cout << "Memory usage: " << fixed << setprecision(2) << (memoryUsage / 1048576.0) << " MB\n";
     
     double avgDegree = (2.0 * edgeCount) / n;
     double density = (2.0 * edgeCount) / (n * (n - 1.0));
     
     string detailedOutput = outputDir + "/" + datasetName + "_approx_detailed.txt";
     string csvOutput = outputDir + "/summary_approx.csv";
     
     writeDetailedResults(detailedOutput, datasetName, n, edgeCount, maxBC,
                         computeTime, memoryUsage, numSamples, betweenness);
     writeCSVSummary(csvOutput, datasetName, n, edgeCount, maxBC,
                    computeTime, memoryUsage, avgDegree, density, numSamples);
     
     cout << "\nResults written to:\n";
     cout << "  - " << detailedOutput << "\n";
     cout << "  - " << csvOutput << "\n";
     
     return 0;
 }