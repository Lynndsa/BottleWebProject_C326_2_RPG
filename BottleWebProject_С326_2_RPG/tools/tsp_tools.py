import random


def generate_random_graph(n=None, m=None):

    if n is None:
        n = random.randint(5, 15)
    if m is None:
        m = random.randint(2, min(6, n - 1))

    # Отель — случайная вершина
    k = random.randint(1, n)

    # Строим случайный связный граф:
    # Сначала создаём остовное дерево (гарантирует связность)
    vertices = list(range(1, n + 1))
    random.shuffle(vertices)

    edges = set()
    edge_list = []

    for i in range(1, len(vertices)):
        u = vertices[i]
        v = vertices[random.randint(0, i - 1)]
        w = random.randint(1, 20)
        edge = (min(u, v), max(u, v))
        if edge not in edges:
            edges.add(edge)
            edge_list.append((u, v, w))

    # Добавляем несколько случайных рёбер для плотности
    extra = random.randint(n // 2, n)
    attempts = 0
    while len(edge_list) < len(edge_list) + extra and attempts < extra * 3:
        u = random.randint(1, n)
        v = random.randint(1, n)
        if u != v:
            edge = (min(u, v), max(u, v))
            if edge not in edges:
                edges.add(edge)
                w = random.randint(1, 20)
                edge_list.append((u, v, w))
        attempts += 1

    # Выбираем достопримечательности — любые вершины кроме отеля
    candidates = [v for v in range(1, n + 1) if v != k]
    sites = random.sample(candidates, min(m, len(candidates)))

    return {
        'n':     str(n),
        'm':     str(m),
        'k':     str(k),
        'edges': '\n'.join(f'{u} {v} {w}' for u, v, w in edge_list),
        'sites': ' '.join(str(s) for s in sites),
    }