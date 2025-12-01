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

class BetweennessCentrality {
private:
    int n;
    vector<vector<int>> adj;
    vector<double> betweenness;
    long long memoryUsed;
    
public:
    BetweennessCentrality(int vertices) : n(vertices), adj(vertices), betweenness(vertices, 0.0), memoryUsed(0) {
        memoryUsed = vertices * (sizeof(vector<int>) + sizeof(double));
    }
    
    void addEdge(int u, int v) {
        if (u == v) return;
        adj[u].push_back(v);
        adj[v].push_back(u);
        memoryUsed += 2 * sizeof(int);
    }
    
    vector<double> computeBetweenness() {
        auto start = high_resolution_clock::now();
        
        // Process each node as source
        for (int source = 0; source < n; source++) {
            stack<int> traversal_stack;
            vector<int> distance(n, -1);
            vector<double> path_count(n, 0.0);
            vector<vector<int>> predecessors(n);
            queue<int> bfs_queue;
            
            // Initialize BFS
            path_count[source] = 1.0;
            distance[source] = 0;
            bfs_queue.push(source);
            
            // BFS traversal
            while (!bfs_queue.empty()) {
                int current = bfs_queue.front();
                bfs_queue.pop();
                traversal_stack.push(current);
                
                for (int neighbor : adj[current]) {
                    if (distance[neighbor] < 0) {
                        bfs_queue.push(neighbor);
                        distance[neighbor] = distance[current] + 1;
                    }
                    
                    if (distance[neighbor] == distance[current] + 1) {
                        path_count[neighbor] += path_count[current];
                        predecessors[neighbor].push_back(current);
                    }
                }
            }
            
            // Accumulate dependencies
            vector<double> dependency(n, 0.0);
            while (!traversal_stack.empty()) {
                int node = traversal_stack.top();
                traversal_stack.pop();
                
                for (int pred : predecessors[node]) {
                    dependency[pred] += (path_count[pred] / path_count[node]) * (1.0 + dependency[node]);
                }
                
                if (node != source) {
                    betweenness[node] += dependency[node] / 2.0;
                }
            }
        }
        
        return betweenness;
    }
    
    double getMaxBetweenness() {
        return *max_element(betweenness.begin(), betweenness.end());
    }
    
    vector<pair<double, int>> getTopNodes(int k) {
        vector<pair<double, int>> ranked;
        for (int i = 0; i < n; i++) {
            ranked.push_back({betweenness[i], i});
        }
        sort(ranked.begin(), ranked.end(), [](auto& a, auto& b) {
            if (a.first != b.first) return a.first > b.first;
            return a.second < b.second;
        });
        ranked.resize(min(k, (int)ranked.size()));
        return ranked;
    }
    
    long long getMemoryUsage() {
        return memoryUsed;
    }
    
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
