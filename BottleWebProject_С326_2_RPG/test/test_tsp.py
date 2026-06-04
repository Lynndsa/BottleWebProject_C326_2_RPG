import sys
import os
import unittest
import json

from validators.tsp_validator import parse_input, parse_txt_file
from tools.tsp_tools import generate_random_graph


# Тестирование функции
class TestParseInput(unittest.TestCase):

    def test_valid_input(self):
        # Корректные входные данные - все параметры валидны
        edges = (
            "1 2 5\n"
            "2 3 3\n"
            "3 4 7\n"
            "1 4 10\n"
            "2 4 6"
        )

        # Передаем все 5 параметров: n, m, edges, hotel, sites
        graph, hotel, targets, errors = parse_input(
            '4',    
            '2',    
            edges,   
            '1',     
            '2 3'   
        )

        self.assertEqual(errors, {})
        self.assertEqual(hotel, '1')
        self.assertEqual(targets, ['2', '3'])
        self.assertEqual(graph['1']['2'], 5)

    # Невалидные параметры: неверный формат n, m, или выход за пределы"
    def test_invalid_parameters(self):
        test_cases = [
            ('abc', '2', '1 2 5', '1', '2'),  # n - не число
            ('58', '2', '1 2 5', '1', '2'),   # n > 50 
            ('4', '9', '1 2 5', '1', '2'),    # m > 8
        ]

        for n, m, edges, hotel, sites in test_cases:
            with self.subTest(n=n, m=m):
                _, _, _, errors = parse_input(n, m, edges, hotel, sites)
                self.assertTrue(errors)  

    # Невалидные цели: отель среди целей, дубликаты или пустой список
    def test_invalid_sites(self):
        edges = "1 2 5\n2 3 4\n1 3 7"

        cases = [
            ('3', '2', edges, '1', '1 2'),  # Отель входит в список целей
            ('3', '2', edges, '1', '2 2'),  # Дубликаты целей
            ('3', '2', edges, '1', ''),     # Пустые цели
        ]

        for args in cases:
            with self.subTest(args=args):
                _, _, _, errors = parse_input(*args)
                self.assertTrue(errors)


# Тесты функции parse_txt_file
class TestParseTxtFile(unittest.TestCase):
    # Корректный .txt файл с полной структурой
    def test_valid_file(self):      
        content = (
            "5 2 1\n"           
            "1 2 4\n"          
            "2 3 5\n"
            "3 4 2\n"
            "4 5 3\n"
            "1 5 8\n"
            "sites: 3 5"        # строка с обязательными вершинами
        )

        form_data, errors = parse_txt_file(content)

        self.assertEqual(errors, {})
        self.assertEqual(form_data['n'], '5')
        self.assertEqual(form_data['m'], '2')
        self.assertEqual(form_data['k'], '1')

    # Нарушена структура файла: отсутствуют обязательные элементы
    def test_invalid_file_structure(self):
        cases = [
            '',                          # Пустой файл
            "5 2\n1 2 4\nsites: 3 5",  # Нет k в первой строке
            "5 2 1\n1 2 4\n2 3 5"       # Нет строки sites:
        ]

        for content in cases:
            with self.subTest(content=content):
                _, errors = parse_txt_file(content)
                self.assertIn('global', errors)  

    # Данные в файле корректны по структуре, но не проходят валидацию
    def test_invalid_file_data(self):      
        cases = [
            "5 2 1\n1 2 0\n2 3 5\nsites: 3 5",     # Вес ребра < 1
            "5 2 1\n1 2 4\n2 3 5\nsites: 1 3",     # Отель 1 является целью
            "5 2 1\n1 2 4\n2 3 5\nsites: 3 3",     # Дубликаты в sites
            "5 3 1\n1 2 4\n2 3 5\nsites: 3 5",     # Кол-во сайтов != m
        ]

        for content in cases:
            with self.subTest(content=content):
                _, errors = parse_txt_file(content)
                self.assertIn('global', errors)



# Валидация загружаемых файлов (расширения и кодировка)
class TestFileUploadValidation(unittest.TestCase):
    def test_valid_extensions(self):
        # "Допустимые расширения файлов
        valid_files = ['graph.txt', 'graph.json', 'GRAPH.TXT', 'GRAPH.JSON']

        for filename in valid_files:
            with self.subTest(filename=filename):
                self.assertTrue(filename.lower().endswith(('.txt', '.json')))

    def test_invalid_extensions(self):
        # Недопустимые расширения файлов
        invalid_files = ['graph.csv', 'graph.xlsx', 'graph.docx', 'graph']

        for filename in invalid_files:
            with self.subTest(filename=filename):
                self.assertFalse(filename.lower().endswith(('.txt', '.json')))
# Проверка кодировки UTF-8 и парсинга JSON
    def test_file_content_validation(self):
        
        utf8_content = "5 2 1\n1 2 4\nsites: 3 5".encode('utf-8')
        decoded = utf8_content.decode('utf-8')
        self.assertIsInstance(decoded, str)

        # Некорректная UTF-8 последовательность
        with self.assertRaises(UnicodeDecodeError):
            b'\xff\xfe'.decode('utf-8')

        # Валидный JSON
        valid_json = '{"n":5,"m":2,"k":1,"sites":[3,5],"edges":[{"u":1,"v":2,"w":4}]}'
        data = json.loads(valid_json)
        self.assertEqual(data['n'], 5)

        # Невалидный JSON
        with self.assertRaises(json.JSONDecodeError):
            json.loads('{broken json}')


# Тестирование генерации случайного графа
class TestRandomGeneration(unittest.TestCase):

    def test_random_graph_structure(self):
        data = generate_random_graph()

        self.assertIn('n', data)       # Кол-во вершин
        self.assertIn('m', data)       # Кол-во обязательных вершин
        self.assertIn('k', data)       # Вершина-отель
        self.assertIn('sites', data)   # Список вершин
        self.assertIn('edges', data)   # Список ребер

    def test_random_graph_ranges(self):
        # Проверка, что сгенерированные значения в допустимых диапазонах
        data = generate_random_graph()

        n = int(data['n'])   # 5-50
        m = int(data['m'])   # 1-8
        k = int(data['k'])   # 1-n

        self.assertTrue(5 <= n <= 50)
        self.assertTrue(1 <= m <= 8)
        self.assertTrue(1 <= k <= n)

    def test_random_graph_passes_validation(self):
        # Сгенерированный граф должен проходить все проверки валидатора
        data = generate_random_graph()

        # Передаем сгенерированные данные в валидатор
        graph, hotel, targets, errors = parse_input(
            str(data['n']),
            str(data['m']),
            data['edges'],
            str(data['k']),
            data['sites']
        )

        self.assertEqual(errors, {})  # Ошибок быть не должно


if __name__ == '__main__':
    unittest.main(verbosity=2)