#include <bits/stdc++.h>
using namespace std;
struct CentralityResult {
    double betweenness = 0.0;
    double bridging_coeff = 0.0;
    double bridging_centrality = 0.0;
};
void loadGraph(const string &filepath, unordered_map<long long, vector<long long>> &adj) {
    ifstream fin(filepath);
    if (!fin.is_open()) {
        cerr << "Error: Cannot open file: " << filepath << endl;
        exit(1);
    }
    long long cited, citing;
    while (fin >> cited >> citing) {
        adj[citing].push_back(cited);  
        if (!adj.count(cited)) adj[cited] = {};   
    }
    fin.close();
}
void computeBetweenness(const unordered_map<long long, vector<long long>> &adj,
                        unordered_map<long long, CentralityResult> &results) {
    vector<long long> nodes;
    for (auto &p : adj) nodes.push_back(p.first);
    for (long long s : nodes) {
        stack<long long> S;
        unordered_map<long long, vector<long long>> P;
        unordered_map<long long, double> sigma;
        unordered_map<long long, int> dist;
        queue<long long> Q;
        for (long long v : nodes) {
            P[v] = {};
            sigma[v] = 0;
            dist[v] = -1;
        }
        sigma[s] = 1;
        dist[s] = 0;
        Q.push(s);
        while (!Q.empty()) {
            long long v = Q.front(); Q.pop();
            S.push(v);
            for (long long w : adj.at(v)) {
                if (dist[w] < 0) {
                    Q.push(w);
                    dist[w] = dist[v] + 1;
                }
                if (dist[w] == dist[v] + 1) {
                    sigma[w] += sigma[v];
                    P[w].push_back(v);
                }
            }
        }
        unordered_map<long long, double> delta;
        for (long long v : nodes) delta[v] = 0;
        while (!S.empty()) {
            long long w = S.top(); S.pop();
            for (long long v : P[w])
                delta[v] += (sigma[v] / sigma[w]) * (1 + delta[w]);
            if (w != s) results[w].betweenness += delta[w];
        }
    }
}
void computeBridgingCoeff(const unordered_map<long long, vector<long long>> &adj,
                          unordered_map<long long, CentralityResult> &results) {
    unordered_map<long long, int> degree;
    for (const auto &p : adj) degree[p.first] = p.second.size();

    for (const auto &p : adj) {
        long long v = p.first;
        const auto &nbrs = p.second;
        if (degree[v] == 0 || nbrs.empty()) {
            results[v].bridging_coeff = 0;
            continue;
        }
        double numerator = 1.0 / degree[v];
        double denom = 0;
        for (long long u : nbrs)
            if (degree[u] > 0) denom += 1.0 / degree[u];

        results[v].bridging_coeff = (denom > 0) ? numerator / denom : 0;
    }
}
void finalize(unordered_map<long long, CentralityResult> &results) {
    for (auto &p : results)
        p.second.bridging_centrality = p.second.betweenness * p.second.bridging_coeff;
}
void writeToCSV(const string &filename,
                const unordered_map<long long, CentralityResult> &results) {
    ofstream fout(filename);
    if (!fout.is_open()) {
        cerr << "Error: Cannot create " << filename << endl;
        exit(1);
    }
    fout << "Node,Betweenness,BridgingCoefficient,BridgingCentrality\n";
    for (const auto &p : results)
        fout << p.first << ","
             << p.second.betweenness << ","
             << p.second.bridging_coeff << ","
             << p.second.bridging_centrality << "\n";
    fout.close();
}
int main(int argc, char *argv[]) {
    if (argc != 3) {
        cerr << "Usage: ./bridging_centrality <input_cites_file> <output_csv>\n";
        return 1;
    }
    string inputFile = argv[1];
    string outputFile = argv[2];
    unordered_map<long long, vector<long long>> adj;
    unordered_map<long long, CentralityResult> results;
    loadGraph(inputFile, adj);
    computeBetweenness(adj, results);
    computeBridgingCoeff(adj, results);
    finalize(results);
    writeToCSV(outputFile, results);
    cout << "Bridging centrality computed successfully.\n";
    cout << "Output saved to: " << outputFile << endl;
    return 0;
}