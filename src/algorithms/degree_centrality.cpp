#include <bits/stdc++.h>
#include <chrono>
#include <sys/resource.h>
using namespace std;

typedef long long ll;

struct DegreeResult {
    int indegree = 0;
    int outdegree = 0;
    int total = 0;
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

void computeDegreeCentrality(const string &filepath,
                             unordered_map<ll, DegreeResult> &results) {

    ifstream fin(filepath);
    if (!fin.is_open()) {
        cerr << "Error: Cannot open input file: " << filepath << endl;
        exit(1);
    }

    ll cited, citing;
    while (fin >> cited >> citing) {
        if (results.find(cited) == results.end())
            results[cited] = {0, 0, 0};
        if (results.find(citing) == results.end())
            results[citing] = {0, 0, 0};
        results[citing].outdegree++;
        results[cited].indegree++;
    }
    
    for (auto &entry : results)
        entry.second.total = entry.second.indegree + entry.second.outdegree;

    fin.close();
}

void writeToCSV(const string &filename,
                const unordered_map<ll, DegreeResult> &results) {
    ofstream fout(filename);
    if (!fout.is_open()) {
        cerr << "Error: Cannot create output file: " << filename << endl;
        exit(1);
    }

    fout << "Node,InDegree,OutDegree,TotalDegree\n";
    for (const auto &entry : results) {
        fout << entry.first << ","
             << entry.second.indegree << ","
             << entry.second.outdegree << ","
             << entry.second.total << "\n";
    }

    fout.close();
}

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
    
    fout << "Degree Centrality Analysis Results\n";
    fout << "==================================\n\n";
    fout << "Graph Statistics:\n";
    fout << "  Nodes: " << results.size() << "\n";
    fout << "  Edges: " << num_edges << "\n";
    fout << "  Runtime: " << fixed << setprecision(3) << runtime_sec << " seconds\n";
    fout << "  Peak Memory: " << fixed << setprecision(2) << memory_mb << " MB\n";
    fout << "  Runtime per Node: " << fixed << setprecision(6) << (runtime_sec / results.size()) << " ms\n";
    fout << "  Runtime per Edge: " << fixed << setprecision(6) << (runtime_sec / num_edges) << " ms\n\n";
    
    fout << "Top 10 by Total Degree:\n";
    vector<pair<int, ll>> sorted_total;
    for (const auto &p : results)
        sorted_total.push_back({p.second.total, p.first});
    sort(sorted_total.rbegin(), sorted_total.rend());
    
    for (int i = 0; i < min(10, (int)sorted_total.size()); i++) {
        fout << "  " << (i+1) << ". Node " << sorted_total[i].second 
             << ": " << sorted_total[i].first << "\n";
    }
    
    fout << "\nTop 10 by In-Degree (Citations Received):\n";
    vector<pair<int, ll>> sorted_indegree;
    for (const auto &p : results)
        sorted_indegree.push_back({p.second.indegree, p.first});
    sort(sorted_indegree.rbegin(), sorted_indegree.rend());
    
    for (int i = 0; i < min(10, (int)sorted_indegree.size()); i++) {
        fout << "  " << (i+1) << ". Node " << sorted_indegree[i].second 
             << ": " << sorted_indegree[i].first << "\n";
    }
    
    fout << "\nTop 10 by Out-Degree (Citations Made):\n";
    vector<pair<int, ll>> sorted_outdegree;
    for (const auto &p : results)
        sorted_outdegree.push_back({p.second.outdegree, p.first});
    sort(sorted_outdegree.rbegin(), sorted_outdegree.rend());
    
    for (int i = 0; i < min(10, (int)sorted_outdegree.size()); i++) {
        fout << "  " << (i+1) << ". Node " << sorted_outdegree[i].second 
             << ": " << sorted_outdegree[i].first << "\n";
    }
    
    fout.close();
}

int main(int argc, char* argv[]) {

    if (argc != 3) {
        cerr << "Usage: ./degree_centrality <input_file> <output_dir>\n";
        return 1;
    }
    
    string inputFile = argv[1];
    string outputDir = argv[2];
    
    auto start_time = chrono::high_resolution_clock::now();
    MemoryTracker mem;
    
    unordered_map<ll, DegreeResult> results;
    computeDegreeCentrality(inputFile, results);
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
    
    // Count edges
    int num_edges = 0;
    for (const auto &p : results) {
        num_edges += p.second.indegree;
    }
    
    writeDetailedResults(detailed_file, results, runtime_sec, mem.peak_memory_mb, num_edges);
    
    cerr << "Degree centrality computed successfully.\n";
    cerr << "Nodes: " << results.size() << ", Edges: " << num_edges << "\n";
    cerr << "Runtime: " << fixed << setprecision(3) << runtime_sec << " seconds\n";
    cerr << "Peak Memory: " << fixed << setprecision(2) << mem.peak_memory_mb << " MB\n";
    
    return 0;
}
