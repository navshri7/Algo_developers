/**
 * Degree Centrality Algorithm Implementation for Directed Graphs
 * 
 * This program computes degree centrality metrics for vertices in a directed graph.
 * Unlike undirected graphs where each vertex has a single degree, directed graphs
 * distinguish between:
 * - In-degree: Number of incoming edges (citations received in citation networks)
 * - Out-degree: Number of outgoing edges (citations made in citation networks)
 * - Total degree: Sum of in-degree and out-degree
 * 
 * Degree centrality is the simplest centrality measure, directly counting connections.
 * In citation networks, in-degree is particularly important as it represents impact
 * (how many papers cite this paper), while out-degree represents thoroughness
 * (how many papers this paper cites).
 * 
 * Date: December 2, 2025
 * 
 * Time Complexity: O(m) where m = number of edges (single pass through edge list)
 * Space Complexity: O(n) where n = number of unique vertices
 * 
 * Input Format: 
 *   - Each line: cited citing (directed edge from citing to cited)
 *   - Example: "100 200" means paper 200 cites paper 100
 *   - This represents a directed edge: 200 -> 100
 * 
 * IMPORTANT - Edge Direction Convention:
 * The input format "cited citing" means:
 *   - First column (cited): The paper being cited (target of the edge)
 *   - Second column (citing): The paper making the citation (source of the edge)
 *   - Edge direction: citing -> cited (from second column to first column)
 * 
 * This convention affects degree calculations:
 *   - In-degree of a node = number of times it appears in first column (cited)
 *   - Out-degree of a node = number of times it appears in second column (citing)
 * 
 * Output:
 *   - CSV file with degree metrics for each node
 *   - Detailed text file with statistics and top nodes by various metrics
 */

 #include <bits/stdc++.h>
 #include <chrono>
 #include <sys/resource.h>
 using namespace std;
 
 typedef long long ll;
 
 /**
  * DegreeResult Structure
  * 
  * Stores the degree centrality metrics for a single vertex in a directed graph.
  * 
  * For directed graphs, we track three metrics:
  * - indegree: Number of incoming edges (edges pointing TO this vertex)
  * - outdegree: Number of outgoing edges (edges pointing FROM this vertex)
  * - total: Sum of indegree and outdegree
  * 
  * In citation networks:
  * - High in-degree = highly cited paper (influential, important)
  * - High out-degree = paper with many references (thorough literature review)
  * - High total degree = well-connected paper (both influential and thorough)
  */
 struct DegreeResult {
     int indegree = 0;   // Number of incoming edges (citations received)
     int outdegree = 0;  // Number of outgoing edges (citations made)
     int total = 0;      // Total degree (indegree + outdegree)
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
      * 
      * Note: This measures the entire process's memory, not just the algorithm's
      * data structures. It includes overhead from C++ runtime, standard library, etc.
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
  * Compute degree centrality for all vertices in a directed graph
  * 
  * @param filepath Path to the input file containing edge list
  * @param results Map from node ID to its degree metrics (output parameter)
  * 
  * Algorithm:
  * 1. Read edge list from file
  * 2. For each edge (cited, citing):
  *    - Increment out-degree of 'citing' node (source of edge)
  *    - Increment in-degree of 'cited' node (target of edge)
  * 3. Compute total degree as sum of in-degree and out-degree
  * 
  * CRITICAL - Understanding Edge Direction:
  * Input format: "cited citing" means node 'citing' cites node 'cited'
  * This creates a DIRECTED edge: citing -> cited
  * 
  * Therefore:
  * - When we see "100 200", it means paper 200 cites paper 100
  * - Edge direction: 200 -> 100
  * - Paper 100 gets +1 in-degree (it is cited)
  * - Paper 200 gets +1 out-degree (it cites)
  * 
  * Why this matters:
  * - In citation networks, in-degree represents impact/influence
  * - Papers with high in-degree are highly cited (authoritative)
  * - Papers with high out-degree cite many papers (comprehensive)
  * 
  * Time Complexity: O(m) where m = number of edges
  * Space Complexity: O(n) where n = number of unique nodes
  */
 void computeDegreeCentrality(const string &filepath,
                              unordered_map<ll, DegreeResult> &results) {
 
     ifstream fin(filepath);
     if (!fin.is_open()) {
         cerr << "Error: Cannot open input file: " << filepath << endl;
         exit(1);
     }
 
     ll cited, citing;
     
     // Process each edge in the graph
     // Format: "cited citing" represents edge citing -> cited
     while (fin >> cited >> citing) {
         // Ensure both nodes exist in results map
         // Initialize with zero degrees if this is first time seeing the node
         if (results.find(cited) == results.end())
             results[cited] = {0, 0, 0};
         if (results.find(citing) == results.end())
             results[citing] = {0, 0, 0};
         
         // Update degree counts based on edge direction
         // Edge direction: citing -> cited
         results[citing].outdegree++;  // 'citing' node has outgoing edge
         results[cited].indegree++;    // 'cited' node has incoming edge
     }
     
     // Compute total degree for each node
     // Total degree = in-degree + out-degree
     // This gives a measure of overall connectivity regardless of direction
     for (auto &entry : results)
         entry.second.total = entry.second.indegree + entry.second.outdegree;
 
     fin.close();
 }
 
 /**
  * Write degree centrality results to CSV file
  * 
  * @param filename Output CSV file path
  * @param results Map of node IDs to their degree metrics
  * 
  * Creates a CSV file with columns:
  * - Node: Node identifier
  * - InDegree: Number of incoming edges (citations received)
  * - OutDegree: Number of outgoing edges (citations made)
  * - TotalDegree: Sum of in-degree and out-degree
  * 
  * This format is suitable for:
  * - Importing into spreadsheet software
  * - Further analysis in R, Python, or other tools
  * - Graph visualization software that accepts CSV input
  */
 void writeToCSV(const string &filename,
                 const unordered_map<ll, DegreeResult> &results) {
     ofstream fout(filename);
     if (!fout.is_open()) {
         cerr << "Error: Cannot create output file: " << filename << endl;
         exit(1);
     }
 
     // Write CSV header
     fout << "Node,InDegree,OutDegree,TotalDegree\n";
     
     // Write data rows
     for (const auto &entry : results) {
         fout << entry.first << ","                  // Node ID
              << entry.second.indegree << ","        // In-degree
              << entry.second.outdegree << ","       // Out-degree
              << entry.second.total << "\n";         // Total degree
     }
 
     fout.close();
 }
 
 /**
  * Write detailed analysis results to text file
  * 
  * @param filename Output text file path
  * @param results Map of node IDs to their degree metrics
  * @param runtime_sec Total computation time in seconds
  * @param memory_mb Peak memory usage in megabytes
  * @param num_edges Total number of edges in the graph
  * 
  * Generates a comprehensive report including:
  * 1. Graph statistics (nodes, edges, runtime, memory)
  * 2. Top 10 nodes by total degree (most connected overall)
  * 3. Top 10 nodes by in-degree (most cited/influential)
  * 4. Top 10 nodes by out-degree (most citations made/thorough)
  * 
  * The different rankings are meaningful in different contexts:
  * - In-degree ranking: Identifies most influential/important nodes
  * - Out-degree ranking: Identifies most comprehensive/thorough nodes
  * - Total degree ranking: Identifies most connected nodes overall
  */
 void writeDetailedResults(const string &filename,
                           const unordered_map<ll, DegreeResult> &results,
                           double runtime_sec,
                           double memory_mb,
                           int num_edges) {
     ofstream fout(filename);
     if (!fout.is_open()) {
         cerr << "Error: Cannot create " << filename << endl;
         exit(1);
     }
     
     // Write header and basic statistics
     fout << "Degree Centrality Analysis Results\n";
     fout << "==================================\n\n";
     fout << "Graph Statistics:\n";
     fout << "  Nodes: " << results.size() << "\n";
     fout << "  Edges: " << num_edges << "\n";
     fout << "  Runtime: " << fixed << setprecision(3) << runtime_sec << " seconds\n";
     fout << "  Peak Memory: " << fixed << setprecision(2) << memory_mb << " MB\n";
     fout << "  Runtime per Node: " << fixed << setprecision(6) << (runtime_sec / results.size()) << " ms\n";
     fout << "  Runtime per Edge: " << fixed << setprecision(6) << (runtime_sec / num_edges) << " ms\n\n";
     
     // Top 10 by Total Degree (most connected overall)
     fout << "Top 10 by Total Degree:\n";
     vector<pair<int, ll>> sorted_total;
     for (const auto &p : results)
         sorted_total.push_back({p.second.total, p.first});
     sort(sorted_total.rbegin(), sorted_total.rend());  // Sort descending
     
     for (int i = 0; i < min(10, (int)sorted_total.size()); i++) {
         fout << "  " << (i+1) << ". Node " << sorted_total[i].second 
              << ": " << sorted_total[i].first << "\n";
     }
     
     // Top 10 by In-Degree (most cited/influential)
     // In citation networks, high in-degree = highly cited paper
     // These are typically landmark papers, review papers, or foundational work
     fout << "\nTop 10 by In-Degree (Citations Received):\n";
     vector<pair<int, ll>> sorted_indegree;
     for (const auto &p : results)
         sorted_indegree.push_back({p.second.indegree, p.first});
     sort(sorted_indegree.rbegin(), sorted_indegree.rend());  // Sort descending
     
     for (int i = 0; i < min(10, (int)sorted_indegree.size()); i++) {
         fout << "  " << (i+1) << ". Node " << sorted_indegree[i].second 
              << ": " << sorted_indegree[i].first << "\n";
     }
     
     // Top 10 by Out-Degree (most citations made)
     // In citation networks, high out-degree = paper cites many others
     // These are typically review papers or papers building on extensive prior work
     fout << "\nTop 10 by Out-Degree (Citations Made):\n";
     vector<pair<int, ll>> sorted_outdegree;
     for (const auto &p : results)
         sorted_outdegree.push_back({p.second.outdegree, p.first});
     sort(sorted_outdegree.rbegin(), sorted_outdegree.rend());  // Sort descending
     
     for (int i = 0; i < min(10, (int)sorted_outdegree.size()); i++) {
         fout << "  " << (i+1) << ". Node " << sorted_outdegree[i].second 
              << ": " << sorted_outdegree[i].first << "\n";
     }
     
     fout.close();
 }
 
 /**
  * Main function: Orchestrates degree centrality computation
  * 
  * @param argc Number of command-line arguments
  * @param argv Array of command-line arguments
  * @return 0 on success, 1 on error
  * 
  * Usage: ./degree_centrality <input_file> <output_dir>
  * 
  * Process:
  * 1. Parse command-line arguments
  * 2. Read graph and compute degree metrics
  * 3. Track memory usage
  * 4. Write results to CSV and detailed text files
  * 5. Print summary statistics to stderr
  * 
  * Output files:
  * - <basename>.csv: Complete node-degree mapping
  * - <basename>_detailed.txt: Analysis report with top nodes
  */
 int main(int argc, char* argv[]) {
 
     // Validate command-line arguments
     if (argc != 3) {
         cerr << "Usage: ./degree_centrality <input_file> <output_dir>\n";
         return 1;
     }
     
     string inputFile = argv[1];
     string outputDir = argv[2];
     
     // Start timing
     auto start_time = chrono::high_resolution_clock::now();
     MemoryTracker mem;
     
     // Compute degree centrality for all nodes
     unordered_map<ll, DegreeResult> results;
     computeDegreeCentrality(inputFile, results);
     mem.update();  // Record peak memory after computation
     
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
     
     // Count total edges (sum of all in-degrees = total number of edges)
     int num_edges = 0;
     for (const auto &p : results) {
         num_edges += p.second.indegree;
     }
     
     // Write detailed analysis report
     writeDetailedResults(detailed_file, results, runtime_sec, mem.peak_memory_mb, num_edges);
     
     // Print summary to stderr
     cerr << "Degree centrality computed successfully.\n";
     cerr << "Nodes: " << results.size() << ", Edges: " << num_edges << "\n";
     cerr << "Runtime: " << fixed << setprecision(3) << runtime_sec << " seconds\n";
     cerr << "Peak Memory: " << fixed << setprecision(2) << mem.peak_memory_mb << " MB\n";
     
     return 0;
 }