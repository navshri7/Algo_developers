#include <iostream>
#include <vector>
#include <queue>
#include <stack>
#include <map>
#include <algorithm>
#include <stdio.h>
#include <time.h>

using namespace std;

void display_time_elapsed(clock_t begin, clock_t finish)
{
    double duration = ((double) (finish - begin)) / CLOCKS_PER_SEC;
    printf("Elapsed time: %.3fs\n", duration);
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
    
    // Extract vertex and edge counts from first line
    fscanf(file_ptr, "%d %d\n", &vertex_count, &edge_count);
    printf("Reading graph with %d vertices and %d edges\n", vertex_count, edge_count);
    
    // Construct adjacency list representation
    map<int, vector<int>> graph;
    int largest_vertex = 0;
    
    for (int i = 0; i < edge_count; i++) {
        int node1, node2;
        fscanf(file_ptr, "%d %d\n", &node1, &node2);
        graph[node1].push_back(node2);
        graph[node2].push_back(node1);  // Undirected edge
        largest_vertex = max(largest_vertex, max(node1, node2));
    }
    fclose(file_ptr);
    
    printf("Building complete. Max vertex ID: %d\n", largest_vertex);
    
    // Setup betweenness centrality map
    map<int, float> betweenness;
    for (auto& entry : graph) {
        betweenness[entry.first] = 0;
    }
    
    begin_time = clock();
    
    int processed_nodes = 0;
    // Iterate through each node as source for BFS traversal
    for (auto& source_entry : graph) {
        int source = source_entry.first;
        processed_nodes++;
        
        if (processed_nodes % 100 == 0) {
            printf("Processing node %d/%lu\n", processed_nodes, graph.size());
        }
        
        stack<int> traversal_stack;
        map<int, int> distance;
        map<int, float> path_count;
        map<int, vector<int>> predecessors;
        queue<int> bfs_queue;
        
        // Setup initial BFS state
        for (auto& entry : graph) {
            distance[entry.first] = -1;
            path_count[entry.first] = 0;
        }
        
        path_count[source] = 1;
        distance[source] = 0;
        bfs_queue.push(source);
        
        // Execute BFS algorithm
        while (!bfs_queue.empty()) {
            int current = bfs_queue.front();
            bfs_queue.pop();
            traversal_stack.push(current);
            
            // Process all neighbors of current node
            for (int neighbor : graph[current]) {
                if (distance[neighbor] < 0) {
                    bfs_queue.push(neighbor);
                    distance[neighbor] = distance[current] + 1;
                }
                
                // Accumulate shortest paths through current node
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
        
        // Backtrack from leaf nodes to accumulate dependencies
        while (!traversal_stack.empty()) {
            int node = traversal_stack.top();
            traversal_stack.pop();
            
            for (int pred : predecessors[node]) {
                dependency[pred] += ((path_count[pred] / path_count[node]) * (1 + dependency[node]));
            }
            
            if (node != source) {
                betweenness[node] += dependency[node] / 2;
            }
        }
    }
    
    finish_time = clock();
    display_time_elapsed(begin_time, finish_time);
    
    // Determine maximum value and prepare sorted output
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
    
    printf("\nMaximum BC of graph: %.2f\n", maximum_bc);
    printf("\nTop 20 nodes by Betweenness Centrality:\n");
    printf("Rank\tNode ID\tBetweenness Centrality\n");
    printf("----\t-------\t----------------------\n");
    
    int display_count = min(20, (int)sorted_results.size());
    for (int i = 0; i < display_count; i++) {
        printf("%d\t%d\t%.2f\n", i + 1, sorted_results[i].second, sorted_results[i].first);
    }
    
    // Save complete results to output file
    FILE *output_file = fopen("betweenness_results.txt", "w");
    fprintf(output_file, "Node_ID\tBetweenness_Centrality\n");
    for (auto& result : sorted_results) {
        fprintf(output_file, "%d\t%.6f\n", result.second, result.first);
    }
    fclose(output_file);
    printf("\nFull results written to betweenness_results.txt\n");
    
    return 0;
}
