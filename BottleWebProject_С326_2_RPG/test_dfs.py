"""
Модульные тесты для варианта DFS (поиск в глубину).
Покрывают: dfs_algorithm.py и validators/dfs_validator.py
"""

import sys
import os
import unittest

# Добавляем корень проекта в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from algorithms.dfs_algorithm import (
    build_graph,
    get_all_nodes,
    find_longest_path,
)
from validators.dfs_validator import (
    parse_transactions,
    validate_params,
    filter_valid,
)


# ─────────────────────────────────────────────
#  Вспомогательные данные
# ─────────────────────────────────────────────

def make_tx(sender, receiver, amount=100.0, timestamp=1):
    return {'sender': sender, 'receiver': receiver,
            'amount': amount, 'timestamp': timestamp}


# ─────────────────────────────────────────────
#  1. Тесты build_graph
# ─────────────────────────────────────────────

class TestBuildGraph(unittest.TestCase):

    def test_single_transaction(self):
        """Граф из одной транзакции содержит одно ребро."""
        txs = [make_tx('A', 'B', 50.0, 1)]
        g = build_graph(txs)
        self.assertIn('A', g)
        self.assertEqual(len(g['A']), 1)
        receiver, amount, ts = g['A'][0]
        self.assertEqual(receiver, 'B')
        self.assertAlmostEqual(amount, 50.0)
        self.assertEqual(ts, 1)

    def test_multiple_edges_sorted_by_timestamp(self):
        """Рёбра из одной вершины сортируются по временной метке."""
        txs = [
            make_tx('A', 'C', 10.0, 30),
            make_tx('A', 'B', 20.0, 10),
            make_tx('A', 'D', 30.0, 20),
        ]
        g = build_graph(txs)
        timestamps = [e[2] for e in g['A']]
        self.assertEqual(timestamps, sorted(timestamps))

    def test_no_transactions_returns_empty(self):
        """Пустой список транзакций → пустой граф."""
        g = build_graph([])
        self.assertEqual(g, {})

    def test_receiver_not_in_adjacency_if_no_outgoing(self):
        """Вершина, у которой нет исходящих, не создаёт ключ в словаре."""
        txs = [make_tx('A', 'B')]
        g = build_graph(txs)
        self.assertNotIn('B', g)


# ─────────────────────────────────────────────
#  2. Тесты get_all_nodes
# ─────────────────────────────────────────────

class TestGetAllNodes(unittest.TestCase):

    def test_basic_nodes(self):
        txs = [make_tx('A', 'B'), make_tx('B', 'C')]
        nodes = get_all_nodes(txs)
        self.assertEqual(nodes, {'A', 'B', 'C'})

    def test_no_transactions(self):
        nodes = get_all_nodes([])
        self.assertEqual(nodes, set())

    def test_duplicate_nodes_counted_once(self):
        txs = [make_tx('A', 'B'), make_tx('A', 'C'), make_tx('B', 'C')]
        nodes = get_all_nodes(txs)
        self.assertEqual(nodes, {'A', 'B', 'C'})


# ─────────────────────────────────────────────
#  3. Тесты find_longest_path — основная логика DFS
# ─────────────────────────────────────────────

class TestFindLongestPath(unittest.TestCase):

    # ── 3.1 Граничные случаи ──────────────────

    def test_empty_transactions_returns_empty_result(self):
        """Пустой список → нулевой результат, без ошибок."""
        res = find_longest_path([])
        self.assertIsNone(res['path'])
        self.assertEqual(res['max_chain_len'], 0)
        self.assertEqual(res['suspicious_count'], 0)
        self.assertEqual(res['total_tx'], 0)

    def test_single_transaction_chain_length_1(self):
        """Одна транзакция образует цепочку длиной 1."""
        txs = [make_tx('A', 'B', 100.0, 1)]
        res = find_longest_path(txs)
        self.assertEqual(res['max_chain_len'], 1)
        self.assertIsNotNone(res['path'])

    def test_self_loop_does_not_crash(self):
        """Если вдруг передать A→A — алгоритм не падает."""
        txs = [{'sender': 'A', 'receiver': 'A', 'amount': 10.0, 'timestamp': 1}]
        # DFS пропустит A→A (receiver в visited), результат — пусто
        res = find_longest_path(txs)
        self.assertEqual(res['max_chain_len'], 0)

    # ── 3.2 Линейная цепочка ─────────────────

    def test_linear_chain_correct_length(self):
        """A→B→C→D — цепочка длиной 3."""
        txs = [
            make_tx('A', 'B', 10.0, 1),
            make_tx('B', 'C', 20.0, 2),
            make_tx('C', 'D', 30.0, 3),
        ]
        res = find_longest_path(txs, threshold=4)
        self.assertEqual(res['max_chain_len'], 3)
        self.assertFalse(res['path']['is_suspicious'])

    def test_linear_chain_correct_total_amount(self):
        """Сумма по пути A→B→C должна совпадать с суммой рёбер."""
        txs = [
            make_tx('A', 'B', 50.0, 1),
            make_tx('B', 'C', 75.5, 2),
        ]
        res = find_longest_path(txs)
        self.assertAlmostEqual(res['path']['total_amount'], 125.5, places=2)

    def test_linear_chain_correct_nodes(self):
        """Узлы пути A→B→C должны быть ['A','B','C']."""
        txs = [
            make_tx('A', 'B', 10.0, 1),
            make_tx('B', 'C', 10.0, 2),
        ]
        res = find_longest_path(txs)
        self.assertEqual(res['path']['nodes'], ['A', 'B', 'C'])

    # ── 3.3 Хронологическое условие ──────────

    def test_chronological_order_enforced(self):
        """Транзакция с меньшим ts не продолжает путь — нарушение хронологии."""
        # B→C идёт раньше A→B, поэтому A→B→C невозможно
        txs = [
            make_tx('A', 'B', 10.0, 10),
            make_tx('B', 'C', 10.0, 5),   # ts=5 < ts=10 → нельзя добавить
        ]
        res = find_longest_path(txs)
        # Максимальная цепочка — одна транзакция (A→B или B→C, но не обе)
        self.assertEqual(res['max_chain_len'], 1)

    def test_equal_timestamps_not_allowed(self):
        """Транзакции с одинаковым ts не могут образовывать путь."""
        txs = [
            make_tx('A', 'B', 10.0, 5),
            make_tx('B', 'C', 10.0, 5),   # ts равен — не проходит
        ]
        res = find_longest_path(txs)
        self.assertEqual(res['max_chain_len'], 1)

    # ── 3.4 Разветвлённый граф ────────────────

    def test_branched_graph_finds_longest(self):
        """Если два пути от A, берётся длиннейший."""
        txs = [
            make_tx('A', 'B', 10.0, 1),
            make_tx('B', 'C', 10.0, 2),   # путь A→B→C длиной 2
            make_tx('A', 'X', 99.0, 1),   # путь A→X длиной 1
        ]
        res = find_longest_path(txs)
        self.assertEqual(res['max_chain_len'], 2)

    def test_tiebreak_by_total_amount(self):
        """При равной длине выигрывает путь с большей суммой."""
        txs = [
            # Путь A→B→C: суммы 10+10 = 20
            make_tx('A', 'B', 10.0, 1),
            make_tx('B', 'C', 10.0, 2),
            # Путь X→Y→Z: суммы 50+50 = 100
            make_tx('X', 'Y', 50.0, 1),
            make_tx('Y', 'Z', 50.0, 2),
        ]
        res = find_longest_path(txs)
        self.assertEqual(res['max_chain_len'], 2)
        self.assertAlmostEqual(res['path']['total_amount'], 100.0, places=2)

    # ── 3.5 Флаг подозрительности ────────────

    def test_suspicious_flag_when_chain_meets_threshold(self):
        """Цепочка >= threshold → is_suspicious = True."""
        txs = [
            make_tx('A', 'B', 1.0, 1),
            make_tx('B', 'C', 1.0, 2),
            make_tx('C', 'D', 1.0, 3),
            make_tx('D', 'E', 1.0, 4),
        ]
        res = find_longest_path(txs, threshold=4)
        self.assertTrue(res['path']['is_suspicious'])
        self.assertEqual(res['suspicious_count'], 1)

    def test_not_suspicious_when_below_threshold(self):
        """Цепочка < threshold → is_suspicious = False."""
        txs = [
            make_tx('A', 'B', 1.0, 1),
            make_tx('B', 'C', 1.0, 2),
        ]
        res = find_longest_path(txs, threshold=4)
        self.assertFalse(res['path']['is_suspicious'])
        self.assertEqual(res['suspicious_count'], 0)

    def test_suspicious_flag_exactly_at_threshold(self):
        """Цепочка ровно равная threshold → is_suspicious = True."""
        txs = [make_tx(chr(65+i), chr(66+i), 1.0, i+1) for i in range(3)]  # длина 3
        res = find_longest_path(txs, threshold=3)
        self.assertTrue(res['path']['is_suspicious'])

    # ── 3.6 Статистика ───────────────────────

    def test_total_tx_count(self):
        txs = [make_tx('A', 'B', 1.0, i) for i in range(5)]
        res = find_longest_path(txs)
        self.assertEqual(res['total_tx'], 5)

    def test_total_wallets_count(self):
        txs = [make_tx('A', 'B'), make_tx('B', 'C'), make_tx('C', 'D')]
        res = find_longest_path(txs)
        self.assertEqual(res['total_wallets'], 4)  # A, B, C, D

    def test_transaction_table_in_suspicious_path_flag(self):
        """Транзакции, входящие в подозрительный путь, помечены in_suspicious_path."""
        txs = [
            make_tx('A', 'B', 1.0, 1),
            make_tx('B', 'C', 1.0, 2),
            make_tx('B', 'C', 1.0, 2),   # дубликат — не продолжит путь
            make_tx('X', 'Y', 1.0, 100), # независимая транзакция
        ]
        res = find_longest_path(txs, threshold=2)
        # Транзакция X→Y не должна быть в подозрительном пути
        table = {(r['sender'], r['receiver']): r['in_suspicious_path']
                 for r in res['transactions']}
        self.assertFalse(table.get(('X', 'Y'), True))

    # ── 3.7 Устойчивость ─────────────────────

    def test_disconnected_graph(self):
        """Два изолированных пути — алгоритм находит длиннейший без ошибок."""
        txs = [
            make_tx('A', 'B', 1.0, 1),                       # путь длина 1
            make_tx('X', 'Y', 1.0, 1),
            make_tx('Y', 'Z', 1.0, 2),                       # путь длина 2
        ]
        res = find_longest_path(txs)
        self.assertEqual(res['max_chain_len'], 2)

    def test_cycle_not_revisited(self):
        """DFS не посещает одну вершину дважды (нет зацикливания)."""
        txs = [
            make_tx('A', 'B', 1.0, 1),
            make_tx('B', 'C', 1.0, 2),
            make_tx('C', 'A', 1.0, 3),   # возврат к A
        ]
        # Алгоритм должен завершиться, не зависнуть
        res = find_longest_path(txs)
        self.assertIsNotNone(res)
        self.assertGreater(res['max_chain_len'], 0)


# ─────────────────────────────────────────────
#  4. Тесты parse_transactions (валидатор)
# ─────────────────────────────────────────────

class TestParseTransactions(unittest.TestCase):

    # ── 4.1 Корректный ввод ───────────────────

    def test_valid_single_line(self):
        parsed, errors = parse_transactions('Alice Bob 100.0 1000')
        self.assertEqual(len(errors), 0)
        self.assertTrue(parsed[0]['valid'])
        self.assertEqual(parsed[0]['sender'], 'Alice')
        self.assertEqual(parsed[0]['receiver'], 'Bob')

    def test_valid_multiple_lines(self):
        text = "A B 50.0 1\nB C 75.0 2\nC D 25.0 3"
        parsed, errors = parse_transactions(text)
        self.assertEqual(len(errors), 0)
        self.assertEqual(sum(1 for r in parsed if r['valid']), 3)

    def test_empty_lines_skipped(self):
        text = "A B 10.0 1\n\n\nB C 20.0 2"
        parsed, errors = parse_transactions(text)
        self.assertEqual(len(parsed), 2)  # пустые строки не добавляются

    # ── 4.2 Ошибочный ввод ───────────────────

    def test_empty_input_returns_error(self):
        parsed, errors = parse_transactions('')
        self.assertTrue(len(errors) > 0)
        self.assertEqual(len(parsed), 0)

    def test_whitespace_only_returns_error(self):
        parsed, errors = parse_transactions('   \n  ')
        self.assertTrue(len(errors) > 0)

    def test_too_few_fields(self):
        parsed, errors = parse_transactions('A B 100.0')  # нет timestamp
        self.assertFalse(parsed[0]['valid'])
        self.assertIn('4', parsed[0]['error'])  # упоминание '4 поля'

    def test_sender_equals_receiver_invalid(self):
        parsed, errors = parse_transactions('A A 100.0 1')
        self.assertFalse(parsed[0]['valid'])
        self.assertIn('совпад', parsed[0]['error'])

    def test_negative_amount_invalid(self):
        parsed, errors = parse_transactions('A B -50.0 1')
        self.assertFalse(parsed[0]['valid'])
        self.assertIn('сумма', parsed[0]['error'].lower())

    def test_zero_amount_invalid(self):
        parsed, errors = parse_transactions('A B 0 1')
        self.assertFalse(parsed[0]['valid'])

    def test_non_numeric_amount_invalid(self):
        parsed, errors = parse_transactions('A B abc 1')
        self.assertFalse(parsed[0]['valid'])

    def test_negative_timestamp_invalid(self):
        parsed, errors = parse_transactions('A B 100.0 -1')
        self.assertFalse(parsed[0]['valid'])
        self.assertIn('метка', parsed[0]['error'].lower())

    def test_non_integer_timestamp_invalid(self):
        parsed, errors = parse_transactions('A B 100.0 1.5')
        self.assertFalse(parsed[0]['valid'])

    def test_zero_timestamp_valid(self):
        """Нулевой timestamp допустим (>= 0)."""
        parsed, errors = parse_transactions('A B 100.0 0')
        self.assertTrue(parsed[0]['valid'])

    def test_all_invalid_lines_generates_global_error(self):
        """Если нет ни одной корректной строки — глобальная ошибка."""
        text = "A A 100.0 1\nB B 200.0 2"
        parsed, errors = parse_transactions(text)
        self.assertTrue(len(errors) > 0)

    def test_mixed_valid_and_invalid(self):
        text = "A B 100.0 1\nC C 50.0 2\nD E 75.0 3"
        parsed, errors = parse_transactions(text)
        valid_count = sum(1 for r in parsed if r['valid'])
        self.assertEqual(valid_count, 2)   # A→B и D→E
        self.assertEqual(len(errors), 0)   # есть корректные → нет глобальной ошибки


# ─────────────────────────────────────────────
#  5. Тесты validate_params
# ─────────────────────────────────────────────

class TestValidateParams(unittest.TestCase):

    def test_all_valid(self):
        errors = validate_params('4', '10', '5')
        self.assertEqual(errors, {})

    def test_threshold_too_low(self):
        errors = validate_params('1', '10', '5')
        self.assertIn('threshold', errors)

    def test_threshold_too_high(self):
        errors = validate_params('21', '10', '5')
        self.assertIn('threshold', errors)

    def test_threshold_not_integer(self):
        errors = validate_params('abc', '10', '5')
        self.assertIn('threshold', errors)

    def test_threshold_float_invalid(self):
        errors = validate_params('3.5', '10', '5')
        self.assertIn('threshold', errors)

    def test_threshold_boundary_2(self):
        errors = validate_params('2', '10', '5')
        self.assertNotIn('threshold', errors)

    def test_threshold_boundary_20(self):
        errors = validate_params('20', '10', '5')
        self.assertNotIn('threshold', errors)

    def test_tx_count_too_low(self):
        errors = validate_params('4', '0', '5')
        self.assertIn('tx_count', errors)

    def test_tx_count_too_high(self):
        errors = validate_params('4', '51', '5')
        self.assertIn('tx_count', errors)

    def test_tx_count_boundary_1(self):
        errors = validate_params('4', '1', '5')
        self.assertNotIn('tx_count', errors)

    def test_tx_count_boundary_50(self):
        errors = validate_params('4', '50', '5')
        self.assertNotIn('tx_count', errors)

    def test_wallet_count_too_low(self):
        errors = validate_params('4', '10', '1')
        self.assertIn('wallet_count', errors)

    def test_wallet_count_too_high(self):
        errors = validate_params('4', '10', '21')
        self.assertIn('wallet_count', errors)

    def test_wallet_count_boundary_2(self):
        errors = validate_params('4', '10', '2')
        self.assertNotIn('wallet_count', errors)

    def test_wallet_count_boundary_20(self):
        errors = validate_params('4', '10', '20')
        self.assertNotIn('wallet_count', errors)

    def test_multiple_errors(self):
        errors = validate_params('0', '0', '0')
        self.assertIn('threshold', errors)
        self.assertIn('tx_count', errors)
        self.assertIn('wallet_count', errors)


# ─────────────────────────────────────────────
#  6. Тесты filter_valid
# ─────────────────────────────────────────────

class TestFilterValid(unittest.TestCase):

    def test_returns_only_valid_rows(self):
        rows = [
            {'sender': 'A', 'receiver': 'B', 'amount': 10.0,
             'timestamp': 1, 'valid': True,  'error': None},
            {'sender': '—', 'receiver': '—', 'amount': '—',
             'timestamp': '—', 'valid': False, 'error': 'ошибка'},
        ]
        result = filter_valid(rows)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['sender'], 'A')

    def test_filtered_rows_have_required_keys(self):
        rows = [
            {'sender': 'X', 'receiver': 'Y', 'amount': 5.0,
             'timestamp': 99, 'valid': True,  'error': None},
        ]
        result = filter_valid(rows)
        self.assertIn('sender', result[0])
        self.assertIn('receiver', result[0])
        self.assertIn('amount', result[0])
        self.assertIn('timestamp', result[0])
        # 'valid' и 'error' не должны передаваться дальше
        self.assertNotIn('valid', result[0])
        self.assertNotIn('error', result[0])

    def test_empty_input_returns_empty(self):
        self.assertEqual(filter_valid([]), [])

    def test_all_invalid_returns_empty(self):
        rows = [
            {'sender': '—', 'receiver': '—', 'amount': '—',
             'timestamp': '—', 'valid': False, 'error': 'err'},
        ]
        self.assertEqual(filter_valid(rows), [])


# ─────────────────────────────────────────────
#  Запуск
# ─────────────────────────────────────────────

if __name__ == '__main__':
    unittest.main(verbosity=2)
