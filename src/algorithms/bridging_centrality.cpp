/**
 * Bridging Centrality Algorithm Implementation for Directed Graphs
 * 
 * This program computes bridging centrality, a measure that identifies nodes that
 * serve as bridges between different parts of a network. Bridging centrality combines:
 * 1. Betweenness centrality - how often a node lies on shortest paths
 * 2. Bridging coefficient - tendency to connect low-degree nodes
 * 
 * Bridging centrality = Betweenness × Bridging Coefficient
 * 
 * The bridging coefficient is calculated as:
 * BC(v) = (1/degree(v)) × Σ(1/degree(u)) for all neighbors u
 * 
 * This metric is particularly useful for:
 * - Identifying information bottlenecks
 * - Finding nodes that connect disparate communities
 * - Detecting structural holes in networks
 * - Citation network analysis (papers bridging different research areas)
 * 
 * Date: December 2, 2025
 * 
 * Time Complexity: O(n × m) where n = nodes, m = edges (dominated by betweenness)
 * Space Complexity: O(n + m)
 * 
 * Input Format: 
 *   - Each line: cited citing (directed edge from citing to cited)
 *   - Example: "100 200" means paper 200 cites paper 100
 *   - Creates directed edge: 200 -> 100
 * 
 * Output:
 *   - CSV file with betweenness, bridging coefficient, and bridging centrality
 *   - Detailed text file with statistics and top nodes by various metrics
 * 
 * Reference: Hwang, W., et al. (2008). "Bridging centrality: Identifying bridging nodes
 *            in scale-free networks"
 */

 #include <bits/stdc++.h>
 #include <chrono>
 #include <sys/resource.h>
 using namespace std;
 
 typedef long long ll;
 
 /**
  * CentralityResult Structure
  * 
  * Stores bridging centrality components for a single node.
  * 
  * Components:
  * - betweenness: Standard betweenness centrality (normalized)
  * - bridging_coeff: Bridging coefficient measuring tendency to bridge low-degree nodes
  * - bridging_centrality: Final metric (betweenness × bridging_coeff)
  * 
  * Interpretation:
  * - High betweenness alone: Node on many shortest paths
  * - High bridging_coeff alone: Node connects sparsely connected neighbors
  * - High bridging_centrality: Node bridges different parts of the network effectively
  */
 struct CentralityResult {
     double betweenness = 0.0;           // Normalized betweenness centrality
     double bridging_coeff = 0.0;        // Bridging coefficient
     double bridging_centrality = 0.0;   // Combined metric
 };
 
 /**
  * MemoryTracker Structure
  * 
  * Tracks peak memory usage during program execution using system calls.
  * Uses getrusage() to query the operating system's resource usage statistics.
  * 
  * On Linux: ru_maxrss is in kilobytes
  * On macOS: ru_maxrss is in bytes (would need adjustment for macOS)
  */
 struct MemoryTracker {
     double peak_memory_mb = 0.0;  // Peak memory usage in megabytes
     
     /**
      * Update peak memory usage
      * 
      * Queries the OS for current resource usage and updates the peak memory
      * if current usage exceeds previously recorded peak.
      */
     void update() {
         struct rusage usage;
         getrusage(RUSAGE_SELF, &usage);
         // ru_maxrss is in kilobytes on Linux, convert to megabytes
         double current_mb = usage.ru_maxrss / 1024.0;
         peak_memory_mb = max(peak_memory_mb, current_mb);
     }
 };
 
 /**
  * Load directed graph from file
  * 
  * @param filepath Path to input file containing edge list
  * @param adj Adjacency list representation (output parameter)
  * 
  * Input format: "cited citing" creates directed edge citing -> cited
  * 
  * For directed graphs, we only store outgoing edges in adjacency list:
  * - adj[citing] contains cited (citing has outgoing edge to cited)
  * - This represents the direction of information/citation flow
  * 
  * We also ensure all cited nodes exist in the adjacency list (even if they
  * have no outgoing edges) to include all nodes in centrality calculations.
  * 
  * Time Complexity: O(m) where m = number of edges
  * Space Complexity: O(n + m) where n = number of nodes
  */
 void loadGraph(const string &filepath, unordered_map<ll, vector<ll>> &adj) {
     ifstream fin(filepath);
     if (!fin.is_open()) {
         cerr << "Error: Cannot open file: " << filepath << endl;
         exit(1);
     }
     
     ll cited, citing;
     while (fin >> cited >> citing) {
         // Add directed edge: citing -> cited
         adj[citing].push_back(cited);
         
         // Ensure cited node exists in map (even if it has no outgoing edges)
         // This is important for nodes that are only targets, not sources
         if (!adj.count(cited)) adj[cited] = {};
     }
     
     fin.close();
 }
 
 /**
  * Compute betweenness centrality for all nodes using Brandes' algorithm
  * 
  * @param adj Adjacency list of the directed graph
  * @param results Map to store computed centrality values (output parameter)
  * 
  * Betweenness centrality measures how often a node lies on shortest paths
  * between other pairs of nodes. It's calculated as:
  * 
  * BC(v) = Σ(σ(s,t|v) / σ(s,t)) for all pairs s,t
  * 
  * where:
  * - σ(s,t) = number of shortest paths from s to t
  * - σ(s,t|v) = number of those paths passing through v
  * 
  * Algorithm (Brandes' algorithm):
  * For each source node s:
  *   1. BFS to find shortest paths from s to all other nodes
  *   2. Track predecessor lists and path counts
  *   3. Backtrack to accumulate dependencies
  * 
  * NORMALIZATION:
  * Raw betweenness values are normalized by dividing by (n-1)(n-2) where n
  * is the number of nodes. This scales values to [0,1] range and makes them
  * comparable across graphs of different sizes.
  * 
  * For directed graphs: normalizer = (n-1)(n-2)
  * For undirected graphs: normalizer = (n-1)(n-2)/2
  * 
  * Time Complexity: O(n × m) where n = nodes, m = edges
  * Space Complexity: O(n²) worst case for storing paths
  */
 void computeBetweenness(const unordered_map<ll, vector<ll>> &adj,
                         unordered_map<ll, CentralityResult> &results) {
     // Collect all node IDs
     vector<ll> nodes;
     for (auto &p : adj) nodes.push_back(p.first);
     
     // Process each node as source for shortest paths
     for (ll s : nodes) {
         // S: stack to store vertices in order of non-increasing distance from s
         stack<ll> S;
         
         // P[w]: list of predecessors of w on shortest paths from s
         unordered_map<ll, vector<ll>> P;
         
         // sigma[w]: number of shortest paths from s to w
         unordered_map<ll, double> sigma;
         
         // dist[w]: distance from s to w (-1 means unvisited)
         unordered_map<ll, int> dist;
         
         // Q: queue for BFS traversal
         queue<ll> Q;
         
         // Initialize data structures for all nodes
         for (ll v : nodes) {
             P[v] = {};
             sigma[v] = 0;
             dist[v] = -1;
         }
         
         // Initialize source node
         sigma[s] = 1;   // One path to itself (empty path)
         dist[s] = 0;    // Distance to itself is 0
         Q.push(s);
         
         // FORWARD PHASE: BFS to find shortest paths
         while (!Q.empty()) {
             ll v = Q.front(); Q.pop();
             S.push(v);  // Store for backward phase
             
             // Explore all outgoing edges from v
             for (ll w : adj.at(v)) {
                 // First time reaching w - set its distance
                 if (dist[w] < 0) {
                     Q.push(w);
                     dist[w] = dist[v] + 1;
                 }
                 
                 // If w is on a shortest path through v
                 if (dist[w] == dist[v] + 1) {
                     sigma[w] += sigma[v];  // Add v's paths to w's count
                     P[w].push_back(v);     // v is a predecessor of w
                 }
             }
         }
         
         // BACKWARD PHASE: Accumulate dependencies
         // delta[v]: dependency of source s on v
         unordered_map<ll, double> delta;
         for (ll v : nodes) delta[v] = 0;
         
         // Process nodes in reverse order (from farthest to closest)
         while (!S.empty()) {
             ll w = S.top(); S.pop();
             
             // For each predecessor v of w on shortest paths from s
             for (ll v : P[w]) {
                 // Propagate dependency back through the shortest path tree
                 // Formula: delta[v] += (sigma[v] / sigma[w]) * (1 + delta[w])
                 delta[v] += (sigma[v] / sigma[w]) * (1 + delta[w]);
             }
             
             // Add to betweenness (skip source itself)
             if (w != s) results[w].betweenness += delta[w];
         }
     }
     
     // NORMALIZATION: Scale betweenness to [0,1] range
     // For directed graphs: divide by (n-1)(n-2)
     // This accounts for all possible ordered pairs of nodes
     int n = nodes.size();
     if (n > 2) {
         double normalizer = (n - 1) * (n - 2);
         for (auto &p : results) {
             p.second.betweenness /= normalizer;
         }
     }
 }
 
 /**
  * Compute bridging coefficient for all nodes
  * 
  * @param adj Adjacency list of the directed graph
  * @param results Map to store computed bridging coefficients (output parameter)
  * 
  * The bridging coefficient measures a node's tendency to bridge between
  * sparsely connected parts of the network. It's calculated as:
  * 
  * BC(v) = (1/degree(v)) × Σ(1/degree(u)) for all neighbors u of v
  * 
  * Intuition:
  * - Nodes connecting to low-degree neighbors get higher coefficients
  * - This identifies nodes that bridge otherwise disconnected communities
  * - Low-degree neighbors suggest they're not central in their own communities
  * 
  * FORMULA INTERPRETATION:
  * - (1/degree(v)): Normalizes by node's own degree
  * - Σ(1/degree(u)): Sum of inverse degrees of neighbors
  * - Product emphasizes nodes with both:
  *   1. Few connections themselves (low degree)
  *   2. Connections to sparsely connected nodes (low neighbor degrees)
  * 
  * IMPORTANT FIX:
  * The formula multiplies (1/degree(v)) by the sum of (1/degree(neighbors)).
  * Earlier versions incorrectly divided instead of multiplied, which inverted
  * the intended behavior.
  * 
  * Time Complexity: O(n + m) where n = nodes, m = edges
  * Space Complexity: O(n) for degree map
  */
 void computeBridgingCoeff(const unordered_map<ll, vector<ll>> &adj,
                           unordered_map<ll, CentralityResult> &results) {
     // First pass: compute out-degree for all nodes
     unordered_map<ll, int> degree;
     for (const auto &p : adj) degree[p.first] = p.second.size();
 
     // Second pass: compute bridging coefficient for each node
     for (const auto &p : adj) {
         ll v = p.first;
         const auto &nbrs = p.second;  // Outgoing neighbors
         
         // Handle edge cases: isolated nodes or nodes with no outgoing edges
         if (degree[v] == 0 || nbrs.empty()) {
             results[v].bridging_coeff = 0;
             continue;
         }
         
         // Calculate sum of inverse degrees of neighbors
         double sum_inverse_deg = 0;
         for (ll u : nbrs) {
             if (degree[u] > 0) {
                 sum_inverse_deg += 1.0 / degree[u];
             }
         }
 
         // CORRECTED FORMULA: Multiply (not divide) by (1/degree[v])
         // BC(v) = (1/degree(v)) × Σ(1/degree(neighbors))
         // 
         // This gives higher scores to:
         // - Nodes with low degree themselves
         // - Nodes whose neighbors have low degree
         // 
         // Such nodes are "bridges" connecting sparse regions
         results[v].bridging_coeff = (1.0 / degree[v]) * sum_inverse_deg;
     }
 }
 
 /**
  * Finalize bridging centrality computation
  * 
  * @param results Map containing betweenness and bridging coefficients (updated)
  * 
  * Combines the two components to produce final bridging centrality:
  * 
  * Bridging Centrality = Betweenness × Bridging Coefficient
  * 
  * This combination captures nodes that are:
  * 1. On many shortest paths (high betweenness)
  * 2. Connecting sparsely connected regions (high bridging coefficient)
  * 
  * Such nodes are critical bridges in the network structure.
  * 
  * Why multiply instead of add?
  * - Multiplication emphasizes nodes that score high on BOTH metrics
  * - A node with high betweenness but low bridging coefficient is just
  *   a central hub, not necessarily a bridge
  * - A node with high bridging coefficient but low betweenness might not
  *   be on important paths
  * - The product identifies true structural bridges
  */
 void finalize(unordered_map<ll, CentralityResult> &results) {
     for (auto &p : results)
         p.second.bridging_centrality = p.second.betweenness * p.second.bridging_coeff;
 }
 
 /**
  * Write bridging centrality results to CSV file
  * 
  * @param filename Output CSV file path
  * @param results Map of node IDs to their centrality metrics
  * 
  * Creates a CSV file with columns:
  * - Node: Node identifier
  * - Betweenness: Normalized betweenness centrality [0,1]
  * - BridgingCoefficient: Bridging coefficient (unnormalized)
  * - BridgingCentrality: Product of betweenness and bridging coefficient
  * 
  * High precision (10 decimal places) is used because centrality values
  * can be very small, especially in large graphs.
  */
 void writeToCSV(const string &filename,
                 const unordered_map<ll, CentralityResult> &results) {
     ofstream fout(filename);
     if (!fout.is_open()) {
         cerr << "Error: Cannot create " << filename << endl;
         exit(1);
     }
     
     // Write CSV header
     fout << "Node,Betweenness,BridgingCoefficient,BridgingCentrality\n";
     
     // Write data rows with high precision
     for (const auto &p : results)
         fout << p.first << ","
              << fixed << setprecision(10)
              << p.second.betweenness << ","
              << p.second.bridging_coeff << ","
              << p.second.bridging_centrality << "\n";
     
     fout.close();
 }
 
 /**
  * Write detailed analysis results to text file
  * 
  * @param filename Output text file path
  * @param results Map of node IDs to their centrality metrics
  * @param runtime_sec Total computation time in seconds
  * @param memory_mb Peak memory usage in megabytes
  * @param num_nodes Total number of nodes in graph
  * @param num_edges Total number of edges in graph
  * 
  * Generates a comprehensive report including:
  * 1. Graph statistics (size, runtime, memory)
  * 2. Top 10 nodes by bridging centrality (overall importance as bridges)
  * 3. Top 10 nodes by betweenness (on most shortest paths)
  * 4. Top 10 nodes by bridging coefficient (best positioned to bridge)
  * 
  * Different rankings reveal different aspects:
  * - Bridging centrality: Best overall bridges
  * - Betweenness alone: Most central nodes (might be hubs, not bridges)
  * - Bridging coefficient alone: Best structural position (might lack traffic)
  */
 void writeDetailedResults(const string &filename,
                           const unordered_map<ll, CentralityResult> &results,
                           double runtime_sec,
                           double memory_mb,
                           int num_nodes,
                           int num_edges) {
     ofstream fout(filename);
     if (!fout.is_open()) {
         cerr << "Error: Cannot create " << filename << endl;
         exit(1);
     }
     
     // Write header and basic statistics
     fout << "Bridging Centrality Analysis Results\n";
     fout << "====================================\n\n";
     fout << "Graph Statistics:\n";
     fout << "  Nodes: " << num_nodes << "\n";
     fout << "  Edges: " << num_edges << "\n";
     fout << "  Runtime: " << fixed << setprecision(3) << runtime_sec << " seconds\n";
     fout << "  Peak Memory: " << fixed << setprecision(2) << memory_mb << " MB\n";
     fout << "  Runtime per Node: " << fixed << setprecision(6) << (runtime_sec / num_nodes) << " ms\n";
     fout << "  Runtime per Edge: " << fixed << setprecision(6) << (runtime_sec / num_edges) << " ms\n\n";
     
     // Top 10 by Bridging Centrality (combined metric - most important)
     fout << "Top 10 by Bridging Centrality:\n";
     vector<pair<double, ll>> sorted_bridging;
     for (const auto &p : results)
         sorted_bridging.push_back({p.second.bridging_centrality, p.first});
     sort(sorted_bridging.rbegin(), sorted_bridging.rend());  // Sort descending
     
     for (int i = 0; i < min(10, (int)sorted_bridging.size()); i++) {
         fout << "  " << (i+1) << ". Node " << sorted_bridging[i].second 
              << ": " << fixed << setprecision(10) << sorted_bridging[i].first << "\n";
     }
     
     // Top 10 by Betweenness (on most shortest paths)
     fout << "\nTop 10 by Betweenness:\n";
     vector<pair<double, ll>> sorted_betweenness;
     for (const auto &p : results)
         sorted_betweenness.push_back({p.second.betweenness, p.first});
     sort(sorted_betweenness.rbegin(), sorted_betweenness.rend());  // Sort descending
     
     for (int i = 0; i < min(10, (int)sorted_betweenness.size()); i++) {
         fout << "  " << (i+1) << ". Node " << sorted_betweenness[i].second 
              << ": " << fixed << setprecision(10) << sorted_betweenness[i].first << "\n";
     }
     
     // Top 10 by Bridging Coefficient (best structural position)
     fout << "\nTop 10 by Bridging Coefficient:\n";
     vector<pair<double, ll>> sorted_coeff;
     for (const auto &p : results)
         sorted_coeff.push_back({p.second.bridging_coeff, p.first});
     sort(sorted_coeff.rbegin(), sorted_coeff.rend());  // Sort descending
     
     for (int i = 0; i < min(10, (int)sorted_coeff.size()); i++) {
         fout << "  " << (i+1) << ". Node " << sorted_coeff[i].second 
              << ": " << fixed << setprecision(10) << sorted_coeff[i].first << "\n";
     }
     
     fout.close();
 }
 
 /**
  * Main function: Orchestrates bridging centrality computation
  * 
  * @param argc Number of command-line arguments
  * @param argv Array of command-line arguments
  * @return 0 on success, 1 on error
  * 
  * Usage: ./bridging_centrality <input_file> <output_dir>
  * 
  * Process:
  * 1. Load directed graph from file
  * 2. Compute betweenness centrality (Brandes' algorithm)
  * 3. Compute bridging coefficient
  * 4. Combine into final bridging centrality
  * 5. Write results to CSV and detailed text files
  * 6. Track memory usage throughout
  * 
  * Output files:
  * - <basename>.csv: Complete node-centrality mapping
  * - <basename>_detailed.txt: Analysis report with top nodes
  */
 int main(int argc, char *argv[]) {
     // Validate command-line arguments
     if (argc != 3) {
         cerr << "Usage: ./bridging_centrality <input_file> <output_dir>\n";
         return 1;
     }
     
     string inputFile = argv[1];
     string outputDir = argv[2];
     
     // Start timing
     auto start_time = chrono::high_resolution_clock::now();
     MemoryTracker mem;
     
     // Initialize data structures
     unordered_map<ll, vector<ll>> adj;
     unordered_map<ll, CentralityResult> results;
     
     // Step 1: Load graph from file
     loadGraph(inputFile, adj);
     mem.update();
     
     // Calculate graph statistics
     int num_nodes = adj.size();
     int num_edges = 0;
     for (const auto &p : adj) num_edges += p.second.size();
     
     // Step 2: Compute betweenness centrality (most time-consuming)
     computeBetweenness(adj, results);
     mem.update();
     
     // Step 3: Compute bridging coefficient
     computeBridgingCoeff(adj, results);
     mem.update();
     
     // Step 4: Combine into final bridging centrality
     finalize(results);
     mem.update();
     
     // Extract basename from input file path for output naming
     string basename = inputFile;
     size_t last_slash = basename.rfind('/');
     if (last_slash != string::npos) basename = basename.substr(last_slash + 1);
     size_t dot_pos = basename.rfind('.');
     if (dot_pos != string::npos) basename = basename.substr(0, dot_pos);
     
     // Construct output file paths
     string csv_file = outputDir + "/" + basename + ".csv";
     string detailed_file = outputDir + "/" + basename + "_detailed.txt";
     
     // Write CSV output
     writeToCSV(csv_file, results);
     
     // Calculate total runtime
     auto end_time = chrono::high_resolution_clock::now();
     double runtime_sec = chrono::duration<double>(end_time - start_time).count();
     
     // Write detailed analysis report
     writeDetailedResults(detailed_file, results, runtime_sec, mem.peak_memory_mb, num_nodes, num_edges);
     
     // Print summary to stderr
     cerr << "Bridging centrality computed successfully.\n";
     cerr << "Nodes: " << num_nodes << ", Edges: " << num_edges << "\n";
     cerr << "Runtime: " << fixed << setprecision(3) << runtime_sec << " seconds\n";
     cerr << "Peak Memory: " << fixed << setprecision(2) << mem.peak_memory_mb << " MB\n";
     
     return 0;
 }