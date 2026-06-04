import os
import sys
import time
import random
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class TestTSPSelenium(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print("ЗАПУСК ТЕСТОВ ПС (МАРШРУТЫ TSP)")
        cls.driver = webdriver.Chrome()  # Инициализация браузера Chrome
        cls.driver.maximize_window()     # Разворачиваем окно на весь экран
        cls.base_url = "http://127.0.0.1:5555"  # Наш локальный порт
        cls.wait = WebDriverWait(cls.driver, 10)  # Ожидание элементов

    def scroll_down(self, y=500):
        """Плавный скролл вниз на заданное расстояние."""
        self.driver.execute_script(f"window.scrollBy(0, {y});")
        time.sleep(1.5)

    def pause(self, text, sec=None):
        """Умная пауза с выводом логов."""
        sec = sec or random.uniform(1.5, 2.5)
        print(text)
        time.sleep(sec)

    # =========================================================================
    # ПС-01: Переход с главной на страницу модуля TSP
    # =========================================================================
    def test_1_open_page(self):
        print("\n[TEST 1] Старт с главной страницы")
        self.driver.get(self.base_url)
        self.pause("[TEST 1] Ждём главную страницу")
        
        self.driver.get(self.base_url + "/tsp")
        self.pause("[TEST 1] Перешли в модуль TSP")
        
        self.wait.until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        print("TEST 1 пройден")

    # =========================================================================
    # ПС-02: Случайный граф, генерация и запуск просчета
    # =========================================================================
    def test_2_random_generation(self):
        print("\n[TEST 2] RANDOM сценарий TSP")
        self.driver.get(self.base_url + "/tsp")
        self.pause("[TEST 2] Открыли страницу TSP")

        random_button = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[formaction='/tsp/random']"))
        )
        # Большой скролл, чтобы кнопка гарантированно была в зоне видимости
        self.scroll_down(300)
        self.pause("[TEST 2] Жмём кнопку 'Случайный'")
        
        self.driver.execute_script("arguments[0].click();", random_button)

        self.wait.until(
            EC.presence_of_element_located((By.ID, "input-n"))
        )
        n_val = self.driver.find_element(By.ID, "input-n").get_attribute("value")
        print(f"[TEST 2] Бэкенд сгенерировал граф. Текущий N = {n_val}")

        solve_btn = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn-submit-tsp"))
        )
        self.pause("[TEST 2] Жмём Найти оптимальный маршрут")
        self.driver.execute_script("arguments[0].click();", solve_btn)

        self.pause("[TEST 2] Ожидаем просчёт алгоритма...")
        self.wait.until(
            EC.presence_of_element_located((By.ID, "result-anchor"))
        )
        
        # Скроллим глубоко вниз к блоку визуализации
        self.scroll_down(800)
        self.pause("[TEST 2] Маршрут успешно визуализирован!")
        print("TEST 2 пройден")

    # =========================================================================
    # ПС-03: Полностью РУЧНОЙ ВВОД параметров и добавление ребер через кнопку
    # =========================================================================
    def test_3_manual_input(self):
        print("\n[TEST 3] MANUAL сценарий TSP (Стресс-тест: 50 вершин)")
        self.driver.get(self.base_url + "/tsp")
        self.pause("[TEST 3] Открыли чистую форму TSP")

        # 1. Находим базовые параметры
        n_field = self.wait.until(EC.presence_of_element_located((By.ID, "input-n")))
        m_field = self.driver.find_element(By.NAME, "m")
        k_field = self.driver.find_element(By.ID, "input-k")
        sites_field = self.driver.find_element(By.NAME, "sites")

        # Заполняем по красоте большие данные
        n_field.clear()
        n_field.send_keys("50")
        
        m_field.clear()
        m_field.send_keys("7")
        
        k_field.clear()
        k_field.send_keys("48")  # Отель 48
        
        sites_field.clear()
        sites_field.send_keys("50 18 34 13 47 8 42")
        self.pause("[TEST 3] Заполнили параметры вручную (N=50, M=7, K=48, сайтов=7)")

        # Находим кнопку добавления ребра 
        add_edge_btn = self.wait.until(
            EC.element_to_be_clickable((By.ID, "btn-add-edge"))
        )
        #  прокручиваем к кнопке добавления рёбер
        self.scroll_down(400)
        
        test_edges = [
                    # Основное кольцо и связи между сайтами
                    ("48", "50", "17"),
                    ("48", "18", "1"),
                    ("48", "34", "20"),
                    ("50", "18", "12"),
                    ("50", "34", "10"),
                    ("18", "34", "3"),
                    ("34", "13", "5"),
                    ("13", "47", "6"),
                    ("47", "8", "20"),
                    ("8", "42", "7"),
                    ("42", "48", "4"),
                    ("13", "8", "9"),
                    ("50", "13", "8"),
                    ("50", "47", "2"),
                    ("50", "8", "8"),
                    ("18", "13", "3"),
                    ("18", "42", "18"),
                    ("34", "47", "5"),
                    ("34", "42", "18"),
                    ("13", "42", "17"),
                    ("1", "48", "10"),
                    ("1", "50", "17"),
                    ("1", "18", "20"),
                    ("9", "50", "1"),
                    ("18", "25", "11"),
                    ("8", "16", "8")
                ]

        print(f"[TEST 3] Начинаем автоматическое заполнение таблицы рёбер ({len(test_edges)} строк)...")
        for i, (u_val, v_val, w_val) in enumerate(test_edges, start=1):
            add_edge_btn.click()
            time.sleep(0.1)  # Легкая задержка, чтобы JS успел создать DOM-элементы
            
            # Находим инпуты в только что созданной строке по индексу `i`
            u_input = self.driver.find_element(By.NAME, f"u_{i}")
            v_input = self.driver.find_element(By.NAME, f"v_{i}")
            w_input = self.driver.find_element(By.NAME, f"w_{i}")
            
            u_input.send_keys(u_val)
            v_input.send_keys(v_val)
            w_input.send_keys(w_val)

        # Скроллим ещё ниже, так как таблица рёбер разрослась на 12 строк
        self.scroll_down(300)
        self.pause("[TEST 3] Таблица рёбер успешно заполнена скриптом!")

        # 3. Отправляем форму на расчёт
        solve_btn = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn-submit-tsp"))
        )
        self.pause("[TEST 3] Жмём 'Найти оптимальный маршрут' и отправляем 50 вершин на бэкенд...")
        self.driver.execute_script("arguments[0].click();", solve_btn)

        # Даем бэкенду чуть больше времени (4-5 секунд), так как граф большой
        print("[TEST 3] Ждем пока Дейкстра и перебор отработают...")
        time.sleep(4)

        # 4. Проверяем, что блок результатов успешно появился
        self.wait.until(
            EC.presence_of_element_located((By.ID, "result-anchor"))
        )
        
        # Финальный мощный скролл в самый низ страницы к готовому графу
        self.scroll_down(800)
        self.pause("[TEST 3] Тяжелый ручной ввод успешно рассчитан!")
        print("TEST 3 пройден")


if __name__ == "__main__":
    unittest.main()