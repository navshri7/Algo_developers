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

class EigenvectorCentrality {
private:
    int n;
    vector<vector<int>> adj;
    vector<double> eigen;
    long long memoryUsed;
    double lambda;
    
public:
    EigenvectorCentrality(int vertices) 
        : n(vertices), adj(vertices), eigen(vertices, 0.0), memoryUsed(0), lambda(0.0) {
        memoryUsed = vertices * (sizeof(vector<int>) + sizeof(double));
    }
    
    void addEdge(int u, int v) {
        if (u == v) return;
        adj[u].push_back(v);
        adj[v].push_back(u);
        memoryUsed += 2 * sizeof(int);
    }
    
    vector<double> computeEigenvector() {
        // Power iteration on A^T (incoming edges)
        vector<double> x(n, 1.0 / sqrt(max(1, n)));
        vector<double> y(n);
        lambda = 0.0;
        
        const int max_iter = 10000;
        const double tol = 1e-9;
        
        for (int it = 0; it < max_iter; ++it) {
            // y = A^T * x (accumulate from incoming edges)
            fill(y.begin(), y.end(), 0.0);
            for (int u = 0; u < n; ++u) {
                for (int v : adj[u]) {
                    y[v] += x[u];
                }
            }
            
            // Normalize
            double norm = 0.0;
            for (double v : y) norm += v * v;
            norm = sqrt(norm);
            if (norm == 0.0) break;
            
            for (int i = 0; i < n; ++i) x[i] = y[i] / norm;
            
            // Rayleigh quotient for eigenvalue
            double rq = 0.0;
            fill(y.begin(), y.end(), 0.0);
            for (int u = 0; u < n; ++u) {
                for (int v : adj[u]) {
                    y[v] += x[u];
                }
            }
            for (int i = 0; i < n; ++i) rq += x[i] * y[i];
            
            if (it > 0 && abs(rq - lambda) < tol) {
                lambda = rq;
                break;
            }
            lambda = rq;
        }
        
        // Normalize to [0, 1]
        double emax = 0.0;
        for (double v : x) if (v > emax) emax = v;
        if (emax > 0.0) {
            for (double &v : x) v /= emax;
        }
        
        eigen = x;
        return eigen;
    }
    
    double getMaxEigen() {
        return *max_element(eigen.begin(), eigen.end());
    }
    
    double getLambda() {
        return lambda;
    }
    
    long long getMemoryUsage() {
        return memoryUsed;
    }
    
    vector<double> getEigen() {
        return eigen;
    }
};

void writeDetailedResults(const string& outputFile, const string& datasetName,
                         int n, int m, double maxEigen, double runtime, 
                         long long memory, double lambda, const vector<double>& eigen) {
    ofstream out(outputFile);
    
    out << "Dataset: " << datasetName << "\n";
    out << "Vertices: " << n << "\n";
    out << "Edges: " << m << "\n";
    out << "Max Eigenvector Centrality: " << fixed << setprecision(6) << maxEigen << "\n";
    out << "Largest Eigenvalue (Lambda): " << fixed << setprecision(6) << lambda << "\n";
    out << "Runtime (seconds): " << fixed << setprecision(6) << runtime << "\n";
    out << "Memory Usage (MB): " << fixed << setprecision(2) << (memory / 1048576.0) << "\n";
    
    out << "\n=== Top 100 Vertices by Eigenvector Centrality ===\n";
    out << "Rank\tVertex_ID\tEigen_Centrality\n";
    
    vector<pair<double, int>> ranked;
    for (int i = 0; i < n; i++) {
        ranked.push_back({eigen[i], i});
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
                    int n, int m, double maxEigen, double runtime, long long memory,
                    double avgDegree, double density, double lambda) {
    bool fileExists = ifstream(csvFile).good();
    ofstream out(csvFile, ios::app);
    
    if (!fileExists) {
        out << "Dataset,Vertices,Edges,MaxEigen,Runtime_sec,Memory_MB,AvgDegree,Density,Lambda\n";
    }
    
    out << datasetName << "," << n << "," << m << "," 
        << fixed << setprecision(6) << maxEigen << ","
        << fixed << setprecision(6) << runtime << ","
        << fixed << setprecision(2) << (memory / 1048576.0) << ","
        << fixed << setprecision(4) << avgDegree << ","
        << scientific << setprecision(6) << density << ","
        << fixed << setprecision(6) << lambda << "\n";
    
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
    EigenvectorCentrality eigen(n);
    
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
            eigen.addEdge(u - 1, v - 1);
            edgeCount++;
        }
    }
    inFile.close();
    
    auto readEnd = high_resolution_clock::now();
    double readTime = duration_cast<milliseconds>(readEnd - readStart).count() / 1000.0;
    
    cout << "Graph loaded in " << fixed << setprecision(3) << readTime << " seconds\n";
    cout << "Unique edges: " << edgeCount << "\n";
    
    cout << "Computing eigenvector centrality...\n";
    auto computeStart = high_resolution_clock::now();
    vector<double> eigenVec = eigen.computeEigenvector();
    auto computeEnd = high_resolution_clock::now();
    
    double computeTime = duration_cast<milliseconds>(computeEnd - computeStart).count() / 1000.0;
    long long memoryUsage = eigen.getMemoryUsage();
    
    cout << "Computation complete in " << fixed << setprecision(6) << computeTime << " seconds\n";
    
    double maxEigen = eigen.getMaxEigen();
    double lambda = eigen.getLambda();
    cout << "Maximum eigenvector centrality: " << fixed << setprecision(6) << maxEigen << "\n";
    cout << "Largest eigenvalue: " << fixed << setprecision(6) << lambda << "\n";
    cout << "Memory usage: " << fixed << setprecision(2) << (memoryUsage / 1048576.0) << " MB\n";
    
    double avgDegree = (2.0 * edgeCount) / n;
    double density = (2.0 * edgeCount) / (n * (n - 1.0));
    
    string detailedOutput = outputDir + "/" + datasetName + "_detailed.txt";
    string csvOutput = outputDir + "/summary.csv";
    
    writeDetailedResults(detailedOutput, datasetName, n, edgeCount, maxEigen,
                        computeTime, memoryUsage, lambda, eigenVec);
    writeCSVSummary(csvOutput, datasetName, n, edgeCount, maxEigen,
                   computeTime, memoryUsage, avgDegree, density, lambda);
    
    cout << "\nResults written to:\n";
    cout << "  - " << detailedOutput << "\n";
    cout << "  - " << csvOutput << "\n";
    
    return 0;
}
