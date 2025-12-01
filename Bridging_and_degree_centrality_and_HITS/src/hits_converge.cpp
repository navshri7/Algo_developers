#include <bits/stdc++.h>
using namespace std;
using ll = long long;
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
                           vector<double> &auths_out) {

    int n = (int)out_adj.size();
    hubs_out.assign(n, 1.0);   
    auths_out.assign(n, 1.0);  
    l2_normalize(hubs_out);
    l2_normalize(auths_out);
    vector<double> hubs_prev(n), auths_prev(n);
    vector<double> auth_new(n), hub_new(n);
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
int main(int argc, char* argv[]) {
    if (argc < 3) {
        cerr << "Usage: " << argv[0] << " <input_cites_file> <output_csv> [epsilon] [max_iter]\n";
        return 1;
    }
    string inputFile = argv[1];
    string outputFile = argv[2];
    double epsilon = 1e-6;
    int max_iter = 1000;
    if (argc >= 4) epsilon = stod(argv[3]);
    if (argc >= 5) max_iter = stoi(argv[4]);
    vector<ll> index_to_node;
    vector<vector<int>> out_adj, in_adj;
    read_cora_edges(inputFile, index_to_node, out_adj, in_adj);
    int n = (int)index_to_node.size();
    if (n == 0) {
        cerr << "Error: empty graph (no nodes found).\n";
        return 1;
    }
    vector<double> hubs, auths;
    compute_hits_converge(out_adj, in_adj, epsilon, max_iter, hubs, auths);
    write_hits_csv(outputFile, index_to_node, hubs, auths);
    cout << "HITS computed successfully for " << n << " nodes.\n";
    cout << "Results written to: " << outputFile << "\n";
    cout << "Parameters: epsilon=" << epsilon << " max_iter=" << max_iter << "\n";
    return 0;
}
