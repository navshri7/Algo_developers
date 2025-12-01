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

class KatzCentrality {
private:
    int n;
    vector<vector<int>> adj;
    vector<double> katz;
    long long memoryUsed;
    double alpha;
    double beta;
    
public:
    KatzCentrality(int vertices, double alpha_param = -1.0) 
        : n(vertices), adj(vertices), katz(vertices, 0.0), memoryUsed(0), 
          alpha(alpha_param), beta(1.0) {
        memoryUsed = vertices * (sizeof(vector<int>) + sizeof(double));
    }
    
    void addEdge(int u, int v) {
        if (u == v) return;
        adj[u].push_back(v);
        adj[v].push_back(u);
        memoryUsed += 2 * sizeof(int);
    }
    
    double estimateSpectralRadius() {
        // Power iteration to estimate largest eigenvalue
        vector<double> x(n, 1.0 / sqrt(max(1, n)));
        vector<double> y(n);
        double lambda = 0.0;
        
        for (int it = 0; it < 1000; ++it) {
            // y = A^T * x
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
            
            // Rayleigh quotient
            double rq = 0.0;
            fill(y.begin(), y.end(), 0.0);
            for (int u = 0; u < n; ++u) {
                for (int v : adj[u]) {
                    y[v] += x[u];
                }
            }
            for (int i = 0; i < n; ++i) rq += x[i] * y[i];
            
            if (it > 0 && abs(rq - lambda) < 1e-9) {
                lambda = rq;
                break;
            }
            lambda = rq;
        }
        
        return lambda;
    }
    
    vector<double> computeKatz() {
        auto start = high_resolution_clock::now();
        
        // Estimate alpha if not provided
        if (alpha <= 0.0) {
            double lambda_max = estimateSpectralRadius();
            if (lambda_max > 0.0) {
                alpha = 0.85 / lambda_max;
            } else {
                alpha = 0.01;
            }
        }
        
        // Katz iteration: x_{t+1} = alpha * A^T * x_t + beta
        vector<double> x(n, 0.0);
        vector<double> xnext(n, 0.0);
        const int max_iter = 10000;
        const double tol = 1e-9;
        
        for (int it = 0; it < max_iter; ++it) {
            // xnext = alpha * A^T * x + beta
            fill(xnext.begin(), xnext.end(), beta);
            for (int u = 0; u < n; ++u) {
                if (x[u] != 0.0) {
                    for (int v : adj[u]) {
                        xnext[v] += alpha * x[u];
                    }
                }
            }
            
            // Check convergence
            double diff = 0.0;
            for (int i = 0; i < n; ++i) {
                double d = xnext[i] - x[i];
                diff += d * d;
            }
            diff = sqrt(diff);
            
            x.swap(xnext);
            
            if (diff < tol) break;
        }
        
        // Normalize
        double kmax = 0.0;
        for (double v : x) if (v > kmax) kmax = v;
        if (kmax > 0.0) {
            for (double &v : x) v /= kmax;
        }
        
        katz = x;
        return katz;
    }
    
    double getMaxKatz() {
        return *max_element(katz.begin(), katz.end());
    }
    
    double getAlpha() {
        return alpha;
    }
    
    long long getMemoryUsage() {
        return memoryUsed;
    }
    
    vector<double> getKatz() {
        return katz;
    }
};

void writeDetailedResults(const string& outputFile, const string& datasetName,
                         int n, int m, double maxKatz, double runtime, 
                         long long memory, double alpha, const vector<double>& katz) {
    ofstream out(outputFile);
    
    out << "Dataset: " << datasetName << "\n";
    out << "Vertices: " << n << "\n";
    out << "Edges: " << m << "\n";
    out << "Max Katz Centrality: " << fixed << setprecision(6) << maxKatz << "\n";
    out << "Alpha Parameter: " << fixed << setprecision(6) << alpha << "\n";
    out << "Runtime (seconds): " << fixed << setprecision(6) << runtime << "\n";
    out << "Memory Usage (MB): " << fixed << setprecision(2) << (memory / 1048576.0) << "\n";
    
    out << "\n=== Top 100 Vertices by Katz Centrality ===\n";
    out << "Rank\tVertex_ID\tKatz_Centrality\n";
    
    vector<pair<double, int>> ranked;
    for (int i = 0; i < n; i++) {
        ranked.push_back({katz[i], i});
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
                    int n, int m, double maxKatz, double runtime, long long memory,
                    double avgDegree, double density, double alpha) {
    bool fileExists = ifstream(csvFile).good();
    ofstream out(csvFile, ios::app);
    
    if (!fileExists) {
        out << "Dataset,Vertices,Edges,MaxKatz,Runtime_sec,Memory_MB,AvgDegree,Density,Alpha\n";
    }
    
    out << datasetName << "," << n << "," << m << "," 
        << fixed << setprecision(6) << maxKatz << ","
        << fixed << setprecision(6) << runtime << ","
        << fixed << setprecision(2) << (memory / 1048576.0) << ","
        << fixed << setprecision(4) << avgDegree << ","
        << scientific << setprecision(6) << density << ","
        << fixed << setprecision(6) << alpha << "\n";
    
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
    KatzCentrality katz(n);
    
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
            katz.addEdge(u - 1, v - 1);
            edgeCount++;
        }
    }
    inFile.close();
    
    auto readEnd = high_resolution_clock::now();
    double readTime = duration_cast<milliseconds>(readEnd - readStart).count() / 1000.0;
    
    cout << "Graph loaded in " << fixed << setprecision(3) << readTime << " seconds\n";
    cout << "Unique edges: " << edgeCount << "\n";
    
    cout << "Computing Katz centrality...\n";
    auto computeStart = high_resolution_clock::now();
    vector<double> katzVec = katz.computeKatz();
    auto computeEnd = high_resolution_clock::now();
    
    double computeTime = duration_cast<milliseconds>(computeEnd - computeStart).count() / 1000.0;
    long long memoryUsage = katz.getMemoryUsage();
    
    cout << "Computation complete in " << fixed << setprecision(6) << computeTime << " seconds\n";
    
    double maxKatz = katz.getMaxKatz();
    double alpha = katz.getAlpha();
    cout << "Maximum Katz centrality: " << fixed << setprecision(6) << maxKatz << "\n";
    cout << "Alpha parameter: " << fixed << setprecision(6) << alpha << "\n";
    cout << "Memory usage: " << fixed << setprecision(2) << (memoryUsage / 1048576.0) << " MB\n";
    
    double avgDegree = (2.0 * edgeCount) / n;
    double density = (2.0 * edgeCount) / (n * (n - 1.0));
    
    string detailedOutput = outputDir + "/" + datasetName + "_detailed.txt";
    string csvOutput = outputDir + "/summary.csv";
    
    writeDetailedResults(detailedOutput, datasetName, n, edgeCount, maxKatz,
                        computeTime, memoryUsage, alpha, katzVec);
    writeCSVSummary(csvOutput, datasetName, n, edgeCount, maxKatz,
                   computeTime, memoryUsage, avgDegree, density, alpha);
    
    cout << "\nResults written to:\n";
    cout << "  - " << detailedOutput << "\n";
    cout << "  - " << csvOutput << "\n";
    
    return 0;
}
