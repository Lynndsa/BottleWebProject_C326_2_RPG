import os
import sys
import time
import unittest
import subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import requests

class TestBFSSelenium(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print("ЗАПУСК ТЕСТОВ BFS")
        
        # Запуск сервера
        cls.server_process = subprocess.Popen([sys.executable, "app.py"])
        
        # Ожидание готовности сервера
        cls.base_url = "http://127.0.0.1:5555"
        for i in range(15):
            try:
                requests.get(cls.base_url)
                print("✓ Сервер запущен")
                break
            except:
                time.sleep(1)
        
        # Настройка браузера
        options = webdriver.ChromeOptions()
        options.add_experimental_option("detach", True)
        
        cls.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        cls.driver.maximize_window()
        cls.wait = WebDriverWait(cls.driver, 10)
        
        # Открываем главную страницу
        cls.driver.get(cls.base_url)
        time.sleep(2)

    @classmethod
    def tearDownClass(cls):
        print("\nЗАВЕРШЕНИЕ РАБОТЫ")
        if hasattr(cls, 'driver'):
            cls.driver.quit()
        if hasattr(cls, 'server_process'):
            cls.server_process.terminate()
            cls.server_process.wait()

    def go_to_bfs_page(self):
        """Переход на страницу BFS"""
        print("    Переход на страницу BFS...")
        self.driver.get(self.base_url + "/bfs")
        time.sleep(2)
        print("    ✓ Страница BFS загружена")

    def go_to_home(self):
        """Возврат на главную страницу"""
        print("    Возврат на главную страницу...")
        self.driver.get(self.base_url)
        time.sleep(1)
        print("    ✓ Главная страница загружена")

    def test_manual_parameters_and_edges(self):
        """Тест: ручной ввод параметров и связей"""
        
        print("\n" + "="*70)
        print("ТЕСТ: Ручной ввод параметров и связей")
        print("="*70)
        
        # Переходим на страницу BFS
        self.go_to_bfs_page()
        
        # ШАГ 1: Вводим основные параметры
        print("\n[1] Ввод параметров симуляции")
        
        # Количество узлов (N)
        n_input = self.driver.find_element(By.NAME, "n")
        n_input.clear()
        n_input.send_keys("50")
        print("    ✓ Узлы (N) = 50")
        time.sleep(1)
        
        # Количество очагов (M)
        m_input = self.driver.find_element(By.NAME, "m")
        m_input.clear()
        m_input.send_keys("50")
        print("    ✓ Очаги (M) = 50")
        time.sleep(1)
        
        # Вероятность заражения (p)
        p_input = self.driver.find_element(By.NAME, "p")
        p_input.clear()
        p_input.send_keys("0.6")
        print("    ✓ Вероятность (p) = 0.6")
        time.sleep(1)
        
        # Количество итераций (iter)
        iter_input = self.driver.find_element(By.NAME, "iter")
        iter_input.clear()
        iter_input.send_keys("100")
        print("    ✓ Итераций (iter) = 100")
        time.sleep(2)
        
        # ШАГ 2: Вводим связи между вершинами в таблице
        print("\n[2] Ввод связей (ребер) между вершинами")
        
        time.sleep(2)
        
        # Находим таблицу
        try:
            # Ждем появления таблицы после ввода N
            matrix_table = self.wait.until(
                EC.presence_of_element_located((By.ID, "matrix-table"))
            )
            print("    ✓ Таблица связей загружена")
            
            # Находим все строки в таблице (кроме заголовка)
            rows = matrix_table.find_elements(By.TAG_NAME, "tr")
            print(f"    ✓ Найдено строк для ввода: {len(rows) - 1}")
            
            # Определяем связи: (u, v)
            edges = [
                (1, 2),
                (1, 3),
                (2, 4),
                (3, 4),
                (4, 5),
                (5, 6),
                (2, 6),

                (6, 1),
                (40, 9),
                (23, 4),
                (34, 4),
                (45, 5),
                (32, 6),
                (21, 6),

                (12, 2),
                (14, 3),
                (25, 4),
                (36, 4),
                (41, 5),
                (8, 6),
                (1, 6),

                (16, 2),
                (17, 3),
                (28, 4),
                (39, 4),
                (42, 5),
                (21, 6),
                (22, 6),

                (14, 2),
                (12, 3),
                (23, 4),
                (31, 4),
                (45, 5),
                (38, 6),
                (29, 6),

                (2, 22),
                (11, 34),
                (22, 43),
                (31, 44),
                (42, 23),
                (45, 12),
                (21, 23),

                (12, 32),
                (11, 43),
                (22, 41),
                (23, 41),
                (34, 45),
                (25, 16),
                (42, 16),

                (12, 26),
            ]
            
            # Заполняем связи
            for i, (u, v) in enumerate(edges, start=1):
                try:
                    # Находим поля ввода для текущей строки
                    u_input = matrix_table.find_element(By.NAME, f"u_{i}")
                    v_input = matrix_table.find_element(By.NAME, f"v_{i}")
                    
                    # Очищаем и вводим значения
                    u_input.clear()
                    u_input.send_keys(str(u))
                    v_input.clear()
                    v_input.send_keys(str(v))
                    
                    print(f"    ✓ Связь {i}: {u} → {v}")
                    time.sleep(0.3)
                except:
                    print(f"    ⚠ Строка {i} не найдена")
                    break
            
            print(f"    ✓ Введено {len(edges)} связей")
            
        except Exception as e:
            print(f"    ⚠ Ошибка при работе с таблицей: {e}")
        
        time.sleep(3)
        
        # ШАГ 3: Запускаем симуляцию
        print("\n[3] Запуск симуляции")
        
        # Находим кнопку запуска
        try:
            run_btn = self.driver.find_element(By.CSS_SELECTOR, "button.btn-submit-bfs")
            print(f"    ✓ Найдена кнопка: '{run_btn.text}'")
        except:
            run_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Запустить симуляцию')]")
            print(f"    ✓ Найдена кнопка: '{run_btn.text}'")
        
        # Скроллим и нажимаем
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", run_btn)
        time.sleep(1)
        self.driver.execute_script("arguments[0].click();", run_btn)
        print("    ✓ Кнопка 'Запустить симуляцию' НАЖАТА")
        
        # ШАГ 4: Ожидаем результаты
        print("\n[4] Ожидание результатов симуляции...")
        time.sleep(5)
        
        # ШАГ 5: Прокручиваем к результатам
        print("\n[5] Прокрутка к результатам")
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        
        # ШАГ 6: Проверяем результаты
        print("\n[6] Проверка результатов")
        
        results_found = False
        
        # Проверяем статистику
        try:
            stats = self.driver.find_elements(By.CLASS_NAME, "analytics-metric-value")
            if stats:
                print(f"    ✓ Найдена статистика ({len(stats)} показателей):")
                for stat in stats[:4]:
                    print(f"        • {stat.text}")
                results_found = True
        except:
            pass
        
        # Проверяем SVG граф
        try:
            svg = self.driver.find_element(By.TAG_NAME, "svg")
            print("    ✓ SVG визуализация графа найдена!")
            results_found = True
        except:
            pass
        
        # Проверяем блок результатов
        try:
            results_block = self.driver.find_element(By.CLASS_NAME, "results-wrapper-block")
            print("    ✓ Блок результатов найден!")
            results_found = True
        except:
            pass
        
        # Финальный результат
        print("\n" + "="*70)
        if results_found:
            print("✅ ТЕСТ ПРОЙДЕН: Ручной ввод параметров и связей успешно выполнен!")
        else:
            print("⚠ ТЕСТ ТРЕБУЕТ ПРОВЕРКИ: Возможно результаты не загрузились")
        print("="*70)
        
        # Даем время посмотреть
        print("\n[7] Финальная пауза для просмотра результатов (8 секунд)")
        time.sleep(8)
        
        # Возвращаемся на главную
        self.go_to_home()

    def test_manual_parameters_only(self):
        """Тест: только ручной ввод параметров (без ручных связей)"""
        
        print("\n" + "="*70)
        print("ТЕСТ: Ручной ввод параметров (генерация случайного графа)")
        print("="*70)
        
        # Переходим на страницу BFS
        self.go_to_bfs_page()
        
        # ШАГ 1: Вводим параметры
        print("\n[1] Ввод параметров")
        
        params = [
            ("n", "8", "Узлы (N)"),
            ("m", "6", "Очаги (M)"),
            ("p", "0.7", "Вероятность (p)"),
            ("iter", "150", "Итераций (iter)")
        ]
        
        for name, value, desc in params:
            input_field = self.driver.find_element(By.NAME, name)
            input_field.clear()
            input_field.send_keys(value)
            print(f"    ✓ {desc} = {value}")
            time.sleep(0.5)
        
        # ШАГ 2: Генерируем граф с этими параметрами
        print("\n[2] Генерация случайного графа")
        generate_btn = self.driver.find_element(By.CSS_SELECTOR, "button[formaction='/bfs/random']")
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", generate_btn)
        time.sleep(0.5)
        generate_btn.click()
        print("    ✓ Кнопка 'Сгенерировать сеть' НАЖАТА")
        
        # Ждем генерации
        time.sleep(3)
        
        # ШАГ 3: Проверяем матрицу
        print("\n[3] Проверка сгенерированной матрицы")
        try:
            matrix = self.wait.until(EC.presence_of_element_located((By.ID, "matrix-table")))
            rows = matrix.find_elements(By.TAG_NAME, "tr")
            print(f"    ✓ Матрица загружена, количество ребер: {len(rows) - 1}")
        except:
            print("    ⚠ Матрица не загружена")
        
        # ШАГ 4: Запускаем симуляцию
        print("\n[4] Запуск симуляции")
        run_btn = self.driver.find_element(By.CSS_SELECTOR, "button.btn-submit-bfs")
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", run_btn)
        time.sleep(0.5)
        run_btn.click()
        print("    ✓ Симуляция запущена")
        
        # Ждем результаты
        print("\n[5] Ожидание результатов...")
        time.sleep(5)
        
        # Прокручиваем к результатам
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        
        print("\n✅ Тест завершен! Просмотрите результаты в браузере")
        time.sleep(8)
        
        # Возвращаемся на главную
        self.go_to_home()

    def test_full_bfs_workflow(self):
        """Полный тест BFS симуляции"""
        
        print("\n" + "="*70)
        print("ТЕСТ: BFS - Генерация графа и запуск симуляции")
        print("="*70)
        
        # Переходим на страницу BFS
        self.go_to_bfs_page()
        
        # ШАГ 1: Нажимаем кнопку "Сгенерировать сеть"
        print("\n[1] Генерация случайного графа")
        
        generate_btn = self.driver.find_element(By.CSS_SELECTOR, "button[formaction='/bfs/random']")
        print(f"    ✓ Найдена кнопка: '{generate_btn.text}'")
        
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", generate_btn)
        time.sleep(0.5)
        self.driver.execute_script("arguments[0].click();", generate_btn)
        print("    ✓ Кнопка 'Сгенерировать сеть' НАЖАТА")
        
        time.sleep(3)
        
        # ШАГ 2: Проверяем появление матрицы
        print("\n[2] Проверка загрузки матрицы смежности")
        try:
            matrix = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "matrix-table"))
            )
            print("    ✓ Матрица смежности загружена")
            rows = matrix.find_elements(By.TAG_NAME, "tr")
            print(f"    ✓ Количество ребер: {len(rows) - 1}")
        except:
            print("    ⚠ Матрица не загружена")
        
        time.sleep(2)
        
        # ШАГ 3: Нажимаем кнопку запуска
        print("\n[3] Запуск симуляции")
        
        try:
            run_btn = self.driver.find_element(By.CSS_SELECTOR, "button.btn-submit-bfs")
            print(f"    ✓ Найдена кнопка: '{run_btn.text}'")
        except:
            all_buttons = self.driver.find_elements(By.TAG_NAME, "button")
            for btn in all_buttons:
                if btn.get_attribute('formaction') is None and btn.get_attribute('type') == 'submit':
                    run_btn = btn
                    print(f"    ✓ Найдена кнопка: '{btn.text}'")
                    break
        
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", run_btn)
        time.sleep(0.5)
        self.driver.execute_script("arguments[0].click();", run_btn)
        print("    ✓ Кнопка 'Запустить симуляцию' НАЖАТА")
        
        print("\n[4] Ожидание результатов симуляции...")
        time.sleep(5)
        
        print("\n[5] Прокрутка к результатам")
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        
        print("\n[6] Проверка результатов")
        
        results_found = False
        
        try:
            results_block = self.driver.find_element(By.CLASS_NAME, "results-wrapper-block")
            print("    ✓ Блок результатов найден!")
            results_found = True
        except:
            print("    ⚠ Блок результатов не найден")
        
        try:
            svg = self.driver.find_element(By.TAG_NAME, "svg")
            print("    ✓ SVG визуализация графа найдена!")
            results_found = True
        except:
            pass
        
        try:
            chart = self.driver.find_element(By.XPATH, "//img[contains(@src, 'base64')]")
            print("    ✓ График динамики заражения найден!")
            results_found = True
        except:
            pass
        
        print("\n" + "="*70)
        if results_found:
            print("✅ ТЕСТ ПРОЙДЕН: Симуляция успешно запущена и результаты отображены!")
        else:
            print("⚠ ТЕСТ ТРЕБУЕТ ПРОВЕРКИ: Кнопки нажаты, но результаты не видны")
        print("="*70)
        
        print("\n[7] Финальная пауза для просмотра результатов (8 секунд)")
        time.sleep(8)
        
        # Возвращаемся на главную
        self.go_to_home()

    def test_generate_only(self):
        """Тест только генерации графа"""
        
        print("\n" + "="*70)
        print("ТЕСТ: Только генерация случайного графа")
        print("="*70)
        
        # Переходим на страницу BFS
        self.go_to_bfs_page()
        
        generate_btn = self.driver.find_element(By.CSS_SELECTOR, "button[formaction='/bfs/random']")
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", generate_btn)
        time.sleep(0.5)
        generate_btn.click()
        
        time.sleep(3)
        
        try:
            matrix = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.ID, "matrix-table"))
            )
            rows = matrix.find_elements(By.TAG_NAME, "tr")
            print(f"✓ Граф сгенерирован успешно! Количество ребер: {len(rows) - 1}")
        except:
            print("❌ Граф не сгенерирован")
        
        time.sleep(3)
        
        # Возвращаемся на главную
        self.go_to_home()

    def test_run_only(self):
        """Тест только запуска симуляции (с уже существующим графом)"""
        
        print("\n" + "="*70)
        print("ТЕСТ: Запуск симуляции на существующем графе")
        print("="*70)
        
        # Переходим на страницу BFS
        self.go_to_bfs_page()
        
        generate_btn = self.driver.find_element(By.CSS_SELECTOR, "button[formaction='/bfs/random']")
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", generate_btn)
        time.sleep(0.5)
        generate_btn.click()
        time.sleep(3)
        
        run_btn = self.driver.find_element(By.CSS_SELECTOR, "button.btn-submit-bfs")
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", run_btn)
        time.sleep(0.5)
        run_btn.click()
        
        print("✓ Симуляция запущена!")
        time.sleep(5)
        
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        
        print("✓ Результаты должны быть видны внизу страницы")
        time.sleep(5)
        
        # Возвращаемся на главную
        self.go_to_home()


def run_test_choice():
    """Функция для выбора и запуска тестов с возвратом в меню"""
    
    # Создаем экземпляр теста
    test = TestBFSSelenium()
    
    try:
        # Инициализация
        test.setUpClass()
        
        while True:
            print("\n" + "="*70)
            print("ГЛАВНОЕ МЕНЮ ТЕСТИРОВАНИЯ BFS")
            print("="*70)
            print("1 - Полный тест (генерация + запуск + проверка)")
            print("2 - Только генерация графа")
            print("3 - Только запуск симуляции")
            print("4 - Ручной ввод параметров и связей (полный)")
            print("5 - Ручной ввод параметров + случайный граф")
            print("-"*70)
            print("0 - ВЫХОД")
            print("="*70)
            
            choice = input("\n👉 Ваш выбор (0-5): ").strip()
            
            if choice == "0":
                print("\n🚪 Выход из программы...")
                break
            elif choice == "1":
                test.test_full_bfs_workflow()
                input("\n✅ Тест завершен. Нажмите Enter для возврата в меню...")
            elif choice == "2":
                test.test_generate_only()
                input("\n✅ Тест завершен. Нажмите Enter для возврата в меню...")
            elif choice == "3":
                test.test_run_only()
                input("\n✅ Тест завершен. Нажмите Enter для возврата в меню...")
            elif choice == "4":
                test.test_manual_parameters_and_edges()
                input("\n✅ Тест завершен. Нажмите Enter для возврата в меню...")
            elif choice == "5":
                test.test_manual_parameters_only()
                input("\n✅ Тест завершен. Нажмите Enter для возврата в меню...")
            else:
                print("\n❌ Неверный выбор! Пожалуйста, выберите 0-5")
                time.sleep(1)
    
    except KeyboardInterrupt:
        print("\n\n⚠️ Программа прервана пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
    finally:
        # Закрытие ресурсов
        print("\n🧹 Закрытие браузера и остановка сервера...")
        test.tearDownClass()
        print("👋 До свидания!")


if __name__ == "__main__":
    run_test_choice()