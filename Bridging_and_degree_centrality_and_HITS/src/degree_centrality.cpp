#include <bits/stdc++.h>
using namespace std;
struct DegreeResult {
    int indegree;
    int outdegree;
    int total;
};
void computeDegreeCentrality(const string &filepath,
                             unordered_map<long long, DegreeResult> &results) {

    ifstream fin(filepath);
    if (!fin.is_open()) {
        cerr << "Error: Cannot open input file: " << filepath << endl;
        exit(1);
    }

    long long cited, citing;
    while (fin >> cited >> citing) {
        if (results.find(cited) == results.end())
            results[cited] = {0,0,0};
        if (results.find(citing) == results.end())
            results[citing] = {0,0,0};
        results[citing].outdegree++;
        results[cited].indegree++;
    }
    for (auto &entry : results)
        entry.second.total = entry.second.indegree + entry.second.outdegree;

    fin.close();
}
void writeToCSV(const string &filename,
                const unordered_map<long long, DegreeResult> &results) {
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
int main(int argc, char* argv[]) {

    if (argc != 3) {
        cerr << "Usage: ./degree_centrality <input_cites_file> <output_csv>\n";
        return 1;
    }
    string inputFile = argv[1];
    string outputFile = argv[2];
    unordered_map<long long, DegreeResult> results;
    computeDegreeCentrality(inputFile, results);
    writeToCSV(outputFile, results);
    cout << "Degree centrality computed successfully.\n";
    cout << "Output written to: " << outputFile << endl;
    return 0;
}
