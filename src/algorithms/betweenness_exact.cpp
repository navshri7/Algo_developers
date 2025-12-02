/**
 * Betweenness Centrality Algorithm Implementation
 * 
 * This program computes the betweenness centrality for all vertices in an undirected graph
 * using Brandes' algorithm. Betweenness centrality measures the importance of a vertex
 * based on the number of shortest paths that pass through it.
 * 
 * The algorithm uses BFS from each vertex to compute shortest paths and then accumulates
 * dependencies in reverse order to calculate betweenness values efficiently.
 * 
 * 
 * Date: December 2, 2025
 * 
 * Time Complexity: O(n * m) for unweighted graphs where n = vertices, m = edges
 * Space Complexity: O(n + m)
 * 
 * Input Format: 
 *   - First line: n (vertices) m (edges)
 *   - Following lines: u v (edge between vertices u and v)
 *   - Vertex IDs should be 1-indexed
 * 
 * Output:
 *   - Detailed text file with statistics and top vertices by betweenness
 *   - CSV summary file with performance metrics
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
 
 using namespace std;
 using namespace std::chrono;
 
 /**
  * BetweennessCentrality Class
  * 
  * Implements Brandes' algorithm for computing betweenness centrality in undirected graphs.
  * 
  * Betweenness centrality of a vertex v is defined as:
  * BC(v) = sum over all pairs (s,t) of: (number of shortest s-t paths through v) / (total shortest s-t paths)
  * 
  * The algorithm works by:
  * 1. For each source vertex s:
  *    a. Perform BFS to find shortest paths from s to all other vertices
  *    b. Count the number of shortest paths to each vertex
  *    c. Accumulate dependencies by backtracking from furthest vertices
  * 2. Sum up contributions from all sources to get final betweenness values
  * 
  * Reference: Brandes, U. (2001). "A faster algorithm for betweenness centrality"
  */
 class BetweennessCentrality {
 private:
     int n;                          // Number of vertices in the graph
     vector<vector<int>> adj;        // Adjacency list representation of the graph
     vector<double> betweenness;     // Betweenness centrality value for each vertex
     long long memoryUsed;           // Estimated memory usage in bytes
     
 public:
     /**
      * Constructor: Initialize the BetweennessCentrality object
      * 
      * @param vertices Number of vertices in the graph
      * 
      * Initializes data structures for storing the graph and betweenness values.
      * All betweenness values start at 0.0.
      */
     BetweennessCentrality(int vertices) : n(vertices), adj(vertices), betweenness(vertices, 0.0), memoryUsed(0) {
         // Estimate initial memory usage for adjacency list and betweenness array
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
         // Ignore self-loops as they don't affect betweenness centrality
         if (u == v) return;
         
         // Add edge in both directions (undirected graph)
         adj[u].push_back(v);
         adj[v].push_back(u);
         
         // Update memory usage for two integers (bidirectional edge)
         memoryUsed += 2 * sizeof(int);
     }
     
     /**
      * Compute betweenness centrality for all vertices
      * 
      * @return Vector containing the betweenness centrality value for each vertex
      * 
      * Implements Brandes' algorithm for betweenness centrality computation:
      * 
      * Algorithm Overview:
      * For each source vertex s:
      *   1. FORWARD PHASE (BFS):
      *      - Find shortest paths from s to all other vertices
      *      - Count number of shortest paths (path_count)
      *      - Track predecessors on shortest paths
      *      - Store vertices in order of increasing distance (using stack)
      *   
      *   2. BACKWARD PHASE (Dependency Accumulation):
      *      - Process vertices in reverse order (decreasing distance from source)
      *      - For each vertex w, compute dependency of s on w
      *      - Propagate dependencies back to predecessors
      *      - Add to betweenness score
      * 
      * The dependency formula ensures that each vertex gets credit proportional
      * to the fraction of shortest paths that pass through it.
      * 
      * Time Complexity: O(n * m) where n = vertices, m = edges
      * Space Complexity: O(n + m) for storing distances, paths, and predecessors
      */
     vector<double> computeBetweenness() {
         auto start = high_resolution_clock::now();
         
         // Process each node as source vertex
         for (int source = 0; source < n; source++) {
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
             
             // BACKWARD PHASE: Accumulate dependencies by processing vertices
             // in reverse order (from furthest to closest)
             vector<double> dependency(n, 0.0);
             
             while (!traversal_stack.empty()) {
                 int node = traversal_stack.top();
                 traversal_stack.pop();
                 
                 // For each predecessor of this node on shortest paths from source
                 for (int pred : predecessors[node]) {
                     // Dependency formula: fraction of paths through pred times
                     // (1 + dependency of node)
                     // This propagates the importance back through the shortest path tree
                     dependency[pred] += (path_count[pred] / path_count[node]) * (1.0 + dependency[node]);
                 }
                 
                 // Add this node's dependency to its betweenness score
                 // Skip the source itself as it's not "between" anything in this iteration
                 // Divide by 2 because we're considering undirected edges
                 // (each shortest path is counted from both endpoints)
                 if (node != source) {
                     betweenness[node] += dependency[node] / 2.0;
                 }
             }
         }
         
         return betweenness;
     }
     
     /**
      * Get the maximum betweenness centrality value in the graph
      * 
      * @return Maximum betweenness centrality across all vertices
      * 
      * The vertex with maximum betweenness is the most "central" vertex
      * in terms of lying on shortest paths between other vertices.
      */
     double getMaxBetweenness() {
         return *max_element(betweenness.begin(), betweenness.end());
     }
     
     /**
      * Get the top k vertices by betweenness centrality
      * 
      * @param k Number of top vertices to return
      * @return Vector of (betweenness, vertex_id) pairs sorted by betweenness (descending)
      * 
      * Returns at most k vertices. If the graph has fewer than k vertices,
      * returns all vertices sorted by betweenness.
      */
     vector<pair<double, int>> getTopNodes(int k) {
         // Create vector of (betweenness, vertex_id) pairs
         vector<pair<double, int>> ranked;
         for (int i = 0; i < n; i++) {
             ranked.push_back({betweenness[i], i});
         }
         
         // Sort by betweenness (descending), then by vertex ID (ascending) for ties
         sort(ranked.begin(), ranked.end(), [](auto& a, auto& b) {
             if (a.first != b.first) return a.first > b.first;
             return a.second < b.second;
         });
         
         // Keep only top k vertices
         ranked.resize(min(k, (int)ranked.size()));
         return ranked;
     }
     
     /**
      * Get estimated memory usage of the algorithm
      * 
      * @return Estimated memory usage in bytes
      * 
      * Provides an approximation of memory consumed by the data structures
      * used in the betweenness centrality computation.
      */
     long long getMemoryUsage() {
         return memoryUsed;
     }
     
     /**
      * Get the complete betweenness centrality vector
      * 
      * @return Vector of betweenness values for all vertices
      * 
      * Useful for further analysis or custom processing of results.
      */
     vector<double> getBetweenness() {
         return betweenness;
     }
 };
 
 void writeDetailedResults(const string& outputFile, const string& datasetName,
                          int n, int m, double maxBC, double runtime, 
                          long long memory, const vector<double>& betweenness) {
     ofstream out(outputFile);
     
     out << "Dataset: " << datasetName << "\n";
     out << "Vertices: " << n << "\n";
     out << "Edges: " << m << "\n";
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
                     double avgDegree, double density) {
     bool fileExists = ifstream(csvFile).good();
     ofstream out(csvFile, ios::app);
     
     if (!fileExists) {
         out << "Dataset,Vertices,Edges,MaxBC,Runtime_sec,Memory_MB,AvgDegree,Density\n";
     }
     
     out << datasetName << "," << n << "," << m << "," 
         << fixed << setprecision(6) << maxBC << ","
         << fixed << setprecision(6) << runtime << ","
         << fixed << setprecision(2) << (memory / 1048576.0) << ","
         << fixed << setprecision(4) << avgDegree << ","
         << scientific << setprecision(6) << density << "\n";
     
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
     
     cout << "Dataset: " << datasetName << "\n";
     cout << "Vertices: " << n << ", Edges: " << m << "\n";
     
     auto readStart = high_resolution_clock::now();
     BetweennessCentrality bc(n);
     
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
             bc.addEdge(u - 1, v - 1);
             edgeCount++;
         }
     }
     inFile.close();
     
     auto readEnd = high_resolution_clock::now();
     double readTime = duration_cast<milliseconds>(readEnd - readStart).count() / 1000.0;
     
     cout << "Graph loaded in " << fixed << setprecision(3) << readTime << " seconds\n";
     cout << "Unique edges: " << edgeCount << "\n";
     
     cout << "Computing betweenness centrality...\n";
     auto computeStart = high_resolution_clock::now();
     vector<double> betweenness = bc.computeBetweenness();
     auto computeEnd = high_resolution_clock::now();
     
     double computeTime = duration_cast<milliseconds>(computeEnd - computeStart).count() / 1000.0;
     long long memoryUsage = bc.getMemoryUsage();
     
     cout << "Computation complete in " << fixed << setprecision(6) << computeTime << " seconds\n";
     
     double maxBC = bc.getMaxBetweenness();
     cout << "Maximum betweenness: " << fixed << setprecision(6) << maxBC << "\n";
     cout << "Memory usage: " << fixed << setprecision(2) << (memoryUsage / 1048576.0) << " MB\n";
     
     double avgDegree = (2.0 * edgeCount) / n;
     double density = (2.0 * edgeCount) / (n * (n - 1.0));
     
     string detailedOutput = outputDir + "/" + datasetName + "_detailed.txt";
     string csvOutput = outputDir + "/summary.csv";
     
     writeDetailedResults(detailedOutput, datasetName, n, edgeCount, maxBC,
                         computeTime, memoryUsage, betweenness);
     writeCSVSummary(csvOutput, datasetName, n, edgeCount, maxBC,
                    computeTime, memoryUsage, avgDegree, density);
     
     cout << "\nResults written to:\n";
     cout << "  - " << detailedOutput << "\n";
     cout << "  - " << csvOutput << "\n";
     
     return 0;
 }