#include <bits/stdc++.h>
#include <chrono>
#include <sys/resource.h>
using namespace std;

typedef long long ll;

struct MemoryTracker {
    double peak_memory_mb = 0.0;
    
    void update() {
        struct rusage usage;
        getrusage(RUSAGE_SELF, &usage);
        double current_mb = usage.ru_maxrss / 1024.0;
        peak_memory_mb = max(peak_memory_mb, current_mb);
    }
};

void read_cora_edges(const string &filepath,
                     vector<ll> &nodes_out,
                     vector<vector<int>> &out_adj,
                     vector<vector<int>> &in_adj) {
    ifstream fin(filepath);
    if (!fin.is_open()) {
        cerr << "Error: cannot open file: " << filepath << endl;
        exit(1);
    }
    vector<pair<ll,ll>> edges;
    edges.reserve(6000); 
    unordered_map<ll,int> id_map; 
    vector<ll> id_list;           
    ll cited, citing;
    while (fin >> cited >> citing) {
        edges.emplace_back(citing, cited);
        if (!id_map.count(cited)) {
            int idx = (int)id_list.size();
            id_map[cited] = idx;
            id_list.push_back(cited);
        }
        if (!id_map.count(citing)) {
            int idx = (int)id_list.size();
            id_map[citing] = idx;
            id_list.push_back(citing);
        }
    }
    fin.close();
    int n = (int)id_list.size();
    out_adj.assign(n, vector<int>());
    in_adj.assign(n, vector<int>());
    for (const auto &e : edges) {
        ll uID = e.first; 
        ll vID = e.second; 
        int u = id_map[uID];
        int v = id_map[vID];
        out_adj[u].push_back(v); 
        in_adj[v].push_back(u);  
    }
    nodes_out = id_list;
}

void l2_normalize(vector<double> &v) {
    double sumsq = 0.0;
    for (double x : v) sumsq += x*x;
    double norm = sqrt(sumsq);
    if (norm > 0.0) {
        for (double &x : v) x /= norm;
    }
}

double max_abs_diff(const vector<double> &a, const vector<double> &b) {
    double mx = 0.0;
    int n = (int)a.size();
    for (int i = 0; i < n; ++i) {
        double d = fabs(a[i] - b[i]);
        if (d > mx) mx = d;
    }
    return mx;
}

void compute_hits_converge(const vector<vector<int>> &out_adj,
                           const vector<vector<int>> &in_adj,
                           double epsilon,
                           int max_iter,
                           vector<double> &hubs_out,
                           vector<double> &auths_out,
                           int &iterations_taken) {

    int n = (int)out_adj.size();
    hubs_out.assign(n, 1.0);   
    auths_out.assign(n, 1.0);  
    l2_normalize(hubs_out);
    l2_normalize(auths_out);
    vector<double> hubs_prev(n), auths_prev(n);
    vector<double> auth_new(n), hub_new(n);
    
    iterations_taken = 0;
    for (int iter = 1; iter <= max_iter; ++iter) {
        hubs_prev = hubs_out;
        auths_prev = auths_out;
        for (int v = 0; v < n; ++v) {
            double s = 0.0;
            for (int u : in_adj[v]) s += hubs_prev[u];
            auth_new[v] = s;
        }
        l2_normalize(auth_new);
        for (int u = 0; u < n; ++u) {
            double s = 0.0;
            for (int v : out_adj[u]) s += auth_new[v];
            hub_new[u] = s;
        }
        l2_normalize(hub_new);
        double diff_auth = max_abs_diff(auth_new, auths_prev);
        double diff_hub  = max_abs_diff(hub_new, hubs_prev);
        double maxdiff = max(diff_auth, diff_hub);
        auths_out = auth_new;
        hubs_out  = hub_new;
        iterations_taken = iter;
        if (maxdiff < epsilon) {
            return;
        }
    }
}

void write_hits_csv(const string &filepath,
                    const vector<ll> &index_to_node,
                    const vector<double> &hubs,
                    const vector<double> &auths) {
    ofstream fout(filepath);
    if (!fout.is_open()) {
        cerr << "Error: cannot open output file: " << filepath << endl;
        exit(1);
    }
    fout << "Node,Hub,Authority\n";
    int n = (int)index_to_node.size();
    for (int i = 0; i < n; ++i) {
        fout << index_to_node[i] << "," << fixed << setprecision(10)
             << hubs[i] << "," << auths[i] << "\n";
    }
    fout.close();
}

void write_hits_hub_csv(const string &filepath,
                        const vector<ll> &index_to_node,
                        const vector<double> &hubs) {
    ofstream fout(filepath);
    if (!fout.is_open()) {
        cerr << "Error: cannot open output file: " << filepath << endl;
        exit(1);
    }
    fout << "Node,Hub\n";
    int n = (int)index_to_node.size();
    for (int i = 0; i < n; ++i) {
        fout << index_to_node[i] << "," << fixed << setprecision(10)
             << hubs[i] << "\n";
    }
    fout.close();
}

void write_hits_authority_csv(const string &filepath,
                              const vector<ll> &index_to_node,
                              const vector<double> &auths) {
    ofstream fout(filepath);
    if (!fout.is_open()) {
        cerr << "Error: cannot open output file: " << filepath << endl;
        exit(1);
    }
    fout << "Node,Authority\n";
    int n = (int)index_to_node.size();
    for (int i = 0; i < n; ++i) {
        fout << index_to_node[i] << "," << fixed << setprecision(10)
             << auths[i] << "\n";
    }
    fout.close();
}

void writeDetailedResults(const string &filename,
                          const vector<ll> &index_to_node,
                          const vector<double> &hubs,
                          const vector<double> &auths,
                          double runtime_sec,
                          double memory_mb,
                          int num_edges,
                          int iterations_taken,
                          double epsilon,
                          int max_iter) {
    ofstream fout(filename);
    if (!fout.is_open()) {
        cerr << "Error: Cannot create " << filename << endl;
        exit(1);
    }
    
    fout << "HITS Algorithm Analysis Results\n";
    fout << "===============================\n\n";
    fout << "Graph Statistics:\n";
    fout << "  Nodes: " << index_to_node.size() << "\n";
    fout << "  Edges: " << num_edges << "\n";
    fout << "  Runtime: " << fixed << setprecision(3) << runtime_sec << " seconds\n";
    fout << "  Peak Memory: " << fixed << setprecision(2) << memory_mb << " MB\n";
    fout << "  Runtime per Node: " << fixed << setprecision(6) << (runtime_sec / index_to_node.size()) << " ms\n";
    fout << "  Runtime per Edge: " << fixed << setprecision(6) << (runtime_sec / num_edges) << " ms\n\n";
    
    fout << "Convergence Parameters:\n";
    fout << "  Epsilon: " << fixed << setprecision(10) << epsilon << "\n";
    fout << "  Max Iterations: " << max_iter << "\n";
    fout << "  Iterations Taken: " << iterations_taken << "\n\n";
    
    fout << "Top 10 by Hub Score:\n";
    vector<pair<double, ll>> sorted_hubs;
    for (int i = 0; i < (int)index_to_node.size(); i++)
        sorted_hubs.push_back({hubs[i], index_to_node[i]});
    sort(sorted_hubs.rbegin(), sorted_hubs.rend());
    
    for (int i = 0; i < min(10, (int)sorted_hubs.size()); i++) {
        fout << "  " << (i+1) << ". Node " << sorted_hubs[i].second 
             << ": " << fixed << setprecision(10) << sorted_hubs[i].first << "\n";
    }
    
    fout << "\nTop 10 by Authority Score:\n";
    vector<pair<double, ll>> sorted_auths;
    for (int i = 0; i < (int)index_to_node.size(); i++)
        sorted_auths.push_back({auths[i], index_to_node[i]});
    sort(sorted_auths.rbegin(), sorted_auths.rend());
    
    for (int i = 0; i < min(10, (int)sorted_auths.size()); i++) {
        fout << "  " << (i+1) << ". Node " << sorted_auths[i].second 
             << ": " << fixed << setprecision(10) << sorted_auths[i].first << "\n";
    }
    
    fout.close();
}

void writeDetailedHubResults(const string &filename,
                             const vector<ll> &index_to_node,
                             const vector<double> &hubs,
                             double runtime_sec,
                             double memory_mb,
                             int num_edges,
                             int iterations_taken,
                             double epsilon,
                             int max_iter) {
    ofstream fout(filename);
    if (!fout.is_open()) {
        cerr << "Error: Cannot create " << filename << endl;
        exit(1);
    }
    
    fout << "HITS Hub Score Analysis Results\n";
    fout << "===============================\n\n";
    fout << "Graph Statistics:\n";
    fout << "  Nodes: " << index_to_node.size() << "\n";
    fout << "  Edges: " << num_edges << "\n";
    fout << "  Runtime: " << fixed << setprecision(3) << runtime_sec << " seconds\n";
    fout << "  Peak Memory: " << fixed << setprecision(2) << memory_mb << " MB\n";
    fout << "  Runtime per Node: " << fixed << setprecision(6) << (runtime_sec / index_to_node.size()) << " ms\n";
    fout << "  Runtime per Edge: " << fixed << setprecision(6) << (runtime_sec / num_edges) << " ms\n\n";
    
    fout << "Convergence Parameters:\n";
    fout << "  Epsilon: " << fixed << setprecision(10) << epsilon << "\n";
    fout << "  Max Iterations: " << max_iter << "\n";
    fout << "  Iterations Taken: " << iterations_taken << "\n\n";
    
    fout << "Top 10 by Hub Score:\n";
    vector<pair<double, ll>> sorted_hubs;
    for (int i = 0; i < (int)index_to_node.size(); i++)
        sorted_hubs.push_back({hubs[i], index_to_node[i]});
    sort(sorted_hubs.rbegin(), sorted_hubs.rend());
    
    for (int i = 0; i < min(10, (int)sorted_hubs.size()); i++) {
        fout << "  " << (i+1) << ". Node " << sorted_hubs[i].second 
             << ": " << fixed << setprecision(10) << sorted_hubs[i].first << "\n";
    }
    
    fout.close();
}

void writeDetailedAuthorityResults(const string &filename,
                                   const vector<ll> &index_to_node,
                                   const vector<double> &auths,
                                   double runtime_sec,
                                   double memory_mb,
                                   int num_edges,
                                   int iterations_taken,
                                   double epsilon,
                                   int max_iter) {
    ofstream fout(filename);
    if (!fout.is_open()) {
        cerr << "Error: Cannot create " << filename << endl;
        exit(1);
    }
    
    fout << "HITS Authority Score Analysis Results\n";
    fout << "=====================================\n\n";
    fout << "Graph Statistics:\n";
    fout << "  Nodes: " << index_to_node.size() << "\n";
    fout << "  Edges: " << num_edges << "\n";
    fout << "  Runtime: " << fixed << setprecision(3) << runtime_sec << " seconds\n";
    fout << "  Peak Memory: " << fixed << setprecision(2) << memory_mb << " MB\n";
    fout << "  Runtime per Node: " << fixed << setprecision(6) << (runtime_sec / index_to_node.size()) << " ms\n";
    fout << "  Runtime per Edge: " << fixed << setprecision(6) << (runtime_sec / num_edges) << " ms\n\n";
    
    fout << "Convergence Parameters:\n";
    fout << "  Epsilon: " << fixed << setprecision(10) << epsilon << "\n";
    fout << "  Max Iterations: " << max_iter << "\n";
    fout << "  Iterations Taken: " << iterations_taken << "\n\n";
    
    fout << "Top 10 by Authority Score:\n";
    vector<pair<double, ll>> sorted_auths;
    for (int i = 0; i < (int)index_to_node.size(); i++)
        sorted_auths.push_back({auths[i], index_to_node[i]});
    sort(sorted_auths.rbegin(), sorted_auths.rend());
    
    for (int i = 0; i < min(10, (int)sorted_auths.size()); i++) {
        fout << "  " << (i+1) << ". Node " << sorted_auths[i].second 
             << ": " << fixed << setprecision(10) << sorted_auths[i].first << "\n";
    }
    
    fout.close();
}

int main(int argc, char* argv[]) {
    if (argc < 3) {
        cerr << "Usage: " << argv[0] << " <input_file> <output_dir> [epsilon] [max_iter]\n";
        return 1;
    }
    
    string inputFile = argv[1];
    string outputDir = argv[2];
    double epsilon = 1e-6;
    int max_iter = 1000;
    if (argc >= 4) epsilon = stod(argv[3]);
    if (argc >= 5) max_iter = stoi(argv[4]);
    
    auto start_time = chrono::high_resolution_clock::now();
    MemoryTracker mem;
    
    vector<ll> index_to_node;
    vector<vector<int>> out_adj, in_adj;
    read_cora_edges(inputFile, index_to_node, out_adj, in_adj);
    mem.update();
    
    int n = (int)index_to_node.size();
    if (n == 0) {
        cerr << "Error: empty graph (no nodes found).\n";
        return 1;
    }
    
    int num_edges = 0;
    for (const auto &v : out_adj) num_edges += v.size();
    
    vector<double> hubs, auths;
    int iterations_taken = 0;
    compute_hits_converge(out_adj, in_adj, epsilon, max_iter, hubs, auths, iterations_taken);
    mem.update();
    
    // Get basename from input file
    string basename = inputFile;
    size_t last_slash = basename.rfind('/');
    if (last_slash != string::npos) basename = basename.substr(last_slash + 1);
    size_t dot_pos = basename.rfind('.');
    if (dot_pos != string::npos) basename = basename.substr(0, dot_pos);
    
    string csv_file = outputDir + "/" + basename + ".csv";
    string hub_csv_file = outputDir + "/" + basename + "_hub.csv";
    string authority_csv_file = outputDir + "/" + basename + "_authority.csv";
    string detailed_file = outputDir + "/" + basename + "_detailed.txt";
    string hub_detailed_file = outputDir + "/" + basename + "_hub_detailed.txt";
    string authority_detailed_file = outputDir + "/" + basename + "_authority_detailed.txt";
    
    write_hits_csv(csv_file, index_to_node, hubs, auths);
    write_hits_hub_csv(hub_csv_file, index_to_node, hubs);
    write_hits_authority_csv(authority_csv_file, index_to_node, auths);
    
    auto end_time = chrono::high_resolution_clock::now();
    double runtime_sec = chrono::duration<double>(end_time - start_time).count();
    
    writeDetailedResults(detailed_file, index_to_node, hubs, auths, runtime_sec, 
                        mem.peak_memory_mb, num_edges, iterations_taken, epsilon, max_iter);
    writeDetailedHubResults(hub_detailed_file, index_to_node, hubs, runtime_sec,
                           mem.peak_memory_mb, num_edges, iterations_taken, epsilon, max_iter);
    writeDetailedAuthorityResults(authority_detailed_file, index_to_node, auths, runtime_sec,
                                 mem.peak_memory_mb, num_edges, iterations_taken, epsilon, max_iter);
    
    cerr << "HITS computed successfully for " << n << " nodes.\n";
    cerr << "Edges: " << num_edges << "\n";
    cerr << "Runtime: " << fixed << setprecision(3) << runtime_sec << " seconds\n";
    cerr << "Peak Memory: " << fixed << setprecision(2) << mem.peak_memory_mb << " MB\n";
    cerr << "Iterations: " << iterations_taken << "\n";
    
    return 0;
}
