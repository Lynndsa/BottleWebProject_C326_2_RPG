"""
dfs_algorithm.py — DFS-анализ графа финансовых транзакций.

Задача (Вариант 3): найти ОДИН самый длинный путь без циклов
(максимальная по числу рёбер последовательность переводов).
При равной длине побеждает путь с максимальной суммой.
Путь помечается подозрительным, если его длина >= threshold.
"""

from collections import defaultdict


Transaction = dict
PathResult  = dict


# ---------------------------------------------------------------------------
# Построение графа
# ---------------------------------------------------------------------------

def build_graph(transactions: list[Transaction]) -> dict[str, list[tuple]]:
    """
    Список смежности: adj[sender] = [(receiver, amount, timestamp), ...]
    Рёбра каждой вершины отсортированы по возрастанию timestamp.
    """
    adj: dict[str, list[tuple]] = defaultdict(list)
    for tx in transactions:
        adj[tx['sender']].append((
            tx['receiver'],
            float(tx['amount']),
            int(tx['timestamp']),
        ))
    for node in adj:
        adj[node].sort(key=lambda x: x[2])
    return dict(adj)


def get_all_nodes(transactions: list[Transaction]) -> set[str]:
    nodes = set()
    for tx in transactions:
        nodes.add(tx['sender'])
        nodes.add(tx['receiver'])
    return nodes


# ---------------------------------------------------------------------------
# DFS — поиск ОДНОГО самого длинного пути
# ---------------------------------------------------------------------------

def _dfs(
    node: str,
    adj: dict[str, list[tuple]],
    visited: set[str],
    path_nodes: list[str],
    path_edges: list[dict],
    last_ts: int,
    best: list,          # best[0] = лучший PathResult на данный момент
) -> None:
    """
    Рекурсивный DFS с backtracking.
    Обновляет best[0] если текущий путь длиннее (или длиннее по сумме при равной длине).
    """
    neighbors = adj.get(node, [])
    has_valid_neighbor = False

    for (receiver, amount, ts) in neighbors:
        if receiver in visited:
            continue
        if ts <= last_ts:
            continue  # нарушение хронологии

        has_valid_neighbor = True
        visited.add(receiver)
        path_nodes.append(receiver)
        path_edges.append({
            'sender':    node,
            'receiver':  receiver,
            'amount':    amount,
            'timestamp': ts,
        })

        _dfs(receiver, adj, visited, path_nodes, path_edges, ts, best)

        # Backtracking
        path_nodes.pop()
        path_edges.pop()
        visited.discard(receiver)

    # Тупик — нет продолжений. Фиксируем путь если в нём есть хоть одно ребро.
    if not has_valid_neighbor and path_edges:
        total_amount = sum(e['amount'] for e in path_edges)
        current: PathResult = {
            'nodes':        list(path_nodes),
            'edges':        list(path_edges),
            'edge_count':   len(path_edges),
            'total_amount': round(total_amount, 2),
            'start_ts':     path_edges[0]['timestamp'],
            'end_ts':       path_edges[-1]['timestamp'],
        }
        # Сравниваем с лучшим: приоритет — длина, тай-брейк — сумма
        if best[0] is None:
            best[0] = current
        else:
            prev = best[0]
            if (current['edge_count'] > prev['edge_count'] or
                (current['edge_count'] == prev['edge_count'] and
                 current['total_amount'] > prev['total_amount'])):
                best[0] = current


def find_longest_path(
    transactions: list[Transaction],
    threshold: int = 4,
) -> dict:
    """
    Главная функция: находит ОДИН самый длинный бесцикловый путь в графе.

    Возвращает dict:
    {
        'path':             PathResult | None,   # единственный лучший путь
        'paths':            [PathResult] | [],   # список из одного пути (для совместимости с шаблоном)
        'total_tx':         int,
        'total_wallets':    int,
        'max_chain_len':    int,
        'suspicious_count': int,
        'threshold':        int,
        'transactions':     list[dict],
    }
    """
    if not transactions:
        return _empty_result(threshold)

    adj   = build_graph(transactions)
    nodes = get_all_nodes(transactions)

    best: list = [None]   # изменяемый контейнер для передачи в рекурсию

    # Запускаем DFS из КАЖДОЙ вершины — ищем глобальный максимум
    for start in nodes:
        visited = {start}
        _dfs(
            node=start,
            adj=adj,
            visited=visited,
            path_nodes=[start],
            path_edges=[],
            last_ts=-1,
            best=best,
        )

    longest: PathResult | None = best[0]

    # Помечаем подозрительным
    suspicious_edges: set[tuple] = set()
    if longest is not None:
        longest['is_suspicious'] = longest['edge_count'] >= threshold
        if longest['is_suspicious']:
            for e in longest['edges']:
                suspicious_edges.add((e['sender'], e['receiver'], e['timestamp']))
    
    max_len   = longest['edge_count'] if longest else 0
    sus_count = 1 if (longest and longest['is_suspicious']) else 0
    paths     = [longest] if longest else []

    # Таблица транзакций с пометкой
    tx_table = []
    for tx in transactions:
        key = (tx['sender'], tx['receiver'], int(tx['timestamp']))
        tx_table.append({
            'sender':             tx['sender'],
            'receiver':           tx['receiver'],
            'amount':             f"{float(tx['amount']):,.2f}",
            'timestamp':          tx['timestamp'],
            'in_suspicious_path': key in suspicious_edges,
        })

    return {
        'path':             longest,
        'paths':            paths,
        'total_tx':         len(transactions),
        'total_wallets':    len(nodes),
        'max_chain_len':    max_len,
        'suspicious_count': sus_count,
        'threshold':        threshold,
        'transactions':     tx_table,
    }


# Алиас для обратной совместимости с контроллером
find_all_max_paths = find_longest_path


def _empty_result(threshold: int) -> dict:
    return {
        'path':             None,
        'paths':            [],
        'total_tx':         0,
        'total_wallets':    0,
        'max_chain_len':    0,
        'suspicious_count': 0,
        'threshold':        threshold,
        'transactions':     [],
    }