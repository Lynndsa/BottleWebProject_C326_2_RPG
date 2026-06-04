import unittest
import random
import networkx as nx
from collections import deque

from algorithms.bfs_algorithm import ProbabilisticBFS
from validators.bfs_validator import validate_bfs_params


class TestProbabilisticBFS(unittest.TestCase):

    def setUp(self):
        self.graph = nx.path_graph(5)
        self.p_deterministic = 1.0
        self.p_stochastic = 0.5

    def test_connected_component_size_full(self):
        """Проверяет размер компоненты связности при детерминированном распространении"""
        bfs = ProbabilisticBFS(self.graph, p=self.p_deterministic)
        self.assertEqual(bfs.get_connected_component_size([0]), 5)

    def test_single_simulation_deterministic(self):
        """Проверяет детерминированную симуляцию заражения на линейном графе"""
        bfs = ProbabilisticBFS(self.graph, p=1.0)
        result = bfs.run_single_simulation(initial_infected=[0])

        self.assertEqual(result['total_infected'], 5)
        self.assertEqual(result['infection_steps'][0], 0)
        self.assertEqual(result['infection_steps'][4], 4)
        self.assertEqual(len(result['infection_progression']), 6)

    def test_single_simulation_empty_start(self):
        """Проверяет симуляцию без начальных заражённых узлов"""
        bfs = ProbabilisticBFS(self.graph, p=0.5)
        result = bfs.run_single_simulation(initial_infected=[])
        self.assertEqual(result['total_infected'], 0)
        self.assertEqual(result['duration'], 0)
        self.assertEqual(result['infection_progression'], [0])

    def test_monte_carlo_structure(self):
        """Проверяет структуру результатов Монте-Карло симуляции"""
        bfs = ProbabilisticBFS(self.graph, p=self.p_stochastic)
        iterations = 50
        results = bfs.monte_carlo_simulation(initial_infected=[0], num_iterations=iterations)
        self.assertEqual(results['iterations'], iterations)
        self.assertTrue(0 <= results['avg_infected_percentage'] <= 100)

    def test_monte_carlo_determinism_via_seed(self):
        """Проверяет воспроизводимость результатов при одинаковом seed"""
        random.seed(42)
        bfs1 = ProbabilisticBFS(self.graph, p=0.5)
        res1 = bfs1.monte_carlo_simulation(initial_infected=[0, 1], num_iterations=20)
        
        random.seed(42)
        bfs2 = ProbabilisticBFS(self.graph, p=0.5)
        res2 = bfs2.monte_carlo_simulation(initial_infected=[0, 1], num_iterations=20)
        
        self.assertEqual(res1['avg_infected_count'], res2['avg_infected_count'])
        self.assertEqual(res1['most_common_pattern'], res2['most_common_pattern'])
        self.assertEqual(res1['timeline'], res2['timeline'])


class TestBFSValidator(unittest.TestCase):

    def test_all_params_valid(self):
        """Проверяет корректную валидацию всех параметров"""
        form_data = {
            'n': '10',
            'm': '9',
            'p': '0.5',
            'iter': '100',
            'v_inf': '1 8 9'
        }
        
        validated, errors = validate_bfs_params(form_data)
        
        self.assertEqual(errors, {})
        self.assertEqual(validated['n'], 10)
        self.assertEqual(validated['m'], 9)
        self.assertEqual(validated['p'], 0.5)
        self.assertEqual(validated['iter'], 100)
        self.assertEqual(validated['v_inf'], [1, 8, 9])

    def test_invalid_node_bounds(self):
        """Проверяет обработку недопустимого количества узлов (2-50)"""
        validated, errors = validate_bfs_params({'n': '1', 'm': '0', 'p': '0.5', 'iter': '10'})
        self.assertIn('n', errors)
        self.assertEqual(errors['n'], 'N должно быть от 2 до 50')
        
        validated, errors = validate_bfs_params({'n': '51', 'm': '0', 'p': '0.5', 'iter': '10'})
        self.assertIn('n', errors)

    def test_invalid_edge_bounds_via_max_edges(self):
        """Проверяет ограничение на максимальное количество рёбер"""
        form_data = {
            'n': '10',
            'm': '46', 
            'p': '0.5',
            'iter': '100'
        }
        validated, errors = validate_bfs_params(form_data)
        self.assertIn('m', errors)
        self.assertEqual(errors['m'], 'Максимум рёбер для 10 вершин — 45 (полный граф)')

    def test_probability_with_comma_handling(self):
        """Проверяет обработку вероятности с запятой вместо точки"""
        form_data = {'n': '10', 'm': '5', 'p': '0,5', 'iter': '100'}
        validated, errors = validate_bfs_params(form_data)
        
        self.assertIn('p', errors)
        self.assertEqual(errors['p'], 'p должно быть числом')

    def test_infected_nodes_out_of_range(self):
        """Проверяет реакцию на очаги заражения вне диапазона узлов"""
        form_data = {
            'n': '10',
            'm': '9',
            'p': '0.5',
            'iter': '100',
            'v_inf': '1 13 9'
        }
        validated, errors = validate_bfs_params(form_data)
        self.assertIn('v_inf', errors)
        self.assertEqual(errors['v_inf'], 'Узел 13 вне диапазона 1..10')

    def test_empty_or_broken_infected_nodes(self):
        """Проверяет подстановку узла по умолчанию при пустых очагах"""
        form_data = {
            'n': '10',
            'm': '9',
            'p': '0.5',
            'iter': '100',
            'v_inf': ''
        }
        validated, errors = validate_bfs_params(form_data)
        
        self.assertIn('v_inf', errors)
        self.assertEqual(errors['v_inf'], 'Указаны некорректные очаги, используем узел 1')
        self.assertEqual(validated['v_inf'], [1])


if __name__ == '__main__':
    unittest.main(verbosity=2)