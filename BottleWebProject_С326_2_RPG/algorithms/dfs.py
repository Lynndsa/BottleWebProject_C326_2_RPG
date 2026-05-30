# -*- coding: utf-8 -*-
import random

def generate_transactions(tx_count, wallet_count):
    """Генерация случайных транзакций на сервере."""
    hex_chars = '0123456789ABCDEF'
    wallets = [''.join(random.choices(hex_chars, k=6)) for _ in range(wallet_count)]
    ts = 1_700_000_000
    lines = []
    for _ in range(tx_count):
        frm, to = random.sample(wallets, 2)
        amount = round(random.uniform(100, 10000), 2)
        ts += random.randint(10, 300)
        lines.append(f'{frm} {to} {amount} {ts}')
    return '\n'.join(lines)

def read_transactions_from_file(file_storage):
    """Читает транзакции из загруженного файла."""
    return file_storage.file.read().decode('utf-8', errors='ignore')

def run_dfs(raw_transactions, threshold):
    """
    Основной алгоритм DFS.
    Сюда потом вписывается реализация.
    Пока возвращает заглушку.
    """
    pass
