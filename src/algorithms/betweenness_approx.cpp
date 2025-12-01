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

class ApproximateBetweenness {
private:
    int n;
    vector<vector<int>> adj;
    vector<double> betweenness;
    long long memoryUsed;
    int numSamples;
    
public:
    ApproximateBetweenness(int vertices, int samples = -1) 
        : n(vertices), adj(vertices), betweenness(vertices, 0.0), memoryUsed(0) {
        memoryUsed = vertices * (sizeof(vector<int>) + sizeof(double));
        
        if (samples < 0) {
            // Calculate samples based on accuracy requirements
            double eps = 0.1;
            double conf = 0.1;
            numSamples = (int)ceil((0.5 / (eps * eps)) * log(vertices / conf));
            numSamples = min(numSamples, vertices);
            numSamples = max(numSamples, vertices / 10);
        } else {
            numSamples = min(samples, vertices);
        }
    }
    
    void addEdge(int u, int v) {
        if (u == v) return;
        adj[u].push_back(v);
        adj[v].push_back(u);
        memoryUsed += 2 * sizeof(int);
    }
    
    vector<double> computeApproximateBetweenness() {
        // Select random samples
        vector<int> allNodes;
        for (int i = 0; i < n; i++) {
            allNodes.push_back(i);
        }
        
        srand(42);
        vector<int> sampledNodes;
        vector<int> available = allNodes;
        for (int i = 0; i < numSamples; i++) {
            int idx = rand() % available.size();
            sampledNodes.push_back(available[idx]);
            available.erase(available.begin() + idx);
        }
        
        double scalingFactor = (double)n / (double)numSamples;
        
        // Process each sampled node
        for (int source : sampledNodes) {
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
            
            // Accumulate dependencies with scaling
            vector<double> dependency(n, 0.0);
            while (!traversal_stack.empty()) {
                int node = traversal_stack.top();
                traversal_stack.pop();
                
                for (int pred : predecessors[node]) {
                    dependency[pred] += (path_count[pred] / path_count[node]) * (1.0 + dependency[node]);
                }
                
                if (node != source) {
                    betweenness[node] += (dependency[node] / 2.0) * scalingFactor;
                }
            }
        }
        
        return betweenness;
    }
    
    double getMaxBetweenness() {
        return *max_element(betweenness.begin(), betweenness.end());
    }
    
    int getNumSamples() {
        return numSamples;
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
