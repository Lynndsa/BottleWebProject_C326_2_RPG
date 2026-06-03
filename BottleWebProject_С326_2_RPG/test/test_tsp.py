import sys
import os
import unittest
import json


from validators.tsp_validator import parse_input, parse_txt_file
from tools.tsp_tools import generate_random_graph


# ==========================================================
# Тесты parse_input
# ==========================================================
class TestParseInput(unittest.TestCase):

    def test_valid_input(self):
        edges = (
            "1 2 5\n"
            "2 3 3\n"
            "3 4 7\n"
            "1 4 10\n"
            "2 4 6"
        )

        # Передаем все 5 параметров: n, m, edges, hotel, sites
        graph, hotel, targets, errors = parse_input(
            '4',     # n
            '2',     # m
            edges,   # edges_text
            '1',     # hotel_k
            '2 3'    # sites_text
        )

        self.assertEqual(errors, {})
        self.assertEqual(hotel, '1')
        self.assertEqual(targets, ['2', '3'])
        self.assertEqual(graph['1']['2'], 5)

    def test_invalid_parameters(self):
        # Кейсы: (n, m, edges, hotel, sites)
        test_cases = [
            ('abc', '2', '1 2 5', '1', '2'),
            ('25', '2', '1 2 5', '1', '2'),  # N > 20
            ('4', '9', '1 2 5', '1', '2'),   # M > 8
        ]

        for n, m, edges, hotel, sites in test_cases:
            with self.subTest(n=n, m=m):
                _, _, _, errors = parse_input(n, m, edges, hotel, sites)
                self.assertTrue(errors)

    def test_invalid_sites(self):
        edges = "1 2 5\n2 3 4\n1 3 7"

        # Кейсы: (n, m, edges, hotel, sites)
        cases = [
            ('3', '2', edges, '1', '1 2'),  # Отель входит в список целей
            ('3', '2', edges, '1', '2 2'),  # Дубликаты целей
            ('3', '2', edges, '1', ''),     # Пустые цели
        ]

        for args in cases:
            with self.subTest(args=args):
                _, _, _, errors = parse_input(*args)
                self.assertTrue(errors)


# ==========================================================
# Тесты parse_txt_file
# ==========================================================
class TestParseTxtFile(unittest.TestCase):

    def test_valid_file(self):
        content = (
            "5 2 1\n"
            "1 2 4\n"
            "2 3 5\n"
            "3 4 2\n"
            "4 5 3\n"
            "1 5 8\n"
            "sites: 3 5"
        )

        form_data, errors = parse_txt_file(content)

        self.assertEqual(errors, {})
        self.assertEqual(form_data['n'], '5')
        self.assertEqual(form_data['m'], '2')
        self.assertEqual(form_data['k'], '1')

    def test_invalid_file_structure(self):
        cases = [
            '',
            "5 2\n1 2 4\nsites: 3 5",  # Нет K в первой строке
            "5 2 1\n1 2 4\n2 3 5"        # Нет строки sites:
        ]

        for content in cases:
            with self.subTest(content=content):
                _, errors = parse_txt_file(content)
                self.assertIn('global', errors)

    def test_invalid_file_data(self):
        cases = [
            "5 2 1\n1 2 0\n2 3 5\nsites: 3 5",     # Вес ребра < 1
            "5 2 1\n1 2 4\n2 3 5\nsites: 1 3",     # Отель 1 является целью
            "5 2 1\n1 2 4\n2 3 5\nsites: 3 3",     # Дубликаты в sites
            "5 3 1\n1 2 4\n2 3 5\nsites: 3 5",     # Количество сайтов не совпадает с M=3
        ]

        for content in cases:
            with self.subTest(content=content):
                _, errors = parse_txt_file(content)
                self.assertIn('global', errors)


# ==========================================================
# Проверка загрузки файлов
# ==========================================================
class TestFileUploadValidation(unittest.TestCase):

    def test_valid_extensions(self):
        valid_files = ['graph.txt', 'graph.json', 'GRAPH.TXT', 'GRAPH.JSON']

        for filename in valid_files:
            with self.subTest(filename=filename):
                self.assertTrue(filename.lower().endswith(('.txt', '.json')))

    def test_invalid_extensions(self):
        invalid_files = ['graph.csv', 'graph.xlsx', 'graph.docx', 'graph']

        for filename in invalid_files:
            with self.subTest(filename=filename):
                self.assertFalse(filename.lower().endswith(('.txt', '.json')))

    def test_file_content_validation(self):
        utf8_content = "5 2 1\n1 2 4\nsites: 3 5".encode('utf-8')
        decoded = utf8_content.decode('utf-8')
        self.assertIsInstance(decoded, str)

        with self.assertRaises(UnicodeDecodeError):
            b'\xff\xfe'.decode('utf-8')

        valid_json = '{"n":5,"m":2,"k":1,"sites":[3,5],"edges":[{"u":1,"v":2,"w":4}]}'
        data = json.loads(valid_json)
        self.assertEqual(data['n'], 5)

        with self.assertRaises(json.JSONDecodeError):
            json.loads('{broken json}')


# ==========================================================
# Генерация случайного графа
# ==========================================================
class TestRandomGeneration(unittest.TestCase):

    def test_random_graph_structure(self):
        data = generate_random_graph()

        self.assertIn('n', data)
        self.assertIn('m', data)
        self.assertIn('k', data)
        self.assertIn('sites', data)
        self.assertIn('edges', data)

    def test_random_graph_ranges(self):
        data = generate_random_graph()

        n = int(data['n'])
        m = int(data['m'])
        k = int(data['k'])

        self.assertTrue(5 <= n <= 20)
        self.assertTrue(1 <= m <= 8)
        self.assertTrue(1 <= k <= n)

    def test_random_graph_passes_validation(self):
        data = generate_random_graph()

        # Передаем сгенерированные данные строго по новой сигнатуре (5 параметров)
        graph, hotel, targets, errors = parse_input(
            str(data['n']),
            str(data['m']),
            data['edges'],
            str(data['k']),
            data['sites']
        )

        self.assertEqual(errors, {})


if __name__ == '__main__':
    unittest.main(verbosity=2)