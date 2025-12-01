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

class PageRankCentrality {
private:
    int n;
    vector<vector<int>> adj;
    vector<double> pagerank;
    long long memoryUsed;
    double damping;
    double tol;
    int maxIter;

public:
    PageRankCentrality(int vertices,
                       double damping_param = 0.85,
                       double tol_param = 1e-9,
                       int max_iter_param = 10000)
        : n(vertices),
          adj(vertices),
          pagerank(vertices, 0.0),
          memoryUsed(0),
          damping(damping_param),
          tol(tol_param),
          maxIter(max_iter_param) {
        memoryUsed = vertices * (sizeof(vector<int>) + sizeof(double));
    }

    void addEdge(int u, int v) {
        if (u == v) return;
        adj[u].push_back(v);
        adj[v].push_back(u); // undirected, consistent with other algos
        memoryUsed += 2 * sizeof(int);
    }

    vector<double> computePageRank() {
        if (n == 0) return pagerank;

        vector<double> x(n, 1.0 / n);   // initial PR distribution
        vector<double> xnext(n, 0.0);

        const double d = damping;
        const double one_minus_d = 1.0 - d;

        for (int it = 0; it < maxIter; ++it) {
            // Handle dangling nodes: sum of PR of nodes with no out-links
            double danglingSum = 0.0;
            for (int i = 0; i < n; ++i) {
                if (adj[i].empty()) {
                    danglingSum += x[i];
                }
            }

            // Base value for every node: teleportation + redistributed dangling mass
            double base = one_minus_d / n + d * danglingSum / n;
            fill(xnext.begin(), xnext.end(), base);

            // Distribute PageRank along edges
            for (int u = 0; u < n; ++u) {
                int deg = (int)adj[u].size();
                if (deg == 0) continue;
                double share = d * x[u] / deg;
                for (int v : adj[u]) {
                    xnext[v] += share;
                }
            }

            // Check convergence (L1 norm of difference)
            double diff = 0.0;
            for (int i = 0; i < n; ++i) {
                diff += fabs(xnext[i] - x[i]);
            }

            x.swap(xnext);

            if (diff < tol) {
                // converged
                break;
            }
        }

        // Normalize to max = 1 (like Eigen / Katz implementations)
        double maxPR = 0.0;
        for (double v : x) if (v > maxPR) maxPR = v;
        if (maxPR > 0.0) {
            for (double &v : x) v /= maxPR;
        }

        pagerank = x;
        return pagerank;
    }

    double getMaxPageRank() const {
        return *max_element(pagerank.begin(), pagerank.end());
    }

    double getDamping() const {
        return damping;
    }

    long long getMemoryUsage() const {
        return memoryUsed;
    }

    vector<double> getPageRank() const {
        return pagerank;
    }
};

void writeDetailedResults(const string &outputFile, const string &datasetName,
                          int n, int m, double maxPR, double runtime,
                          long long memory, double damping,
                          const vector<double> &pagerank) {
    ofstream out(outputFile);

    out << "Dataset: " << datasetName << "\n";
    out << "Vertices: " << n << "\n";
    out << "Edges: " << m << "\n";
    out << "Max PageRank Centrality (normalized): " << fixed << setprecision(6) << maxPR << "\n";
    out << "Damping Factor: " << fixed << setprecision(6) << damping << "\n";
    out << "Runtime (seconds): " << fixed << setprecision(6) << runtime << "\n";
    out << "Memory Usage (MB): " << fixed << setprecision(2) << (memory / 1048576.0) << "\n";

    out << "\n=== Top 100 Vertices by PageRank Centrality ===\n";
    out << "Rank\tVertex_ID\tPageRank\n";

    vector<pair<double,int>> ranked;
    ranked.reserve(n);
    for (int i = 0; i < n; ++i) {
        ranked.push_back({pagerank[i], i});
    }
    sort(ranked.begin(), ranked.end(),
         [](const pair<double,int> &a, const pair<double,int> &b) {
             if (a.first != b.first) return a.first > b.first;
             return a.second < b.second;
         });

    int limit = min(100, (int)ranked.size());
    for (int i = 0; i < limit; ++i) {
        out << (i + 1) << "\t" << (ranked[i].second + 1) << "\t"
            << fixed << setprecision(6) << ranked[i].first << "\n";
    }

    out.close();
}

void writeCSVSummary(const string &csvFile, const string &datasetName,
                     int n, int m, double maxPR, double runtime,
                     long long memory, double avgDegree, double density,
                     double damping) {
    bool fileExists = ifstream(csvFile).good();
    ofstream out(csvFile, ios::app);

    if (!fileExists) {
        out << "Dataset,Vertices,Edges,MaxPageRank,Runtime_sec,Memory_MB,"
               "AvgDegree,Density,Damping\n";
    }

    out << datasetName << "," << n << "," << m << ","
        << fixed << setprecision(6) << maxPR << ","
        << fixed << setprecision(6) << runtime << ","
        << fixed << setprecision(2) << (memory / 1048576.0) << ","
        << fixed << setprecision(4) << avgDegree << ","
        << scientific << setprecision(6) << density << ","
        << fixed << setprecision(6) << damping << "\n";

    out.close();
}

int main(int argc, char *argv[]) {
    if (argc < 3) {
        cerr << "Usage: " << argv[0]
             << " <input_file> <output_dir> [dataset_name] [damping]\n";
        return 1;
    }

    string inputFile  = argv[1];
    string outputDir  = argv[2];
    string datasetName = (argc >= 4) ? argv[3] : inputFile;

    double damping = 0.85;
    if (argc >= 5) {
        damping = stod(argv[4]);
        if (damping <= 0.0 || damping >= 1.0) {
            cerr << "Warning: damping factor should be in (0,1). Using default 0.85.\n";
            damping = 0.85;
        }
    }

    // Create output directory if needed
    system(("mkdir -p " + outputDir).c_str());

    ifstream inFile(inputFile);
    if (!inFile) {
        cerr << "Error: Cannot open input file " << inputFile << "\n";
        return 1;
    }

    // Skip comment lines starting with '#'
    string line;
    while (getline(inFile, line)) {
        if (line.empty() || line[0] == '#') continue;
        break;
    }

    // First non-comment line should contain n m
    istringstream iss(line);
    int n, m;
    iss >> n >> m;

    cout << "Dataset: " << datasetName << "\n";
    cout << "Vertices: " << n << ", Edges: " << m << "\n";

    auto readStart = high_resolution_clock::now();
    PageRankCentrality pr(n, damping);

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
            pr.addEdge(u - 1, v - 1);
            edgeCount++;
        }
    }
    inFile.close();

    auto readEnd = high_resolution_clock::now();
    double readTime = duration_cast<milliseconds>(readEnd - readStart).count() / 1000.0;

    cout << "Graph loaded in " << fixed << setprecision(3) << readTime << " seconds\n";
    cout << "Unique edges: " << edgeCount << "\n";

    cout << "Computing PageRank centrality...\n";
    auto computeStart = high_resolution_clock::now();
    vector<double> prVec = pr.computePageRank();
    auto computeEnd = high_resolution_clock::now();

    double computeTime = duration_cast<milliseconds>(computeEnd - computeStart).count() / 1000.0;
    long long memoryUsage = pr.getMemoryUsage();

    cout << "Computation complete in " << fixed << setprecision(6) << computeTime << " seconds\n";

    double maxPR = pr.getMaxPageRank();
    cout << "Maximum PageRank (normalized): " << fixed << setprecision(6) << maxPR << "\n";
    cout << "Damping factor: " << fixed << setprecision(6) << damping << "\n";
    cout << "Memory usage: " << fixed << setprecision(2) << (memoryUsage / 1048576.0) << " MB\n";

    double avgDegree = (2.0 * edgeCount) / n;
    double density   = (2.0 * edgeCount) / (n * (n - 1.0));

    string detailedOutput = outputDir + "/" + datasetName + "_pagerank_detailed.txt";
    string csvOutput      = outputDir + "/summary_pagerank.csv";

    writeDetailedResults(detailedOutput, datasetName, n, edgeCount,
                         maxPR, computeTime, memoryUsage, damping, prVec);
    writeCSVSummary(csvOutput, datasetName, n, edgeCount,
                    maxPR, computeTime, memoryUsage, avgDegree, density, damping);

    cout << "\nResults written to:\n";
    cout << "  - " << detailedOutput << "\n";
    cout << "  - " << csvOutput << "\n";

    return 0;
}
