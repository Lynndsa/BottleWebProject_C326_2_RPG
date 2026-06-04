import random
import string
import time


def _random_wallet(length: int = 6) -> str:
    """Генерирует случайный адрес кошелька: заглавные буквы + цифры."""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=length))


def generate_transactions(
    tx_count: int = 10,
    wallet_count: int = 6,
    base_ts: int | None = None,
    min_amount: float = 100.0,
    max_amount: float = 100_000.0,
    seed: int | None = None,
) -> list[dict]:
    """
    Генерирует список случайных транзакций в виде DAG (ориентированный граф без циклов).

    Возвращает список словарей:
        {'sender': str, 'receiver': str, 'amount': float, 'timestamp': int, 'valid': True}

    Параметры
    ---------
    tx_count     : желаемое число транзакций (может быть меньше при малом wallet_count)
    wallet_count : число уникальных кошельков-вершин (2..50)
    base_ts      : начальная временна́я метка (по умолчанию — текущее время минус случайный сдвиг)
    min_amount   : минимальная сумма перевода
    max_amount   : максимальная сумма перевода
    seed         : seed для воспроизводимости результатов
    """
    if seed is not None:
        random.seed(seed)

    wallet_count = max(2, min(wallet_count, 50))
    tx_count     = max(1, min(tx_count, 200))

    if base_ts is None:
        base_ts = int(time.time()) - random.randint(3600, 86400)

    # Генерируем уникальные адреса кошельков
    wallets: list[str] = []
    seen: set[str] = set()
    attempts = 0
    while len(wallets) < wallet_count and attempts < 10_000:
        w = _random_wallet()
        if w not in seen:
            seen.add(w)
            wallets.append(w)
        attempts += 1

    # DAG без циклов: разрешаем только рёбра i → j, где i < j по индексу кошелька
    all_edges: list[tuple[int, int]] = [
        (i, j)
        for i in range(wallet_count)
        for j in range(i + 1, wallet_count)
    ]
    random.shuffle(all_edges)
    selected_edges = all_edges[:min(tx_count, len(all_edges))]

    # Временны́е метки строго возрастают: шаг 60–600 секунд между транзакциями
    transactions: list[dict] = []
    current_ts = base_ts
    for src_idx, dst_idx in selected_edges:
        current_ts += random.randint(60, 600)
        amount = round(random.uniform(min_amount, max_amount), 2)
        transactions.append({
            'sender':    wallets[src_idx],
            'receiver':  wallets[dst_idx],
            'amount':    amount,
            'timestamp': current_ts,
            'valid':     True,
        })

    # Перемешиваем строки — алгоритм сам сортирует по timestamp
    random.shuffle(transactions)
    return transactions


def transactions_to_text(transactions: list[dict]) -> str:
    """Сериализует транзакции в текстовый формат «sender receiver amount timestamp»."""
    lines = [
        f"{tx['sender']} {tx['receiver']} {tx['amount']:.2f} {tx['timestamp']}"
        for tx in transactions
    ]
    return '\n'.join(lines)