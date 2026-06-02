import random
import datetime
import json
import zipfile
import io
from flask import send_file
from visual.tsp_visual import _build_fig
import matplotlib.pyplot as plt

# Генерирует случайный гарантированно связный граф для тестирования алгоритма TSP.
def generate_random_graph(n=None, m=None):    
    #  выбираем случайно от 5 до 20
    if n is None:
        n = random.randint(5, 20)
    #  выбираем от 2 до 6 (или n-1)
    if m is None:
        m = random.randint(2, min(6, n - 1))

    # Номер вершины отеля выбирается случайно из всего диапазона вершин
    k = random.randint(1, n)

    # Инициализируем структуры для хранения уникальных рёбер графа
    edges = set()       
    edge_list = []      # Финальный список рёбер в формате (откуда, куда, вес)

    # Это гарантирует, что граф будет связным (без изолированных островов)
    vertices = list(range(1, n + 1))
    random.shuffle(vertices)  # Перемешиваем вершины для случайного порядка соединения
    
    for i in range(1, len(vertices)):
        u = vertices[i]
        # Присоединяем текущую вершину к одной из уже подключенных ранее
        v = vertices[random.randint(0, i - 1)]
        w = random.randint(1, 20)  # Случайный вес ребра
        
        edge = (min(u, v), max(u, v))
        if edge not in edges:
            edges.add(edge)
            edge_list.append((u, v, w))

    # Все кроме отеля
    candidates = [v for v in range(1, n + 1) if v != k]
    sites = random.sample(candidates, min(m, len(candidates)))

    # Создаём полный подграф между отелем и достопримечательностями.
    key_nodes = [k] + sites
    for i in range(len(key_nodes)):
        for j in range(i + 1, len(key_nodes)):
            u, v = key_nodes[i], key_nodes[j]
            edge = (min(u, v), max(u, v))
            # Если прямой дороги между ними ещё нет — создаём её
            if edge not in edges:
                edges.add(edge)
                w = random.randint(1, 20)
                edge_list.append((u, v, w))

    #  Добавление случайных рёбер для плотности графа ---
    extra    = random.randint(n // 2, n)  # Количество дополнительных дорог
    target   = len(edge_list) + extra
    attempts = 0
    
    # Пытаемся накидать случайных рёбер, пока не достигнем цели или лимита попыток
    while len(edge_list) < target and attempts < extra * 5:
        u = random.randint(1, n)
        v = random.randint(1, n)
        if u != v:
            edge = (min(u, v), max(u, v))
            if edge not in edges:
                edges.add(edge)
                w = random.randint(1, 20)
                edge_list.append((u, v, w))
        attempts += 1

    # Повторный срез на случай, если структура пересобиралась (страховка консистентности)
    candidates = [v for v in range(1, n + 1) if v != k]
    sites = random.sample(candidates, min(m, len(candidates)))

    # Возвращаем словарь в текстовом формате, готовом для вставки в поля веб-формы
    return {
        'n':      str(n),
        'm':      str(m),
        'k':      str(k),
        'edges': '\n'.join(f'{u} {v} {w}' for u, v, w in edge_list),
        'sites': ' '.join(str(s) for s in sites),
    }

#  Логирует каждый расчёт 
def log_to_file(form_data, result_data, errors=None):
    log_entry = {
        'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'input': form_data,
        'result': result_data,
        'errors': errors
    }
    # Открываем файл в режиме дозаписи ('a' - append)
    with open('tsp_history.json', 'a', encoding='utf-8') as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')

#  Упаковывает результаты вычислений в ZIP-архив 
def build_zip(graph_data, form_data, result_data, errors=None):
    # Формируем структуру будущего JSON-файла с результатами
    log_entry = {
        'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'input': form_data,
        'result': result_data,
        'errors': errors
    }
    
    # Создаём байтовый буфер в оперативной памяти для хранения самого ZIP-архива
    buf = io.BytesIO()
    
    # Открываем контекстный менеджер для записи файлов внутрь архива
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
        # 1. Записываем файл результатов в формате красивого отформатированного JSON
        zf.writestr('result.json', json.dumps(log_entry, ensure_ascii=False, indent=2))

        # 2. Генерируем картинку графа с помощью внутренней функции построения фигуры
        fig = _build_fig(**graph_data)
        
        # Создаём отдельный байтовый буфер для временного сохранения картинки
        img_buf = io.BytesIO()
        fig.savefig(img_buf, format='png', bbox_inches='tight',
                    facecolor=fig.get_facecolor())
        plt.close(fig)  # Освобождаем оперативную память сервера, уничтожая фигуру
        
        img_buf.seek(0)  # Сбрасываем указатель каретки в начало буфера картинки
        # Записываем полученные бинарные данные PNG внутрь ZIP-архива
        zf.writestr('graph.png', img_buf.getvalue())

    # Сбрасываем указатель каретки ZIP-архива в начало, чтобы Flask мог начать его чтение для отправки
    buf.seek(0)
    return buf