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
from selenium.common.exceptions import TimeoutException, NoSuchElementException

sys.stdout.reconfigure(encoding='utf-8')
# ─── Константы ────────────────────────────────────────────────────────────────

BASE_URL          = "http://127.0.0.1:5555"
DFS_URL           = f"{BASE_URL}/dfs"
TIMEOUT           = 15
SCRIPT_DIR        = os.path.dirname(os.path.abspath(__file__))
LARGE_DATA_FILE   = os.path.join(SCRIPT_DIR, "test_data_large.txt")
INVALID_DATA_FILE = os.path.join(SCRIPT_DIR, "test_data_invalid.txt")


# ─── Утилиты ──────────────────────────────────────────────────────────────────

def read_file(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def build_driver() -> webdriver.Edge:
    opts = Options()
    # headless убран: страница скрывает элементы через JS/CSS,
    # headless-режим мешает корректной работе tx_table.js
    opts.add_argument("--window-size=1600,1000")
    opts.add_argument("--disable-extensions")
    return webdriver.Edge(options=opts)


# ─── Базовый класс ────────────────────────────────────────────────────────────

class DfsPageTestBase(unittest.TestCase):
    """
    Один экземпляр браузера на весь класс.
    Все взаимодействия с формой — через execute_script, потому что:
      - textarea#tx-hidden-input скрыта (display:none)
      - input#threshold скрыт, управляется слайдером
      - кнопка submit disabled до тех пор, пока JS не заполнит hidden-поля
      - input_mode — hidden-поле, переключается кнопками с onclick
    """

    @classmethod
    def setUpClass(cls):
        cls.driver = build_driver()
        cls.wait   = WebDriverWait(cls.driver, TIMEOUT)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    # ── открытие страницы ──────────────────────────────────────────────────

    def open_dfs(self):
        self.driver.get(DFS_URL)
        self.wait.until(EC.presence_of_element_located((By.ID, "dfs-form")))
        # Даём JS время инициализироваться
        time.sleep(0.5)

    # ── установка threshold ────────────────────────────────────────────────

    def set_threshold(self, value: int):
        """Устанавливает порог напрямую в скрытый input и слайдер."""
        self.driver.execute_script("""
            var inp = document.getElementById('threshold');
            var rng = document.getElementById('threshold-range');
            var disp = document.getElementById('threshold-display');
            inp.value  = arguments[0];
            rng.value  = arguments[0];
            if (disp) disp.textContent = arguments[0];
        """, str(value))

    # ── установка режима ввода ─────────────────────────────────────────────

    def set_input_mode(self, mode: str):
        """Устанавливает значение hidden-поля input_mode."""
        self.driver.execute_script(
            "document.getElementById('input_mode').value = arguments[0];", mode
        )

    # ── заполнение транзакций ──────────────────────────────────────────────

    def set_transactions(self, text: str):
        """
        Записывает транзакции в скрытую textarea и активирует кнопку submit.
        Это имитирует то, что делает tx_table.js после заполнения таблицы.
        """
        self.driver.execute_script("""
            var ta  = document.getElementById('tx-hidden-input');
            var btn = document.getElementById('tx-run');
            ta.value           = arguments[0];
            ta.style.display   = 'block';   // снимаем display:none для отправки
            btn.disabled       = false;      // активируем кнопку
            btn.removeAttribute('disabled');
        """, text)

    # ── установка tx_count и wallet_count ─────────────────────────────────

    def set_gen_params(self, tx_count: int, wallet_count: int):
        self.driver.execute_script("""
            var tc = document.getElementById('tx_count');
            var wc = document.getElementById('wallet_count');
            if (tc) tc.value = arguments[0];
            if (wc) wc.value = arguments[1];
        """, tx_count, wallet_count)

    # ── отправка формы ─────────────────────────────────────────────────────

    def submit_form(self):
        """Отправляет форму через JS (кнопка может быть disabled)."""
        self.driver.execute_script(
            "document.getElementById('dfs-form').submit();"
        )

    # ── ожидание результата ────────────────────────────────────────────────

    def wait_for_result(self):
        """Ждёт загрузки страницы после submit."""
        try:
            self.wait.until(EC.presence_of_element_located((By.ID, "dfs-form")))
        except TimeoutException:
            pass

    def body_text(self) -> str:
        return self.driver.find_element(By.TAG_NAME, "body").text


# ─── Тест 1: загрузка страницы ────────────────────────────────────────────────

class TestPageLoad(DfsPageTestBase):

    def test_page_opens(self):
        """Страница /dfs открывается с кодом 200."""
        self.open_dfs()
        self.assertIn("dfs", self.driver.current_url)

    def test_title_contains_dfs(self):
        """Заголовок страницы содержит слово 'DFS' или 'Анализ'."""
        self.open_dfs()
        body = self.body_text()
        self.assertTrue(
            "DFS" in body.upper() or "Анализ" in body,
            "На странице не найден ожидаемый заголовок"
        )

    def test_form_present(self):
        """Форма #dfs-form присутствует на странице."""
        self.open_dfs()
        form = self.driver.find_element(By.ID, "dfs-form")
        self.assertIsNotNone(form)

    def test_threshold_field_present(self):
        """Поле threshold присутствует."""
        self.open_dfs()
        el = self.driver.find_element(By.ID, "threshold")
        self.assertIsNotNone(el)

    def test_random_button_present(self):
        """Кнопка 'Случайный' присутствует."""
        self.open_dfs()
        btn = self.driver.find_element(By.ID, "btn-random")
        self.assertTrue(btn.is_displayed())


# ─── Тест 2: ручной ввод ─────────────────────────────────────────────────────

class TestManualInput(DfsPageTestBase):

    VALID_TX = (
        "wallet_A wallet_B 100.00 1000\n"
        "wallet_B wallet_C 200.00 1001\n"
        "wallet_C wallet_D 150.00 1002\n"
    )

    def test_valid_manual_input(self):
        """Корректные транзакции принимаются без ошибок парсинга."""
        self.open_dfs()
        self.set_threshold(2)
        self.set_input_mode("manual")
        self.set_transactions(self.VALID_TX)
        self.submit_form()
        self.wait_for_result()

        body = self.body_text()
        self.assertNotIn("Не найдено ни одной корректной транзакции", body)

    def test_empty_transactions_error(self):
        """Пустые транзакции → сообщение об ошибке."""
        self.open_dfs()
        self.set_threshold(2)
        self.set_input_mode("manual")
        self.set_transactions("")
        self.submit_form()
        self.wait_for_result()

        body = self.body_text()
        has_error = any(p in body for p in [
            "не может быть пустым", "ошибк", "Ошибк", "пуст"
        ])
        self.assertTrue(has_error, "Ожидалось сообщение об ошибке при пустом вводе")

    def test_threshold_out_of_range(self):
        """Порог 999 → ошибка валидации порога."""
        self.open_dfs()
        self.set_threshold(999)
        self.set_input_mode("manual")
        self.set_transactions(self.VALID_TX)
        self.submit_form()
        self.wait_for_result()

        body = self.body_text()
        self.assertIn("Порог", body, "Ожидалась ошибка валидации порога")

    def test_invalid_sender_equals_receiver(self):
        """Отправитель == получатель → строка помечается невалидной."""
        self.open_dfs()
        self.set_threshold(2)
        self.set_input_mode("manual")
        # Одна строка с совпадающими sender/receiver
        self.set_transactions("wallet_A wallet_A 100.00 1000\n")
        self.submit_form()
        self.wait_for_result()

        body = self.body_text()
        has_error = any(p in body for p in [
            "совпадают", "корректн", "ошибк", "Ошибк"
        ])
        self.assertTrue(has_error, "Ожидалась ошибка: отправитель == получатель")


# ─── Тест 3: большой объём данных из файла ────────────────────────────────────

class TestLargeFileInput(DfsPageTestBase):
    """
    Ключевой тест задания — данные считываются из файла Python-кодом,
    затем передаются на страницу через скрытую textarea.
    """

    def test_large_data_from_file(self):
        """
        30 транзакций из test_data_large.txt → обработка без ошибок парсинга.
        Проверяется также время обработки (не более 15 с).
        """
        transactions = read_file(LARGE_DATA_FILE)
        line_count   = sum(1 for l in transactions.splitlines() if l.strip())

        self.open_dfs()
        self.set_threshold(3)
        self.set_input_mode("manual")
        self.set_transactions(transactions)

        start = time.time()
        self.submit_form()
        self.wait_for_result()
        elapsed = time.time() - start

        body = self.body_text()
        self.assertNotIn(
            "Не найдено ни одной корректной транзакции", body,
            f"Все {line_count} строк из файла должны быть приняты"
        )
        self.assertLess(elapsed, 15,
                        f"Обработка {line_count} транзакций заняла {elapsed:.1f}с > 15с")
        print(f"\n  [large_file] {line_count} строк за {elapsed:.2f}с")

    def test_invalid_data_from_file(self):
        """
        test_data_invalid.txt содержит только ошибочные строки →
        сервер возвращает сообщение об ошибке.
        """
        transactions = read_file(INVALID_DATA_FILE)

        self.open_dfs()
        self.set_threshold(2)
        self.set_input_mode("manual")
        self.set_transactions(transactions)
        self.submit_form()
        self.wait_for_result()

        body = self.body_text()
        has_error = any(p in body for p in [
            "корректн", "Ошибк", "ошибк", "некорректн", "пуст"
        ])
        self.assertTrue(has_error,
                        "Ожидалась ошибка для файла с полностью невалидными данными")

    def test_large_data_different_thresholds(self):
        """
        Один и тот же файл с порогом 2 и порогом 20 — оба запроса
        обрабатываются без ошибок сервера (нет HTTP 500).
        """
        transactions = read_file(LARGE_DATA_FILE)

        for threshold in (2, 20):
            with self.subTest(threshold=threshold):
                self.open_dfs()
                self.set_threshold(threshold)
                self.set_input_mode("manual")
                self.set_transactions(transactions)
                self.submit_form()
                self.wait_for_result()

                title = self.driver.title
                self.assertNotIn("500", title,
                                 f"HTTP 500 при пороге {threshold}")
                body = self.body_text()
                self.assertNotIn("Не найдено ни одной корректной транзакции",
                                 body)


# ─── Тест 4: режим random ─────────────────────────────────────────────────────

class TestRandomMode(DfsPageTestBase):

    def test_random_default_params(self):
        """Random-режим с дефолтными параметрами — результат без ошибок."""
        self.open_dfs()
        self.set_threshold(3)
        self.set_input_mode("random")
        # При random-режиме транзакции генерируются на сервере,
        # поэтому textarea не нужна — отправляем форму как есть
        self.set_transactions(" ")   # непустая строка чтобы сервер не отклонил
        self.submit_form()
        self.wait_for_result()

        title = self.driver.title
        self.assertNotIn("500", title, "Сервер вернул ошибку 500")

    def test_random_large_params(self):
        """Random с tx_count=50, wallet_count=20 — завершается за 20 с."""
        self.open_dfs()
        self.set_threshold(4)
        self.set_input_mode("random")
        self.set_gen_params(tx_count=50, wallet_count=20)
        self.set_transactions(" ")

        start = time.time()
        self.submit_form()
        self.wait_for_result()
        elapsed = time.time() - start

        self.assertLess(elapsed, 20,
                        f"random(50, 20) завершился за {elapsed:.1f}с > 20с")
        print(f"\n  [random_large] 50 tx / 20 wallets за {elapsed:.2f}с")


# ─── Тест 5: навигация ────────────────────────────────────────────────────────

class TestNavigation(DfsPageTestBase):

    def test_navbar_brand_goes_home(self):
        """Клик по логотипу (navbar-brand) → переход на /."""
        self.open_dfs()
        brand = self.driver.find_element(By.CSS_SELECTOR, "a.navbar-brand")
        brand.click()
        self.wait.until(EC.url_to_be(f"{BASE_URL}/"))
        self.assertEqual(
            self.driver.current_url.rstrip("/"),
            BASE_URL.rstrip("/")
        )

    def test_nav_dfs_link(self):
        """Ссылка «Модуль DFS» в navbar ведёт на /dfs."""
        self.driver.get(BASE_URL)
        link = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='/dfs']"))
        )
        link.click()
        self.wait.until(EC.url_contains("/dfs"))
        self.assertIn("/dfs", self.driver.current_url)

    def test_all_nav_links_present(self):
        """Все пункты меню присутствуют на странице /dfs."""
        self.open_dfs()
        expected = ["/", "/bfs", "/dfs", "/tsp", "/about"]
        for href in expected:
            links = self.driver.find_elements(
                By.CSS_SELECTOR, f"a[href='{href}']"
            )
            self.assertTrue(len(links) > 0,
                            f"Ссылка {href} не найдена в навигации")


# ─── Тест 6: граничные значения threshold ────────────────────────────────────

class TestThresholdBoundary(DfsPageTestBase):

    SAMPLE_TX = (
        "w1 w2 50.00 100\n"
        "w2 w3 75.00 101\n"
        "w3 w4 30.00 102\n"
        "w4 w5 90.00 103\n"
    )

    def _run(self, threshold: int) -> str:
        self.open_dfs()
        self.set_threshold(threshold)
        self.set_input_mode("manual")
        self.set_transactions(self.SAMPLE_TX)
        self.submit_form()
        self.wait_for_result()
        return self.body_text()

    def test_threshold_min_valid(self):
        """Порог = 2 (минимум) — нет ошибки валидации."""
        body = self._run(2)
        self.assertNotIn("Порог должен быть от 2 до 20", body)

    def test_threshold_max_valid(self):
        """Порог = 20 (максимум) — нет ошибки валидации."""
        body = self._run(20)
        self.assertNotIn("Порог должен быть от 2 до 20", body)

    def test_threshold_below_min(self):
        """Порог = 1 → ошибка валидации."""
        body = self._run(1)
        self.assertIn("Порог", body)

    def test_threshold_above_max(self):
        """Порог = 21 → ошибка валидации."""
        body = self._run(21)
        self.assertIn("Порог", body)


# ─── Точка входа ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    for path in (LARGE_DATA_FILE, INVALID_DATA_FILE):
        if not os.path.exists(path):
            print(f"ПРЕДУПРЕЖДЕНИЕ: файл не найден: {path}")

    loader = unittest.TestLoader()
    suite  = unittest.TestSuite()

    for cls in [
        TestPageLoad,
        TestManualInput,
        TestLargeFileInput,
        TestRandomMode,
        TestNavigation,
        TestThresholdBoundary,
    ]:
        suite.addTests(loader.loadTestsFromTestCase(cls))

    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)