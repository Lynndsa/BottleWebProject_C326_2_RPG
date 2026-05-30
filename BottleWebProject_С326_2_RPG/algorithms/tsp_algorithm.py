import heapq
import itertools


def dijkstra(graph, start):
    distances = {vertex: float('inf') for vertex in graph}
    distances[start] = 0
    priority_queue = [(0, start)]

    while priority_queue:
        current_distance, current_vertex = heapq.heappop(priority_queue)

        if current_distance > distances[current_vertex]:
            continue

        for neighbor, weight in graph[current_vertex].items():
            distance = current_distance + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                heapq.heappush(priority_queue, (distance, neighbor))

    return distances


def solve_tsp(graph, start_node, targets):
    if not targets:
        return None, None

    nodes_of_interest = [start_node] + targets
    dist_matrix = {}
    for node in nodes_of_interest:
        dist_matrix[node] = dijkstra(graph, node)

    best_path = None
    min_total_dist = float('inf')

    for permutation in itertools.permutations(targets):
        current_path = [start_node] + list(permutation) + [start_node]
        current_dist = 0
        possible = True

        for i in range(len(current_path) - 1):
            u, v = current_path[i], current_path[i + 1]
            dist = dist_matrix[u].get(v, float('inf'))
            if dist == float('inf'):
                possible = False
                break
            current_dist += dist

        if possible and current_dist < min_total_dist:
            min_total_dist = current_dist
            best_path = current_path

    if best_path is None:
        return None, None

    return best_path, min_total_dist