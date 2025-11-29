#include <iostream>
#include <fstream>
#include <vector>
#include <queue>
#include <algorithm>
#include <map>

using namespace std;

class KCore {
private:
    int n;
    vector<vector<int>> adj;
    vector<int> coreness;
    
public:
    KCore(int vertices) : n(vertices), adj(vertices), coreness(vertices, 0) {}
    
    void addEdge(int u, int v) {
        // Skip self-loops
        if (u == v) return;
        
        adj[u].push_back(v);
        adj[v].push_back(u);
    }
    
    vector<int> computeKCore() {
        vector<int> degree(n);
        vector<int> pos(n);      // position of vertex in vert array
        vector<int> vert(n);     // vertices sorted by degree
        
        // Compute initial degrees and find max degree
        int maxDegree = 0;
        for (int i = 0; i < n; i++) {
            degree[i] = adj[i].size();
            if (degree[i] > maxDegree) {
                maxDegree = degree[i];
            }
        }
        
        // Handle edge case: empty graph
        if (maxDegree == 0) {
            return coreness; // all zeros
        }
        
        // Create bins for bucket sort
        vector<int> bin(maxDegree + 1, 0);
        
        // Count vertices in each bin (line 13-14 in paper)
        for (int i = 0; i < n; i++) {
            bin[degree[i]]++;
        }
        
        // Compute starting positions of bins (line 15-20 in paper)
        int start = 0;
        for (int d = 0; d <= maxDegree; d++) {
            int num = bin[d];
            bin[d] = start;
            start += num;
        }
        
        // Place vertices in sorted order (line 21-25 in paper)
        for (int i = 0; i < n; i++) {
            pos[i] = bin[degree[i]];
            vert[pos[i]] = i;
            bin[degree[i]]++;
        }
        
        // Restore bin starting positions (line 26-27 in paper)
        for (int d = maxDegree; d > 0; d--) {
            bin[d] = bin[d - 1];
        }
        bin[0] = 0;
        
        // Main loop: process vertices in order (line 28-41 in paper)
        for (int i = 0; i < n; i++) {
            int v = vert[i];
            
            // Update neighbors (line 30-40)
            for (int u : adj[v]) {
                if (degree[u] > degree[v]) {
                    int du = degree[u];
                    int pu = pos[u];
                    int pw = bin[du];
                    int w = vert[pw];
                    
                    // Swap u with first vertex in its bin (line 34-37)
                    if (u != w) {
                        pos[u] = pw;
                        vert[pu] = w;
                        pos[w] = pu;
                        vert[pw] = u;
                    }
                    
                    // Move bin start forward and decrease degree (line 38)
                    bin[du]++;
                    degree[u]--;
                }
            }
        }
        
        // Assign core numbers
        for (int i = 0; i < n; i++) {
            coreness[i] = degree[i];
        }
        
        return coreness;
    }
    
    void printCoreness() {
        cout << "Vertex\tCoreness\n";
        cout << "----------------\n";
        for (int i = 0; i < n; i++) {
            cout << i << "\t" << coreness[i] << "\n";
        }
    }
    
    int getMaxKCore() {
        return *max_element(coreness.begin(), coreness.end());
    }
    
    vector<int> getVerticesInKCore(int k) {
        vector<int> vertices;
        for (int i = 0; i < n; i++) {
            if (coreness[i] >= k) {
                vertices.push_back(i);
            }
        }
        return vertices;
    }
};

int main(int argc, char* argv[]) {
    /*
     * INPUT FORMAT:
     * Line 1: n (number of vertices), m (number of edges), [optional third number]
     * Next m lines: u v (edge between vertex u and v)
     * 
     * Usage: ./kcore <input_file> [output_file]
     * Example: ./kcore cit-DBLP.edges output.txt
     * 
     * OUTPUT:
     * - Coreness value for each vertex
     * - Maximum k-core number
     * - Statistics about k-core distribution
     */
    
    if (argc < 2) {
        cerr << "Usage: " << argv[0] << " <input_file> [output_file]\n";
        cerr << "Example: " << argv[0] << " cit-DBLP.edges output.txt\n";
        return 1;
    }
    
    string inputFile = argv[1];
    string outputFile = (argc >= 3) ? argv[2] : "";
    
    ifstream inFile(inputFile);
    if (!inFile) {
        cerr << "Error: Cannot open input file " << inputFile << "\n";
        return 1;
    }
    
    int n, m, temp;
    inFile >> n >> m;
    
    // Handle optional third number in first line (like in cit-DBLP format)
    if (inFile.peek() != '\n' && inFile.peek() != EOF) {
        inFile >> temp;
    }
    
    cout << "Reading graph from " << inputFile << "...\n";
    cout << "Vertices: " << n << ", Edges: " << m << "\n";
    
    KCore kcore(n);
    
    int edgeCount = 0;
    for (int i = 0; i < m; i++) {
        int u, v;
        if (!(inFile >> u >> v)) {
            cerr << "Warning: Could not read edge " << i + 1 << "\n";
            break;
        }
        
        // Skip self-loops
        if (u == v) {
            continue;
        }
        
        // Validate vertex IDs
        if (u < 1 || u > n || v < 1 || v > n) {
            cerr << "Warning: Invalid edge (" << u << ", " << v << "), skipping\n";
            continue;
        }
        
        // Convert to 0-indexed
        kcore.addEdge(u - 1, v - 1);
        edgeCount++;
    }
    
    inFile.close();
    cout << "Successfully read " << edgeCount << " edges\n";
    
    cout << "\n=== Computing K-Core Decomposition ===\n";
    
    // Compute k-core decomposition
    vector<int> coreness = kcore.computeKCore();
    
    cout << "Computation complete!\n";
    
    int maxCore = kcore.getMaxKCore();
    
    // Compute statistics
    map<int, int> coreDistribution;
    for (int i = 0; i < n; i++) {
        coreDistribution[coreness[i]]++;
    }
    
    // Output results
    ostream* outStream;
    ofstream outFileStream;
    
    if (!outputFile.empty()) {
        outFileStream.open(outputFile);
        if (!outFileStream) {
            cerr << "Warning: Cannot open output file " << outputFile << ", using stdout\n";
            outStream = &cout;
        } else {
            outStream = &outFileStream;
            cout << "Writing results to " << outputFile << "...\n";
        }
    } else {
        outStream = &cout;
    }
    
    *outStream << "\n=== K-Core Decomposition Results ===\n\n";
    *outStream << "Maximum k-core: " << maxCore << "\n\n";
    
    *outStream << "K-Core Distribution:\n";
    *outStream << "Core\tVertices\n";
    *outStream << "--------------------\n";
    for (auto& [core, count] : coreDistribution) {
        *outStream << core << "\t" << count << "\n";
    }
    
    *outStream << "\n=== Coreness Values (first 50 vertices) ===\n";
    *outStream << "Vertex\tCoreness\n";
    *outStream << "----------------\n";
    int displayLimit = min(50, n);
    for (int i = 0; i < displayLimit; i++) {
        *outStream << (i + 1) << "\t" << coreness[i] << "\n";
    }
    if (n > 50) {
        *outStream << "... (" << (n - 50) << " more vertices)\n";
    }
    
    // Print vertices in top k-cores
    *outStream << "\n=== Top K-Cores ===\n";
    int topCores = min(5, maxCore);
    for (int k = maxCore; k > maxCore - topCores && k > 0; k--) {
        vector<int> vertices = kcore.getVerticesInKCore(k);
        *outStream << k << "-core: " << vertices.size() << " vertices\n";
        
        // Show first 20 vertices in this core
        *outStream << "  Sample vertices: ";
        int showCount = min(20, (int)vertices.size());
        for (int i = 0; i < showCount; i++) {
            *outStream << (vertices[i] + 1) << " ";
        }
        if (vertices.size() > 20) {
            *outStream << "... (" << (vertices.size() - 20) << " more)";
        }
        *outStream << "\n";
    }
    
    // Find most influential vertices (highest k-core members)
    *outStream << "\n=== Most Influential Papers (Highest K-Core Members) ===\n";
    vector<pair<int, int>> vertexCoreness; // (coreness, vertex_id)
    for (int i = 0; i < n; i++) {
        vertexCoreness.push_back({coreness[i], i});
    }
    
    // Sort by coreness (descending), then by vertex ID
    sort(vertexCoreness.begin(), vertexCoreness.end(), 
         [](const pair<int,int>& a, const pair<int,int>& b) {
             if (a.first != b.first) return a.first > b.first;
             return a.second < b.second;
         });
    
    *outStream << "\nTop 100 Most Influential Papers:\n";
    *outStream << "Rank\tPaper_ID\tCoreness\n";
    *outStream << "--------------------------------\n";
    int rankLimit = min(100, n);
    for (int i = 0; i < rankLimit; i++) {
        *outStream << (i + 1) << "\t" 
                   << (vertexCoreness[i].second + 1) << "\t\t" 
                   << vertexCoreness[i].first << "\n";
    }
    
    // Statistics about influential papers
    *outStream << "\n=== Influence Distribution ===\n";
    int maxCoreCount = kcore.getVerticesInKCore(maxCore).size();
    *outStream << "Papers in maximum k-core (" << maxCore << "): " << maxCoreCount << "\n";
    
    // Count papers in top tiers
    vector<int> topTierCounts;
    for (int k = maxCore; k >= max(1, maxCore - 5) && k > 0; k--) {
        int count = kcore.getVerticesInKCore(k).size();
        *outStream << "Papers with coreness >= " << k << ": " << count 
                   << " (" << (100.0 * count / n) << "%)\n";
    }
    
    if (outFileStream.is_open()) {
        outFileStream.close();
        cout << "Results written successfully!\n";
    }
    
    cout << "\n=== Summary ===\n";
    cout << "Total papers (vertices): " << n << "\n";
    cout << "Total citations (edges): " << edgeCount << "\n";
    cout << "Maximum k-core: " << maxCore << "\n";
    cout << "Papers in max k-core: " << kcore.getVerticesInKCore(maxCore).size() << "\n";
    
    // Show top 10 most influential on console
    cout << "\n=== Top 10 Most Influential Papers ===\n";
    vector<pair<int, int>> topInfluential;
    for (int i = 0; i < n; i++) {
        topInfluential.push_back({coreness[i], i});
    }
    sort(topInfluential.begin(), topInfluential.end(), 
         [](const pair<int,int>& a, const pair<int,int>& b) {
             if (a.first != b.first) return a.first > b.first;
             return a.second < b.second;
         });
    
    cout << "Rank\tPaper_ID\tCoreness\n";
    cout << "--------------------------------\n";
    for (int i = 0; i < min(10, n); i++) {
        cout << (i + 1) << "\t" 
             << (topInfluential[i].second + 1) << "\t\t" 
             << topInfluential[i].first << "\n";
    }
    
    cout << "\nNote: Higher coreness indicates papers that are part of denser,\n";
    cout << "      more interconnected citation clusters - typically highly\n";
    cout << "      influential foundational works in their field.\n";
    
    return 0;
}

/*
 * ALGORITHM EXPLANATION (Batagelj-Zaversnik Algorithm):
 * 
 * The key insight is to use a bucket sort approach where vertices are
 * processed in increasing order of their degrees. When a vertex is removed,
 * we decrease the degrees of its neighbors and reposition them if needed.
 * 
 * KEY FIX: The original implementation incorrectly checked if degree[u] < d
 * when repositioning neighbors. The correct approach is to ALWAYS reposition
 * neighbors when their degree decreases, using the swap-and-advance technique.
 * 
 * The algorithm maintains:
 * - bin[d]: starting position in vert[] for vertices of degree d
 * - vert[i]: vertex at position i (sorted by degree)
 * - pos[v]: position of vertex v in vert[]
 * 
 * When vertex u's degree decreases from du to du-1:
 * 1. Swap u with the first vertex in bin[du]
 * 2. Advance bin[du] forward (shrinking that bin, growing du-1 bin)
 * 
 * This maintains the invariant that vertices are sorted by degree.
 */
