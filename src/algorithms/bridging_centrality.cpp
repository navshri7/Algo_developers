#include <bits/stdc++.h>
#include <chrono>
#include <sys/resource.h>
using namespace std;

typedef long long ll;

struct CentralityResult {
    double betweenness = 0.0;
    double bridging_coeff = 0.0;
    double bridging_centrality = 0.0;
};

struct MemoryTracker {
    double peak_memory_mb = 0.0;
    
    void update() {
        struct rusage usage;
        getrusage(RUSAGE_SELF, &usage);
        double current_mb = usage.ru_maxrss / 1024.0;
        peak_memory_mb = max(peak_memory_mb, current_mb);
    }
};

void loadGraph(const string &filepath, unordered_map<ll, vector<ll>> &adj) {
    ifstream fin(filepath);
    if (!fin.is_open()) {
        cerr << "Error: Cannot open file: " << filepath << endl;
        exit(1);
    }
    ll cited, citing;
    while (fin >> cited >> citing) {
        adj[citing].push_back(cited);  
        if (!adj.count(cited)) adj[cited] = {};   
    }
    fin.close();
}

void computeBetweenness(const unordered_map<ll, vector<ll>> &adj,
                        unordered_map<ll, CentralityResult> &results) {
    vector<ll> nodes;
    for (auto &p : adj) nodes.push_back(p.first);
    
    for (ll s : nodes) {
        stack<ll> S;
        unordered_map<ll, vector<ll>> P;
        unordered_map<ll, double> sigma;
        unordered_map<ll, int> dist;
        queue<ll> Q;
        
        for (ll v : nodes) {
            P[v] = {};
            sigma[v] = 0;
            dist[v] = -1;
        }
        
        sigma[s] = 1;
        dist[s] = 0;
        Q.push(s);
        
        while (!Q.empty()) {
            ll v = Q.front(); Q.pop();
            S.push(v);
            for (ll w : adj.at(v)) {
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
        
        unordered_map<ll, double> delta;
        for (ll v : nodes) delta[v] = 0;
        
        while (!S.empty()) {
            ll w = S.top(); S.pop();
            for (ll v : P[w])
                delta[v] += (sigma[v] / sigma[w]) * (1 + delta[w]);
            if (w != s) results[w].betweenness += delta[w];
        }
    }
    
    // FIXED: Normalize betweenness centrality
    int n = nodes.size();
    if (n > 2) {
        double normalizer = (n - 1) * (n - 2);
        for (auto &p : results) {
            p.second.betweenness /= normalizer;
        }
    }
}

void computeBridgingCoeff(const unordered_map<ll, vector<ll>> &adj,
                          unordered_map<ll, CentralityResult> &results) {
    unordered_map<ll, int> degree;
    for (const auto &p : adj) degree[p.first] = p.second.size();

    for (const auto &p : adj) {
        ll v = p.first;
        const auto &nbrs = p.second;
        if (degree[v] == 0 || nbrs.empty()) {
            results[v].bridging_coeff = 0;
            continue;
        }
        
        // FIXED: Changed from division to multiplication
        double sum_inverse_deg = 0;
        for (ll u : nbrs)
            if (degree[u] > 0) sum_inverse_deg += 1.0 / degree[u];

        // Correct formula: (1/degree[v]) * sum(1/degree[neighbors])
        results[v].bridging_coeff = (1.0 / degree[v]) * sum_inverse_deg;
    }
}

void finalize(unordered_map<ll, CentralityResult> &results) {
    for (auto &p : results)
        p.second.bridging_centrality = p.second.betweenness * p.second.bridging_coeff;
}

void writeToCSV(const string &filename,
                const unordered_map<ll, CentralityResult> &results) {
    ofstream fout(filename);
    if (!fout.is_open()) {
        cerr << "Error: Cannot create " << filename << endl;
        exit(1);
    }
    fout << "Node,Betweenness,BridgingCoefficient,BridgingCentrality\n";
    for (const auto &p : results)
        fout << p.first << ","
             << fixed << setprecision(10)
             << p.second.betweenness << ","
             << p.second.bridging_coeff << ","
             << p.second.bridging_centrality << "\n";
    fout.close();
}

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
    
    fout << "Bridging Centrality Analysis Results\n";
    fout << "====================================\n\n";
    fout << "Graph Statistics:\n";
    fout << "  Nodes: " << num_nodes << "\n";
    fout << "  Edges: " << num_edges << "\n";
    fout << "  Runtime: " << fixed << setprecision(3) << runtime_sec << " seconds\n";
    fout << "  Peak Memory: " << fixed << setprecision(2) << memory_mb << " MB\n";
    fout << "  Runtime per Node: " << fixed << setprecision(6) << (runtime_sec / num_nodes) << " ms\n";
    fout << "  Runtime per Edge: " << fixed << setprecision(6) << (runtime_sec / num_edges) << " ms\n\n";
    
    fout << "Top 10 by Bridging Centrality:\n";
    vector<pair<double, ll>> sorted_bridging;
    for (const auto &p : results)
        sorted_bridging.push_back({p.second.bridging_centrality, p.first});
    sort(sorted_bridging.rbegin(), sorted_bridging.rend());
    
    for (int i = 0; i < min(10, (int)sorted_bridging.size()); i++) {
        fout << "  " << (i+1) << ". Node " << sorted_bridging[i].second 
             << ": " << fixed << setprecision(10) << sorted_bridging[i].first << "\n";
    }
    
    fout << "\nTop 10 by Betweenness:\n";
    vector<pair<double, ll>> sorted_betweenness;
    for (const auto &p : results)
        sorted_betweenness.push_back({p.second.betweenness, p.first});
    sort(sorted_betweenness.rbegin(), sorted_betweenness.rend());
    
    for (int i = 0; i < min(10, (int)sorted_betweenness.size()); i++) {
        fout << "  " << (i+1) << ". Node " << sorted_betweenness[i].second 
             << ": " << fixed << setprecision(10) << sorted_betweenness[i].first << "\n";
    }
    
    fout << "\nTop 10 by Bridging Coefficient:\n";
    vector<pair<double, ll>> sorted_coeff;
    for (const auto &p : results)
        sorted_coeff.push_back({p.second.bridging_coeff, p.first});
    sort(sorted_coeff.rbegin(), sorted_coeff.rend());
    
    for (int i = 0; i < min(10, (int)sorted_coeff.size()); i++) {
        fout << "  " << (i+1) << ". Node " << sorted_coeff[i].second 
             << ": " << fixed << setprecision(10) << sorted_coeff[i].first << "\n";
    }
    
    fout.close();
}

int main(int argc, char *argv[]) {
    if (argc != 3) {
        cerr << "Usage: ./bridging_centrality <input_file> <output_dir>\n";
        return 1;
    }
    
    string inputFile = argv[1];
    string outputDir = argv[2];
    
    auto start_time = chrono::high_resolution_clock::now();
    MemoryTracker mem;
    
    unordered_map<ll, vector<ll>> adj;
    unordered_map<ll, CentralityResult> results;
    
    loadGraph(inputFile, adj);
    mem.update();
    
    int num_nodes = adj.size();
    int num_edges = 0;
    for (const auto &p : adj) num_edges += p.second.size();
    
    computeBetweenness(adj, results);
    mem.update();
    
    computeBridgingCoeff(adj, results);
    mem.update();
    
    finalize(results);
    mem.update();
    
    // Get basename from input file
    string basename = inputFile;
    size_t last_slash = basename.rfind('/');
    if (last_slash != string::npos) basename = basename.substr(last_slash + 1);
    size_t dot_pos = basename.rfind('.');
    if (dot_pos != string::npos) basename = basename.substr(0, dot_pos);
    
    string csv_file = outputDir + "/" + basename + ".csv";
    string detailed_file = outputDir + "/" + basename + "_detailed.txt";
    
    writeToCSV(csv_file, results);
    
    auto end_time = chrono::high_resolution_clock::now();
    double runtime_sec = chrono::duration<double>(end_time - start_time).count();
    
    writeDetailedResults(detailed_file, results, runtime_sec, mem.peak_memory_mb, num_nodes, num_edges);
    
    cerr << "Bridging centrality computed successfully.\n";
    cerr << "Nodes: " << num_nodes << ", Edges: " << num_edges << "\n";
    cerr << "Runtime: " << fixed << setprecision(3) << runtime_sec << " seconds\n";
    cerr << "Peak Memory: " << fixed << setprecision(2) << mem.peak_memory_mb << " MB\n";
    
    return 0;
}