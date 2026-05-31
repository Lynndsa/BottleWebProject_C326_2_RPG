import heapq
import itertools


def dijkstra_with_path(graph, start, end, used_edges=None):
    distances    = {vertex: float('inf') for vertex in graph}
    predecessors = {vertex: None for vertex in graph}
    distances[start] = 0
    pq = [(0, start)]

    while pq:
        d, u = heapq.heappop(pq)
        if u == end:
            break
        if d > distances[u]:
            continue
        for v, w in graph[u].items():
            # Штрафуем уже использованные рёбра — но не запрещаем полностью
            penalty = 10000 if used_edges and ((u, v) in used_edges or (v, u) in used_edges) else 0
            new_dist = d + w + penalty
            if new_dist < distances[v]:
                distances[v] = new_dist
                predecessors[v] = u
                heapq.heappush(pq, (new_dist, v))

    if distances[end] == float('inf'):
        return None

    path = []
    curr = end
    while curr is not None:
        path.append(curr)
        curr = predecessors[curr]
    path.reverse()

    return path if path and path[0] == start else None


def get_full_path(graph, best_path):
    if not best_path:
        return None

    full_path  = []
    used_edges = set()

    for i in range(len(best_path) - 1):
        segment = dijkstra_with_path(graph, best_path[i], best_path[i + 1],
                                     used_edges=used_edges)
        if segment is None:
            return None

        # Запоминаем использованные рёбра
        for j in range(len(segment) - 1):
            used_edges.add((segment[j], segment[j + 1]))
            used_edges.add((segment[j + 1], segment[j]))

        if i == 0:
            full_path.extend(segment)
        else:
            full_path.extend(segment[1:])

    return full_path


def dijkstra_simple(graph, start):
    distances = {vertex: float('inf') for vertex in graph}
    distances[start] = 0
    pq = [(0, start)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > distances[u]:
            continue
        for v, w in graph[u].items():
            if distances[u] + w < distances[v]:
                distances[v] = distances[u] + w
                heapq.heappush(pq, (distances[v], v))
    return distances


def solve_tsp(graph, start_node, targets):
    if not targets:
        return None, None

    nodes_of_interest = [start_node] + targets
    dist_matrix = {node: dijkstra_simple(graph, node) for node in nodes_of_interest}

    best_key_path  = None
    min_total_dist = float('inf')

    for permutation in itertools.permutations(targets):
        path = [start_node] + list(permutation) + [start_node]
        current_dist = 0
        is_possible  = True

        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            d = dist_matrix[u].get(v, float('inf'))
            if d == float('inf'):
                is_possible = False
                break
            current_dist += d

        if is_possible and current_dist < min_total_dist:
            min_total_dist = current_dist
            best_key_path  = path

    return (best_key_path, min_total_dist) if best_key_path else (None, None)