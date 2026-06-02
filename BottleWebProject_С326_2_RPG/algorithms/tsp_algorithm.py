import heapq
import itertools

# Поиск кратчайшего пути между двумя конкретными вершинами с возможностью штрафа рёбер.
def dijkstra_with_path(graph, start, end, used_edges=None):
    # Инициализируем расстояния бесконечностью, а предков — None
    distances    = {vertex: float('inf') for vertex in graph}
    preprocessors = {vertex: None for vertex in graph}
    distances[start] = 0
    
    # Очередь приоритетов для Дейкстры: элементы хранятся в формате (текущее_расстояние, вершина)
    pq = [(0, start)]

    while pq:
        d, u = heapq.heappop(pq)
        
        # Если дошли до целевой вершины, досрочно завершаем поиск
        if u == end:
            break
            
        # Если нашли путь длиннее, чем уже сохранён в distances, пропускаем шаг
        if d > distances[u]:
            continue
            
        # Обходим всех соседей текущей вершины u
        for v, w in graph[u].items():
            # Если ребро уже использовалось ранее, добавляем искусственный штраф в 10 000
            penalty = 10000 if used_edges and ((u, v) in used_edges or (v, u) in used_edges) else 0
            new_dist = d + w + penalty
            
            # Релаксация ребра: если нашли более короткий путь до v, обновляем данные
            if new_dist < distances[v]:
                distances[v] = new_dist
                preprocessors[v] = u
                heapq.heappush(pq, (new_dist, v))

    # Если до целевой вершины добраться невозможно, возвращаем None
    if distances[end] == float('inf'):
        return None

    # Восстанавливаем путь в обратном порядке от конца к началу
    path = []
    curr = end
    while curr is not None:
        path.append(curr)
        curr = preprocessors[curr]
    path.reverse()  # Разворачиваем, чтобы получить путь от start к end

    # Возвращаем путь только если он корректно начинается со стартовой вершины
    return path if path and path[0] == start else None

# Строит полный, пошаговый маршрут через все контрольные точки.
def get_full_path(graph, best_path):
    if not best_path:
        return None

    full_path  = []
    used_edges = set()  # Множество для хранения уже пройденных рёбер

    # Идём по парам вершин опорного пути: (отель -> объект1), (объект1 -> объект2) и т.д.
    for i in range(len(best_path) - 1):
        segment = dijkstra_with_path(graph, best_path[i], best_path[i + 1],
                                     used_edges=used_edges)
        if segment is None:
            return None

        # Запоминаем все рёбра из найденного сегмента, чтобы оштрафовать их в будущем
        for j in range(len(segment) - 1):
            used_edges.add((segment[j], segment[j + 1]))
            used_edges.add((segment[j + 1], segment[j]))

        # Склеиваем сегменты в один общий путь.
        # Чтобы стыковочные вершины не дублировались, начиная со второго сегмента отрезаем первый элемент.
        if i == 0:
            full_path.extend(segment)
        else:
            full_path.extend(segment[1:])

    return full_path

    #Классический алгоритм Дейкстры.
def dijkstra_simple(graph, start):
    #Находит кратчайшие расстояния от стартовой вершины до абсолютно всех остальных вершин графа.
    #Используется для быстрого построения матрицы расстояний между ключевыми объектами.
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

    #Решение задачи коммивояжёра (TSP) методом полного перебора (Brute Force).
def solve_tsp(graph, start_node, targets):
    #1. Строит матрицу кратчайших расстояний между отелем и всеми достопримечательностями.
    #2. Перебирает все возможные варианты порядка обхода объектов через itertools.permutations.
    #3. Выбирает маршрут с минимальной суммарной длиной.
    if not targets:
        return None, None

    # Формируем список всех важных для нас вершин: отель + достопримечательности
    nodes_of_interest = [start_node] + targets
    
    # Строим матрицу расстояний: для каждой важной вершины запускаем Дейкстру
    dist_matrix = {node: dijkstra_simple(graph, node) for node in nodes_of_interest}

    best_key_path  = None
    min_total_dist = float('inf')

    # Полный перебор всех возможных перестановок (порядков обхода) достопримечательностей
    for permutation in itertools.permutations(targets):
        # Собираем закольцованный опорный путь: Отель -> Перестановка мест -> Отель
        path = [start_node] + list(permutation) + [start_node]
        current_dist = 0
        is_possible  = True

        # Считаем суммарную длину получившегося опорного пути по матрице расстояний
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            d = dist_matrix[u].get(v, float('inf'))
            
            # Если пути между какими-то двумя точками в графе вообще нет, этот вариант отпадает
            if d == float('inf'):
                is_possible = False
                break
            current_dist += d

        # Если путь физически возможен и он короче, чем лучший найденный ранее — запоминаем его
        if is_possible and current_dist < min_total_dist:
            min_total_dist = current_dist
            best_key_path  = path

    # Возвращаем кортеж: (лучший опорный путь, минимальная дистанция)
    return (best_key_path, min_total_dist) if best_key_path else (None, None)