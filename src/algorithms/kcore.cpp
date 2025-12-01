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

class KCore {
private:
    int n;
    vector<vector<int>> adj;
    vector<int> coreness;
    long long memoryUsed;
    
public:
    KCore(int vertices) : n(vertices), adj(vertices), coreness(vertices, 0), memoryUsed(0) {
        // Estimate memory usage
        memoryUsed = vertices * (sizeof(vector<int>) + sizeof(int));
    }
    
    void addEdge(int u, int v) {
        if (u == v) return;
        adj[u].push_back(v);
        adj[v].push_back(u);
        memoryUsed += 2 * sizeof(int);
    }
    
    vector<int> computeKCore() {
        auto start = high_resolution_clock::now();
        
        vector<int> degree(n);
        vector<int> pos(n);
        vector<int> vert(n);
        
        memoryUsed += 3 * n * sizeof(int);
        
        int maxDegree = 0;
        for (int i = 0; i < n; i++) {
            degree[i] = adj[i].size();
            if (degree[i] > maxDegree) {
                maxDegree = degree[i];
            }
        }
        
        if (maxDegree == 0) {
            return coreness;
        }
        
        vector<int> bin(maxDegree + 1, 0);
        memoryUsed += (maxDegree + 1) * sizeof(int);
        
        for (int i = 0; i < n; i++) {
            bin[degree[i]]++;
        }
        
        int start_pos = 0;
        for (int d = 0; d <= maxDegree; d++) {
            int num = bin[d];
            bin[d] = start_pos;
            start_pos += num;
        }
        
        for (int i = 0; i < n; i++) {
            pos[i] = bin[degree[i]];
            vert[pos[i]] = i;
            bin[degree[i]]++;
        }
        
        for (int d = maxDegree; d > 0; d--) {
            bin[d] = bin[d - 1];
        }
        bin[0] = 0;
        
        for (int i = 0; i < n; i++) {
            int v = vert[i];
            
            for (int u : adj[v]) {
                if (degree[u] > degree[v]) {
                    int du = degree[u];
                    int pu = pos[u];
                    int pw = bin[du];
                    int w = vert[pw];
                    
                    if (u != w) {
                        pos[u] = pw;
                        vert[pu] = w;
                        pos[w] = pu;
                        vert[pw] = u;
                    }
                    
                    bin[du]++;
                    degree[u]--;
                }
            }
        }
        
        for (int i = 0; i < n; i++) {
            coreness[i] = degree[i];
        }
        
        return coreness;
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
    
    long long getMemoryUsage() {
        return memoryUsed;
    }
    
    map<int, int> getCoreDistribution() {
        map<int, int> dist;
        for (int i = 0; i < n; i++) {
            dist[coreness[i]]++;
        }
        return dist;
    }
};

void writeDetailedResults(const string& outputFile, const string& datasetName, 
                         int n, int m, int maxCore, const map<int, int>& dist,
                         double runtime, long long memory, const vector<int>& coreness) {
    ofstream out(outputFile);
    
    out << "Dataset: " << datasetName << "\n";
    out << "Vertices: " << n << "\n";
    out << "Edges: " << m << "\n";
    out << "Max K-Core: " << maxCore << "\n";
    out << "Runtime (seconds): " << fixed << setprecision(6) << runtime << "\n";
    out << "Memory Usage (MB): " << fixed << setprecision(2) << (memory / 1048576.0) << "\n";
    out << "\n=== Core Distribution ===\n";
    out << "Core\tCount\tPercentage\n";
    
    for (auto& [core, count] : dist) {
        out << core << "\t" << count << "\t" 
            << fixed << setprecision(2) << (100.0 * count / n) << "%\n";
    }
    
    out << "\n=== Top 100 Vertices by Coreness ===\n";
    out << "Rank\tVertex_ID\tCoreness\n";
    
    vector<pair<int, int>> ranked;
    for (int i = 0; i < n; i++) {
        ranked.push_back({coreness[i], i});
    }
    sort(ranked.begin(), ranked.end(), [](auto& a, auto& b) {
        if (a.first != b.first) return a.first > b.first;
        return a.second < b.second;
    });
    
    for (int i = 0; i < min(100, (int)ranked.size()); i++) {
        out << (i+1) << "\t" << (ranked[i].second + 1) << "\t" << ranked[i].first << "\n";
    }
    
    out.close();
}

void writeCSVSummary(const string& csvFile, const string& datasetName,
                    int n, int m, int maxCore, double runtime, long long memory,
                    double avgDegree, double density) {
    bool fileExists = ifstream(csvFile).good();
    ofstream out(csvFile, ios::app);
    
    if (!fileExists) {
        out << "Dataset,Vertices,Edges,MaxCore,Runtime_sec,Memory_MB,AvgDegree,Density\n";
    }
    
    out << datasetName << "," << n << "," << m << "," << maxCore << ","
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
    
    // Create output directory if needed
    system(("mkdir -p " + outputDir).c_str());
    
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
    
    // Parse first data line
    istringstream iss(line);
    int n, m;
    iss >> n >> m;
    
    cout << "Dataset: " << datasetName << "\n";
    cout << "Vertices: " << n << ", Edges: " << m << "\n";
    
    auto readStart = high_resolution_clock::now();
    KCore kcore(n);
    
    int edgeCount = 0;
    set<pair<int,int>> uniqueEdges;
    
    // Read edges
    int u, v;
    while (inFile >> u >> v) {
        if (u == v) continue;
        if (u < 1 || u > n || v < 1 || v > n) continue;
        
        // Ensure we don't double-count edges
        int minV = min(u, v);
        int maxV = max(u, v);
        if (uniqueEdges.find({minV, maxV}) == uniqueEdges.end()) {
            uniqueEdges.insert({minV, maxV});
            kcore.addEdge(u - 1, v - 1);
            edgeCount++;
        }
    }
    inFile.close();
    
    auto readEnd = high_resolution_clock::now();
    double readTime = duration_cast<milliseconds>(readEnd - readStart).count() / 1000.0;
    
    cout << "Graph loaded in " << fixed << setprecision(3) << readTime << " seconds\n";
    cout << "Unique edges: " << edgeCount << "\n";
    
    // Compute k-core
    cout << "Computing k-core decomposition...\n";
    auto computeStart = high_resolution_clock::now();
    vector<int> coreness = kcore.computeKCore();
    auto computeEnd = high_resolution_clock::now();
    
    double computeTime = duration_cast<milliseconds>(computeEnd - computeStart).count() / 1000.0;
    long long memoryUsage = kcore.getMemoryUsage();
    
    cout << "Computation complete in " << fixed << setprecision(6) << computeTime << " seconds\n";
    
    int maxCore = kcore.getMaxKCore();
    map<int, int> dist = kcore.getCoreDistribution();
    
    cout << "Maximum k-core: " << maxCore << "\n";
    cout << "Memory usage: " << fixed << setprecision(2) << (memoryUsage / 1048576.0) << " MB\n";
    
    // Calculate metrics
    double avgDegree = (2.0 * edgeCount) / n;
    double density = (2.0 * edgeCount) / (n * (n - 1.0));
    
    // Write results
    string detailedOutput = outputDir + "/" + datasetName + "_detailed.txt";
    string csvOutput = outputDir + "/summary.csv";
    
    writeDetailedResults(detailedOutput, datasetName, n, edgeCount, maxCore, 
                        dist, computeTime, memoryUsage, coreness);
    writeCSVSummary(csvOutput, datasetName, n, edgeCount, maxCore, 
                   computeTime, memoryUsage, avgDegree, density);
    
    cout << "\nResults written to:\n";
    cout << "  - " << detailedOutput << "\n";
    cout << "  - " << csvOutput << "\n";
    
    return 0;
}
