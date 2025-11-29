#include <iostream>
#include <vector>
#include <queue>
#include <stack>
#include <map>
#include <algorithm>
#include <stdio.h>
#include <time.h>
#include <cstdlib>
#include <cmath>

using namespace std;

void display_time_elapsed(clock_t begin, clock_t finish)
{
    double duration = ((double) (finish - begin)) / CLOCKS_PER_SEC;
    printf("Elapsed time: %.3fs\n", duration);
}

// Determine number of samples needed for target accuracy
int compute_sample_count(int total_nodes, double eps = 0.1, double conf = 0.1) {
    double constant = 0.5;
    int samples = (int)ceil((constant / (eps * eps)) * log(total_nodes / conf));
    return min(samples, total_nodes); // Cap at total node count
}

int main(int argc, char const *argv[])
{
    FILE *file_ptr = fopen("cit-DBLP.edges", "r");
    if (!file_ptr) {
        printf("Error: Could not open cit-DBLP.edges\n");
        return 1;
    }
    
    clock_t begin_time, finish_time;
    int vertex_count, edge_count;
    
    // Extract graph size from header
    fscanf(file_ptr, "%d %d\n", &vertex_count, &edge_count);
    printf("Reading graph with %d vertices and %d edges\n", vertex_count, edge_count);
    
    // Construct adjacency list representation
    map<int, vector<int>> graph;
    vector<int> vertex_list;
    int largest_vertex = 0;
    
    for (int i = 0; i < edge_count; i++) {
        int node1, node2;
        fscanf(file_ptr, "%d %d\n", &node1, &node2);
        
        if (graph.find(node1) == graph.end()) {
            vertex_list.push_back(node1);
        }
        if (graph.find(node2) == graph.end()) {
            vertex_list.push_back(node2);
        }
        
        graph[node1].push_back(node2);
        graph[node2].push_back(node1);  // Undirected edge
        largest_vertex = max(largest_vertex, max(node1, node2));
    }
    fclose(file_ptr);
    
    printf("Building complete. Max vertex ID: %d, Total nodes: %lu\n", 
           largest_vertex, graph.size());
    
    // Determine sampling strategy
    int total_nodes = graph.size();
    int num_samples = compute_sample_count(total_nodes, 0.1, 0.1);
    
    // Override with command line argument if provided
    if (argc > 1) {
        num_samples = atoi(argv[1]);
    } else {
        // Default: use larger of calculated or 10% of nodes
        num_samples = max(num_samples, total_nodes / 10);
    }
    num_samples = min(num_samples, total_nodes); // Ensure within bounds
    
    printf("Using sampling approach: %d samples out of %d nodes (%.2f%%)\n", 
           num_samples, total_nodes, (100.0 * num_samples) / total_nodes);
    
    // Setup betweenness centrality storage
    map<int, float> betweenness;
    for (auto& entry : graph) {
        betweenness[entry.first] = 0;
    }
    
    // Perform random sampling with fixed seed
    srand(42);
    vector<int> selected_samples;
    
    // Sample without replacement
    vector<int> available_vertices = vertex_list;
    for (int i = 0; i < num_samples; i++) {
        int random_idx = rand() % available_vertices.size();
        selected_samples.push_back(available_vertices[random_idx]);
        available_vertices.erase(available_vertices.begin() + random_idx);
    }
    
    begin_time = clock();
    
    // Calculate scaling multiplier for approximation
    float scaling_multiplier = (float)total_nodes / (float)num_samples;
    
    // Process each sampled node with BFS
    for (int sample_idx = 0; sample_idx < num_samples; sample_idx++) {
        int source = selected_samples[sample_idx];
        
        if ((sample_idx + 1) % 100 == 0) {
            printf("Processing sample %d/%d (node %d)\n", sample_idx + 1, num_samples, source);
        }
        
        stack<int> traversal_stack;
        map<int, int> distance;
        map<int, float> path_count;
        map<int, vector<int>> predecessors;
        queue<int> bfs_queue;
        
        // Setup initial state for BFS
        for (auto& entry : graph) {
            distance[entry.first] = -1;
            path_count[entry.first] = 0;
        }
        
        path_count[source] = 1;
        distance[source] = 0;
        bfs_queue.push(source);
        
        // Execute breadth-first search
        while (!bfs_queue.empty()) {
            int current = bfs_queue.front();
            bfs_queue.pop();
            traversal_stack.push(current);
            
            // Process all adjacent nodes
            for (int neighbor : graph[current]) {
                if (distance[neighbor] < 0) {
                    bfs_queue.push(neighbor);
                    distance[neighbor] = distance[current] + 1;
                }
                
                // Accumulate shortest paths if neighbor is one hop away
                if (distance[neighbor] == distance[current] + 1) {
                    path_count[neighbor] = path_count[neighbor] + path_count[current];
                    predecessors[neighbor].push_back(current);
                }
            }
        }
        
        map<int, float> dependency;
        for (auto& entry : graph) {
            dependency[entry.first] = 0;
        }
        
        // Backtrack from leaves to compute dependencies
        while (!traversal_stack.empty()) {
            int node = traversal_stack.top();
            traversal_stack.pop();
            
            for (int pred : predecessors[node]) {
                dependency[pred] += ((path_count[pred] / path_count[node]) * (1 + dependency[node]));
            }
            
            if (node != source) {
                // Apply scaling factor for sampling approximation
                betweenness[node] += (dependency[node] / 2) * scaling_multiplier;
            }
        }
    }
    
    finish_time = clock();
    display_time_elapsed(begin_time, finish_time);
    
    // Prepare sorted results and find maximum
    vector<pair<float, int>> sorted_results;
    float maximum_bc = -1;
    
    for (auto& entry : betweenness) {
        sorted_results.push_back({entry.second, entry.first});
        if (entry.second > maximum_bc) {
            maximum_bc = entry.second;
        }
    }
    
    // Sort results in descending order
    sort(sorted_results.rbegin(), sorted_results.rend());
    
    printf("\n=== APPROXIMATE BETWEENNESS CENTRALITY RESULTS ===\n");
    printf("Maximum BC: %.2f\n", maximum_bc);
    printf("Samples used: %d/%d (%.2f%% of graph)\n", 
           num_samples, total_nodes, (100.0 * num_samples) / total_nodes);
    
    printf("\nTop 20 nodes by Betweenness Centrality:\n");
    printf("Rank\tNode ID\tBetweenness Centrality\n");
    printf("----\t-------\t----------------------\n");
    
    int display_count = min(20, (int)sorted_results.size());
    for (int i = 0; i < display_count; i++) {
        printf("%d\t%d\t%.2f\n", i + 1, sorted_results[i].second, sorted_results[i].first);
    }
    
    // Compute statistical measures
    float total_sum = 0, squared_sum = 0;
    for (auto& entry : betweenness) {
        total_sum += entry.second;
        squared_sum += entry.second * entry.second;
    }
    float avg_bc = total_sum / total_nodes;
    float var = (squared_sum / total_nodes) - (avg_bc * avg_bc);
    float std_deviation = sqrt(var);
    
    printf("\nStatistics:\n");
    printf("Mean BC: %.2f\n", avg_bc);
    printf("Std Dev: %.2f\n", std_deviation);
    
    // Save complete results to output file
    FILE *output_file = fopen("betweenness_results_approx.txt", "w");
    fprintf(output_file, "Node_ID\tBetweenness_Centrality\tRank\n");
    for (int i = 0; i < sorted_results.size(); i++) {
        fprintf(output_file, "%d\t%.6f\t%d\n", sorted_results[i].second, sorted_results[i].first, i + 1);
    }
    fclose(output_file);
    printf("\nFull results written to betweenness_results_approx.txt\n");
    
    return 0;
}
