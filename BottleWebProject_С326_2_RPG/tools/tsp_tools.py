import random
import datetime
import json

def generate_random_graph(n=None, m=None):
    if n is None:
        n = random.randint(5, 25)
    if m is None:
        m = random.randint(2, min(6, n - 1))

    k = random.randint(1, n)

    edges = set()
    edge_list = []

    # Остовное дерево — гарантирует связность
    vertices = list(range(1, n + 1))
    random.shuffle(vertices)
    for i in range(1, len(vertices)):
        u = vertices[i]
        v = vertices[random.randint(0, i - 1)]
        w = random.randint(1, 20)
        edge = (min(u, v), max(u, v))
        if edge not in edges:
            edges.add(edge)
            edge_list.append((u, v, w))

    # Выбираем достопримечательности
    candidates = [v for v in range(1, n + 1) if v != k]
    sites = random.sample(candidates, min(m, len(candidates)))

    # Гарантируем прямые рёбра между всеми ключевыми точками
    # отель + все достопримечательности → полный подграф между ними
    key_nodes = [k] + sites
    for i in range(len(key_nodes)):
        for j in range(i + 1, len(key_nodes)):
            u, v = key_nodes[i], key_nodes[j]
            edge = (min(u, v), max(u, v))
            if edge not in edges:
                edges.add(edge)
                w = random.randint(1, 20)
                edge_list.append((u, v, w))

    # Добавляем дополнительные рёбра для плотности
    extra    = random.randint(n // 2, n)
    target   = len(edge_list) + extra
    attempts = 0
    while len(edge_list) < target and attempts < extra * 5:
        u = random.randint(1, n)
        v = random.randint(1, n)
        if u != v:
            edge = (min(u, v), max(u, v))
            if edge not in edges:
                edges.add(edge)
                w = random.randint(1, 20)
                edge_list.append((u, v, w))
        attempts += 1

    return {
        'n':     str(n),
        'm':     str(m),
        'k':     str(k),
        'edges': '\n'.join(f'{u} {v} {w}' for u, v, w in edge_list),
        'sites': ' '.join(str(s) for s in sites),
    }
def log_to_file(form_data, result_data, errors=None):
    log_entry = {
        'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'input': form_data,
        'result': result_data,
        'errors': errors
    }
    with open('tsp_history.json', 'a', encoding='utf-8') as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')