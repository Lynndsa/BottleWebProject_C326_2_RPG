# -*- coding: utf-8 -*-
import os
import sys
import time
import unittest

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.options import Options
from selenium.common.exceptions import TimeoutException

sys.stdout.reconfigure(encoding='utf-8')

# Константы

BASE_URL          = "http://127.0.0.1:5555"
DFS_URL           = f"{BASE_URL}/dfs"
TIMEOUT           = 15
PAUSE             = 1.2   # пауза между шагами
SCRIPT_DIR        = os.path.dirname(os.path.abspath(__file__))
LARGE_DATA_FILE   = os.path.join(SCRIPT_DIR, "test_data_large.txt")
INVALID_DATA_FILE = os.path.join(SCRIPT_DIR, "test_data_invalid.txt")


def read_file(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


class TestDfsPage(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        opts = Options()
        opts.add_argument("--window-size=1600,1000")
        opts.add_argument("--disable-extensions")
        cls.driver = webdriver.Edge(options=opts)
        cls.wait   = WebDriverWait(cls.driver, TIMEOUT)

    @classmethod
    def tearDownClass(cls):
        time.sleep(PAUSE * 2)   # пауза перед закрытием — видно финальный результат
        cls.driver.quit()

    # Вспомогательные методы

    def _open_dfs(self):
        """Открывает /dfs и ждёт загрузки формы."""
        self.driver.get(DFS_URL)
        self.wait.until(EC.presence_of_element_located((By.ID, "dfs-form")))
        time.sleep(PAUSE)
        self._scroll(y=0)

    def _scroll(self, element_id: str = None, y: int = None):
        """Плавная прокрутка к элементу или на координату."""
        if element_id:
            self.driver.execute_script(
                "document.getElementById(arguments[0])"
                ".scrollIntoView({behavior:'smooth', block:'center'});",
                element_id
            )
        elif y is not None:
            self.driver.execute_script(
                f"window.scrollTo({{top:{y}, behavior:'smooth'}});"
            )
        time.sleep(PAUSE)

    def _scroll_down(self):
        self.driver.execute_script(
            "window.scrollTo({top:document.body.scrollHeight, behavior:'smooth'});"
        )
        time.sleep(PAUSE)

    def _set_threshold(self, value: int):
        self._scroll("threshold-range")
        self.driver.execute_script("""
            document.getElementById('threshold').value       = arguments[0];
            document.getElementById('threshold-range').value = arguments[0];
            var d = document.getElementById('threshold-display');
            if (d) d.textContent = arguments[0];
        """, str(value))
        time.sleep(PAUSE)

    def _set_mode(self, mode: str):
        self.driver.execute_script(
            "document.getElementById('input_mode').value = arguments[0];", mode
        )
        time.sleep(PAUSE * 0.5)

    def _set_transactions(self, text: str):
        """Записывает транзакции в скрытую textarea и разблокирует кнопку."""
        self._scroll("tx-main-table")
        self.driver.execute_script("""
            var ta  = document.getElementById('tx-hidden-input');
            var btn = document.getElementById('tx-run');
            ta.value         = arguments[0];
            ta.style.display = 'block';
            btn.disabled     = false;
            btn.removeAttribute('disabled');
        """, text)
        time.sleep(PAUSE)

    def _submit(self):
        self._scroll("tx-run")
        time.sleep(PAUSE)
        self.driver.execute_script("document.getElementById('dfs-form').submit();")

    def _wait_result(self):
        try:
            self.wait.until(EC.presence_of_element_located((By.ID, "dfs-form")))
        except TimeoutException:
            pass
        time.sleep(PAUSE)
        self._scroll_down()

    def _body(self) -> str:
        return self.driver.find_element(By.TAG_NAME, "body").text

    # Тест 1: навигация и структура страницы

    def test_1_page_structure_and_navigation(self):
        """
        Проверяет структуру страницы /dfs и навигацию:
        - все ключевые элементы формы присутствуют
        - все пункты меню видны
        - клик по логотипу возвращает на главную
        - ссылка 'Модуль DFS' ведёт обратно на /dfs
        """
        print("\n[Тест 1] Открываем /dfs...")
        self._open_dfs()

        # Проверяем заголовок
        body = self._body()
        self.assertTrue(
            "DFS" in body.upper() or "Анализ" in body,
            "Заголовок DFS не найден"
        )

        # Проверяем ключевые элементы формы
        print("[Тест 1] Проверяем элементы формы...")
        self._scroll("dfs-form")
        for el_id in ["dfs-form", "threshold", "threshold-range", "btn-random", "tx-run"]:
            el = self.driver.find_element(By.ID, el_id)
            self.assertIsNotNone(el, f"Элемент #{el_id} не найден")
        time.sleep(PAUSE)

        # Проверяем пункты меню
        print("[Тест 1] Проверяем навигацию...")
        self._scroll(y=0)
        for href in ["/", "/bfs", "/dfs", "/tsp", "/about"]:
            links = self.driver.find_elements(By.CSS_SELECTOR, f"a[href='{href}']")
            self.assertTrue(len(links) > 0, f"Ссылка {href} не найдена")
        time.sleep(PAUSE)

        # Клик по логотипу → главная
        print("[Тест 1] Кликаем на логотип -> главная...")
        brand = self.driver.find_element(By.CSS_SELECTOR, "a.navbar-brand")
        brand.click()
        self.wait.until(EC.url_to_be(f"{BASE_URL}/"))
        self.assertEqual(self.driver.current_url.rstrip("/"), BASE_URL.rstrip("/"))
        time.sleep(PAUSE)

        # Ссылка DFS → обратно на /dfs
        print("[Тест 1] Переходим обратно на /dfs...")
        link = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='/dfs']"))
        )
        link.click()
        self.wait.until(EC.url_contains("/dfs"))
        self.assertIn("/dfs", self.driver.current_url)
        time.sleep(PAUSE)

        print("[Тест 1] ПРОЙДЕН")

    # ══ Тест 2: ручной ввод — валидные и невалидные данные ═══════════════════

    def test_2_manual_input_validation(self):
        """
        Проверяет обработку ручного ввода транзакций:
        - корректные данные принимаются без ошибок
        - пустой ввод → сообщение об ошибке
        - отправитель == получатель → строка невалидна
        - порог вне диапазона → ошибка валидации
        """
        VALID_TX = (
            "wallet_A wallet_B 100.00 1000\n"
            "wallet_B wallet_C 200.00 1001\n"
            "wallet_C wallet_D 150.00 1002\n"
            "wallet_D wallet_E 300.00 1003\n"
            "wallet_E wallet_F 250.00 1004\n"
        )

        # Шаг 1: корректные данные
        print("\n[Тест 2] Шаг 1 — корректные транзакции...")
        self._open_dfs()
        self._set_threshold(2)
        self._set_mode("manual")
        self._set_transactions(VALID_TX)
        self._submit()
        self._wait_result()
        self.assertNotIn("Не найдено ни одной корректной транзакции", self._body())
        time.sleep(PAUSE)

        # Шаг 2: пустой ввод
        print("[Тест 2] Шаг 2 — пустые транзакции...")
        self._open_dfs()
        self._set_threshold(2)
        self._set_mode("manual")
        self._set_transactions("")
        self._submit()
        self._wait_result()
        body = self._body()
        self.assertTrue(
            any(p in body for p in ["не может быть пустым", "ошибк", "Ошибк", "пуст"]),
            "Ожидалась ошибка при пустом вводе"
        )
        time.sleep(PAUSE)

        # Шаг 3: отправитель == получатель
        print("[Тест 2] Шаг 3 — отправитель совпадает с получателем...")
        self._open_dfs()
        self._set_threshold(2)
        self._set_mode("manual")
        self._set_transactions("wallet_A wallet_A 100.00 1000\n")
        self._submit()
        self._wait_result()
        body = self._body()
        self.assertTrue(
            any(p in body for p in ["совпадают", "корректн", "ошибк", "Ошибк"]),
            "Ожидалась ошибка: отправитель == получатель"
        )
        time.sleep(PAUSE)

        # Шаг 4: порог вне диапазона
        print("[Тест 2] Шаг 4 — порог 999...")
        self._open_dfs()
        self._set_threshold(999)
        self._set_mode("manual")
        self._set_transactions(VALID_TX)
        self._submit()
        self._wait_result()
        self.assertIn("Порог", self._body(), "Ожидалась ошибка валидации порога")

        print("[Тест 2] ПРОЙДЕН")

    # Тест 3: большой объём данных из файла 

    def test_3_large_file_input(self):
        """
        Ключевой тест: данные считываются из файлов Python-кодом,
        затем передаются на страницу через скрытую textarea.

        Проверяет:
        - 30 корректных транзакций из test_data_large.txt принимаются
        - время обработки < 15 секунд
        - тот же файл с порогом 2 и порогом 20 — нет HTTP 500
        - файл test_data_invalid.txt → ошибка парсинга
        """
        transactions = read_file(LARGE_DATA_FILE)
        line_count   = sum(1 for l in transactions.splitlines() if l.strip())

        # Шаг 1: большой файл, порог 3
        print(f"\n[Тест 3] Шаг 1 — {line_count} транзакций из файла, порог=3...")
        self._open_dfs()
        self._set_threshold(3)
        self._set_mode("manual")
        self._set_transactions(transactions)
        start = time.time()
        self._submit()
        self._wait_result()
        elapsed = time.time() - start
        body = self._body()
        self.assertNotIn("Не найдено ни одной корректной транзакции", body,
                         f"Все {line_count} строк должны быть приняты")
        self.assertLess(elapsed, 15,
                        f"Обработка заняла {elapsed:.1f}с > 15с")
        print(f"[Тест 3] Обработано {line_count} строк за {elapsed:.2f}с")
        time.sleep(PAUSE)

        # Шаг 2: тот же файл, порог 2
        print("[Тест 3] Шаг 2 — тот же файл, порог=2...")
        self._open_dfs()
        self._set_threshold(2)
        self._set_mode("manual")
        self._set_transactions(transactions)
        self._submit()
        self._wait_result()
        self.assertNotIn("500", self.driver.title, "HTTP 500 при пороге 2")
        self.assertNotIn("Не найдено ни одной корректной транзакции", self._body())
        time.sleep(PAUSE)

        # Шаг 3: тот же файл, порог 20
        print("[Тест 3] Шаг 3 — тот же файл, порог=20...")
        self._open_dfs()
        self._set_threshold(20)
        self._set_mode("manual")
        self._set_transactions(transactions)
        self._submit()
        self._wait_result()
        self.assertNotIn("500", self.driver.title, "HTTP 500 при пороге 20")
        time.sleep(PAUSE)

        # Шаг 4: невалидный файл
        print("[Тест 3] Шаг 4 — невалидные данные из файла...")
        invalid_tx = read_file(INVALID_DATA_FILE)
        self._open_dfs()
        self._set_threshold(2)
        self._set_mode("manual")
        self._set_transactions(invalid_tx)
        self._submit()
        self._wait_result()
        body = self._body()
        self.assertTrue(
            any(p in body for p in ["корректн", "Ошибк", "ошибк", "некорректн", "пуст"]),
            "Ожидалась ошибка для невалидного файла"
        )

        print("[Тест 3] ПРОЙДЕН")


# Точка входа

if __name__ == "__main__":
    for path in (LARGE_DATA_FILE, INVALID_DATA_FILE):
        if not os.path.exists(path):
            print(f"ПРЕДУПРЕЖДЕНИЕ: файл не найден: {path}")

    unittest.main(verbosity=2)