# -*- coding: utf-8 -*-
import json
import random
import re
import io
import zipfile
from bottle import route, post, run, template, static_file, request, response

# Импорты модулей проекта
from tools.tsp_tools import generate_random_graph, log_to_file
from validators.tsp_validator import parse_input, parse_txt_file
from visual.tsp_visual import build_svg
from algorithms.tsp_algorithm import solve_tsp, get_full_path, dijkstra_simple

from tools.dfs_tools import generate_transactions, transactions_to_text
from validators.dfs_validator import parse_transactions, filter_valid, validate_params
from algorithms.dfs_algorithm import find_longest_path
from visual.dfs_visual import render_graph_svg, render_graph_html

from algorithms.bfs_algorithm import ProbabilisticBFS
from validators.bfs_validator import validate_bfs_params
from visual.bfs_visual import create_graph_from_edges, generate_graph_svg, generate_infection_chart
from tools.bfs_tools import parse_bfs_config_file, generate_random_bfs_network

import pickle
import os
import json
from tools.tsp_tools import generate_random_graph
from bottle import route, view, static_file, run, template, request, response
from tools.dfs_tools    import generate_transactions, transactions_to_text
from validators.dfs_validator import parse_transactions, filter_valid, validate_params
from algorithms.dfs_algorithm import find_longest_path
from visual.dfs_visual    import render_graph_svg, render_graph_html
from tools.tsp_tools import generate_random_graph, build_zip,log_to_file
from validators.tsp_validator import parse_input, parse_txt_file
from visual.tsp_visual import build_svg
from algorithms.tsp_algorithm import solve_tsp, get_full_path,dijkstra_simple

@route('/favicon.ico')
def favicon():
    return static_file('favicon.ico', root='./static')


@route('/')
def index():
    return template('index', title='Описание задач', year=2026, request_path=request.path)


# --- JSON-эндпоинт: генерация случайных транзакций ---
@route('/dfs/random-json', method=['POST'])
def dfs_random_json():
    response.content_type = 'application/json'
    try:
        tx_count     = int(request.forms.get('tx_count',     '10'))
        wallet_count = int(request.forms.get('wallet_count', '6'))
        tx_count     = max(1, min(200, tx_count))
        wallet_count = max(2, min(50,  wallet_count))
    except ValueError:
        tx_count, wallet_count = 10, 6

    txs = generate_transactions(tx_count=tx_count, wallet_count=wallet_count)
    raw = transactions_to_text(txs)
    parsed_rows, _ = parse_transactions(raw)
    rows = [
        {
            'sender':    r.get('sender',    ''),
            'receiver':  r.get('receiver',  ''),
            'amount':    str(r.get('amount',    '')),
            'timestamp': str(r.get('timestamp', '')),
        }
        for r in parsed_rows if r.get('valid', True)
    ]
    return json.dumps({'rows': rows})


def _read_file(file_obj):
    if not file_obj:
        return ''
    try:
        return file_obj.file.read().decode('utf-8')
    except Exception:
        return ''


# --- Основной роут DFS ---
@route('/dfs', method=['GET', 'POST'])
def dfs_module():
    defaults = dict(
        title='Модуль DFS',
        year=2026,
        request_path=request.path,
        threshold=4,
        tx_count=10,
        wallet_count=6,
        transactions='',
        input_mode='manual',
        errors={},
        error=None,
        graph_html=None,
        result=None,
        parsed_file=[],
    )

    if request.method != 'POST':
        return template('dfs', **defaults)

    mode         = request.forms.get('input_mode', 'manual')
    threshold_s  = request.forms.get('threshold',    '4')
    tx_count_s   = request.forms.get('tx_count',     '10')
    wallet_cnt_s = request.forms.get('wallet_count', '6')

    defaults['input_mode']   = mode
    defaults['threshold']    = threshold_s
    defaults['tx_count']     = tx_count_s
    defaults['wallet_count'] = wallet_cnt_s

    param_errors = validate_params(threshold_s, tx_count_s, wallet_cnt_s)
    if param_errors:
        defaults['errors']       = param_errors
        defaults['transactions'] = request.forms.get('transactions', '')
        return template('dfs', **defaults)

    threshold = int(threshold_s)
    tx_count = int(tx_count_s)
    wallet_count = int(wallet_cnt_s)

    if mode == 'random':
        txs = generate_transactions(tx_count=tx_count, wallet_count=wallet_count)
        raw = transactions_to_text(txs)
    elif mode == 'file':
        raw = _read_file(request.files.get('tx_file'))
        if not raw.strip():
            defaults['errors'] = {'tx_file': 'Файл пуст или не удалось прочитать.'}
            return template('dfs', **defaults)
    else:  # manual
        raw = request.forms.get('transactions', '').strip()

    defaults['transactions'] = raw

    parsed_rows, global_errors = parse_transactions(raw)
    defaults['parsed_file'] = parsed_rows

    if global_errors:
        defaults['errors'] = {'transactions': ' '.join(global_errors)}
        return template('dfs', **defaults)

    valid_txs = filter_valid(parsed_rows)
    if not valid_txs:
        defaults['errors'] = {'transactions': 'Нет корректных транзакций для анализа.'}
        return template('dfs', **defaults)

    result = find_longest_path(valid_txs, threshold=threshold)
    graph_html = render_graph_html(valid_txs, suspicious_paths=result['paths'], container_height=520)
    defaults['graph_html'] = graph_html
    defaults['result']     = result

    return template('dfs', **defaults)


def _tsp_defaults():
    return dict(title='Модуль TSP', year=2026, request_path=request.path)


@route('/tsp', method='GET')
def tsp_get():
    return template('tsp', **_tsp_defaults())

@route('/tsp/random', method='POST')
def tsp_random():
    raw = generate_random_graph()
    form = {'n': raw['n'], 'm': raw['m'], 'k': raw['k'], 'sites': raw['sites']}
    for i, line in enumerate(raw['edges'].strip().splitlines(), 1):
        parts = line.strip().split()
        if len(parts) == 3:
            form[f'u_{i}'] = parts[0]
            form[f'v_{i}'] = parts[1]
            form[f'w_{i}'] = parts[2]
    return template('tsp', **_tsp_defaults(), form=form, errors={})

@route('/tsp/download/<result_id>', method='GET')
def tsp_download(result_id):
    path = f'tmp_results/{result_id}.pkl'
    if not os.path.exists(path):
        return 'Данные устарели или не найдены'

    with open(path, 'rb') as f:
        data = pickle.load(f)

    zip_buf = build_zip(
        graph_data={
            'graph':       data['graph'],
            'best_path':   data['best_path'],
            'full_path':   data['full_path'],
            'hotel':       data['hotel'],
            'unreachable': data['unreachable']
        },
        form_data={'hotel': data['log']['hotel'], 'targets': data['log']['targets']},
        result_data={'path': data['log']['path'], 'dist': data['log']['dist']}
    )

    response.content_type = 'application/zip'
    response.headers['Content-Disposition'] = 'attachment; filename="tsp_result.zip"'
    return zip_buf.getvalue()

@route('/tsp', method='POST')
def tsp_post():

#  Загрузка из файла
    upload = request.files.get('txt_file')
    if upload and upload.filename:
        filename = upload.filename.lower()
        if not filename.endswith(('.txt', '.json')):
            return template(
                'tsp',
                **_tsp_defaults(),
                errors={'global': 'Можно загружать только файлы формата .txt или .json'}
            )
        try:
            content = upload.file.read().decode('utf-8')
        except Exception:
            return template('tsp', **_tsp_defaults(), errors={'global': 'Не удалось прочитать файл'})

        # JSON формат
        if filename.endswith('.json'):
            try:
                import json
                data = json.loads(content)
                form_data = {
                    'n':     str(data['n']),
                    'm':     str(data['m']),
                    'k':     str(data['k']),
                    'sites': ' '.join(str(s) for s in data['sites']),
                    'edges': '\n'.join(f"{e['u']} {e['v']} {e['w']}" for e in data['edges']),
                }
                errors = {}
            except Exception:
                return template(
                    'tsp',
                    **_tsp_defaults(),
                    errors={'global': 'Неверный формат JSON. Ожидается: {"n":..,"m":..,"k":..,"sites":[..],"edges":[{"u":.,"v":.,"w":..}]}'}
                )
        else:
            form_data, errors = parse_txt_file(content)

        if errors:
            return template('tsp', **_tsp_defaults(), form=form_data, errors=errors)

        form = {
            'n': form_data['n'],
            'm': form_data['m'],
            'k': form_data['k'],
            'sites': form_data['sites']
        }
        for i, line in enumerate(form_data['edges'].splitlines(), 1):
            parts = line.split()
            if len(parts) == 3:
                form[f'u_{i}'] = parts[0]
                form[f'v_{i}'] = parts[1]
                form[f'w_{i}'] = parts[2]

        return template('tsp', **_tsp_defaults(), form=form, errors={})

    n_raw = request.forms.get('n', '').strip()
    m = request.forms.get('m', '').strip()
    k = request.forms.get('k', '').strip()
    sites = request.forms.get('sites', '').strip()

    edges_lines = []
    form = {'n': n_raw, 'm': m, 'k': k, 'sites': sites}

    i = 1
    while True:
        u = request.forms.get(f'u_{i}', '').strip()
        v = request.forms.get(f'v_{i}', '').strip()
        w = request.forms.get(f'w_{i}', '').strip()

        if u == '' and v == '' and w == '':
            if not any(request.forms.get(f'u_{j}') for j in range(i + 1, i + 3)):
                break
        else:
            form[f'u_{i}'] = u
            form[f'v_{i}'] = v
            form[f'w_{i}'] = w
            if u and v and w:
                edges_lines.append(f'{u} {v} {w}')
        i += 1
        if i > 500:
            break

    edges_text = '\n'.join(edges_lines)

    # 3. Валидация
    graph, hotel, targets, errors = parse_input(
        n_raw,
        m,
        edges_text,
        k,
        sites
    )

    if errors:
        return template('tsp', **_tsp_defaults(), form=form, errors=errors)
    dists = dijkstra_simple(graph, hotel)
    unreachable = [
        t for t in targets
        if dists.get(t, float('inf')) == float('inf')
    ]
   

    if unreachable:
        svg_html = build_svg(graph, best_path=None, full_path=None,
                             hotel=hotel, unreachable=unreachable)
    
        if len(unreachable) == 1:
            msg = f'Вершина {unreachable[0]} недостижима из отеля {hotel}!'
        else:
            msg = f'Вершины {", ".join(unreachable)} недостижимы из отеля {hotel}!'
    
        return template('tsp', **_tsp_defaults(), form=form, svg_html=svg_html,
                        errors={'global': msg})

    # 5. Решение TSP
    best_path, min_dist = solve_tsp(
        graph,
        hotel,
        targets
    )

    if best_path is None:
        return template('tsp', **_tsp_defaults(), form=form, errors={'global': 'Маршрут не найден'})

        return template(
            'tsp',
            **_tsp_defaults(),
            form=form,
            errors={'global': 'Маршрут не найден'}
        )

    # 6. Полный маршрут
    full_visual_path = get_full_path(
        graph,
        best_path
    )
    # 7. запись в файл
    log_to_file(
    form_data={'hotel': hotel, 'targets': targets},
    result_data={'path': full_visual_path, 'dist': min_dist}
)
    # 8. Визуализация

    svg_html = build_svg(
        graph,
        best_path=best_path,
        full_path=full_visual_path,
        hotel=hotel,
        total_dist=min_dist
    )
    result = {
        'path_str': ' → '.join(best_path),
        'full_path_str': ' → '.join(full_visual_path) if full_visual_path else '',
        'min_weight': min_dist,
    }
    return template('tsp', **_tsp_defaults(), form=form, errors={}, result=result, svg_html=svg_html)


@route('/static/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root='./static')



@route('/bfs')
def bfs_home():
    default_form = {
        'n': '10',
        'm': '12',
        'p': '0.5',
        'iter': '100',
        'v_inf': '1'
    }
    return template('bfs.tpl', 
                    title='Эпидемиология', 
                    year=2026, 
                    request_path=request.path, 
                    form=default_form, 
                    errors={}, 
                    result=None, 
                    svg_html=None)


@post('/bfs/random')
def bfs_random():
    # Собираем то, что пользователь успел ввести на форме (если ввёл)
    n_raw = request.forms.get('n', '10')
    m_raw = request.forms.get('m', '12')
    p_raw = request.forms.get('p', '0.3')
    iter_raw = request.forms.get('iter', '50')

    # Вызываем функцию генерации
    form_data = generate_random_bfs_network(n_raw, m_raw, p_raw, iter_raw)

    # Отдаем промежуточный результат в таблицу рёбер
    return template('bfs.tpl', 
                    title='Эпидемиология', 
                    year=2026, 
                    request_path=request.path, 
                    form=form_data, 
                    errors={}, 
                    result=None, 
                    svg_html=None)


# Глобальный буфер для хранения данных последней успешной симуляции
current_bfs_data = None

@post('/bfs')
def bfs_simulate():
    global current_bfs_data
    form_data = dict(request.forms)

    upload = request.files.get('txt_file')
    if upload and upload.filename:
        file_form_data, file_errors = parse_bfs_config_file(upload)
        if file_errors:
            return template('bfs.tpl', title='Эпидемиология', year=2026, request_path=request.path, form=form_data, errors=file_errors, result=None, svg_html=None)
        form_data.update(file_form_data)

   
    validated_data, errors = validate_bfs_params(form_data)

    # Достаем отвалидированные бэкендом чистые переменные
    n = validated_data.get('n', 10)
    p = validated_data.get('p', 0.5)
    iterations = validated_data.get('iter', 100)
    start_nodes = validated_data.get('v_inf', [1])
    v_inf_str = form_data.get('v_inf', '1')

  # Сбор рёбер из таблицы формы с жесткой валидацией на пустые поля
    edges = []
    edge_idx = 1
    has_empty_fields = False

    while True:
        # Важно: используем дефолтный None, чтобы поймать реальный конец переданных полей
        u_raw = form_data.get(f'u_{edge_idx}', None)
        v_raw = form_data.get(f'v_{edge_idx}', None)
        
        # Если этих полей вообще нет в POST-запросе, значит таблица точно кончилась
        if u_raw is None and v_raw is None:
            break

        u_val = u_raw.strip()
        v_val = v_raw.strip()

        # Если хотя бы одно поле пустое, либо оба поля пустые в существующей строке формы
        if not u_val or not v_val:
            has_empty_fields = True
            break

        # Если оба поля заполнены, валидируем числа
        try:
            u, v = int(u_val), int(v_val)
            if 1 <= u <= n and 1 <= v <= n and u != v:
                if (u, v) not in edges and (v, u) not in edges:
                    edges.append((u, v))
            else:
                errors['edges'] = f'Номера узлов в строке {edge_idx} должны быть от 1 до {n} и не равны друг другу.'
                break
        except ValueError:
            errors['edges'] = f'В строке {edge_idx} введены некорректные символы. Ожидаются числа.'
            break

        edge_idx += 1
        if edge_idx > 200: 
            break

    # Выставляем общие ошибки для таблицы рёбер
    if has_empty_fields:
        errors['edges'] = 'Таблица рёбер содержит незаполненные поля! Пожалуйста, закройте/удалите лишние строки или заполните их.'
    elif not edges and not errors.get('n') and not errors.get('m'):
        errors['edges'] = 'Добавьте хотя бы одно ребро'

    # Если есть ошибки (от валидатора параметров или по рёбрам) — рендерим форму обратно
    if errors:
        return template('bfs.tpl', title='Эпидемиология', year=2026, request_path=request.path, form=form_data, errors=errors, result=None, svg_html=None)

    # Сохраняем успешные данные в глобальный буфер
    current_bfs_data = {
        'n': n, 'm': form_data.get('m', '?'), 'p': p, 'iter': iterations, 'v_inf': v_inf_str, 'edges': edges
    }

    # Запуск симуляции (остальной код функции до конца остаётся без изменений)
    graph = create_graph_from_edges(n, edges)
    simulator = ProbabilisticBFS(graph, p=p)
    sim_results = simulator.monte_carlo_simulation(start_nodes, iterations)

    chart_b64 = generate_infection_chart(sim_results['timeline'], n_nodes = n)
    svg_html = generate_graph_svg(graph, start_nodes, sim_results['infection_frequencies'])

    result = {
        'connectivity_max': sim_results.get('max_possible_reach', n),
        'v_mean': f"{sim_results.get('avg_duration', 0.0):.2f}",
        'p_final': f"{sim_results.get('avg_infected_percentage', 0.0):.1f}",
        'avg_infected_count': int(sim_results.get('avg_infected_count', 0)),
        'iterations': iterations,
        'max_infected': sim_results.get('max_infected', n),
        'min_infected': sim_results.get('min_infected', 0),
        'most_common_infected': sim_results.get('most_common_pattern', []),
        'most_common_percent': f"{sim_results.get('pattern_probability', 0.0):.1f}",
        'chart_base64': chart_b64
    }

    return template('bfs.tpl', title='Эпидемиология', year=2026, request_path=request.path, form=form_data, errors={}, result=result, svg_html=svg_html)


@route('/bfs/download-results', method='GET')
def download_bfs_results():
    global current_bfs_data
    
    if not current_bfs_data:
        response.status = 400
        return "Нет данных для скачивания. Сначала запустите симуляцию."

    # Извлекаем сохранённые данные
    n = current_bfs_data['n']
    m = current_bfs_data['m']
    p = current_bfs_data['p']
    iterations = current_bfs_data['iter']
    v_inf = current_bfs_data['v_inf']
    edges = current_bfs_data['edges']

    # 1. Формируем текстовый отчёт
    stats_content = f"""==================================================
ОТЧЁТ О МОДЕЛИРОВАНИИ РАСПРОСТРАНЕНИЯ ВИРУСА
==================================================
Параметры запуска:
- Количество узлов (N): {n}
- Количество очагов/рёбер (M): {m}
- Вероятность заражения (p): {p}
- Число итераций Монте-Карло (I): {iterations}
- Начальные очаги заражения: {v_inf}

Список связей графа (Рёбра):
"""
    dot_edges = ""
    for idx, (u, v) in enumerate(edges, 1):
        stats_content += f"Ребро #{idx}: Узел {u} <-> Узел {v}\n"
        dot_edges += f"  {u} -- {v};\n"

    stats_content += "\n==================================================\n"
    stats_content += "Статистика посчитана на момент выгрузки архива.\n"

    # 2. Генерируем SVG-код графа для архива
    # Передаем пустой словарь частот или базовые значения, чтобы просто построить сетку
    try:
        graph_obj = create_graph_from_edges(n, edges)
        # Парсим начальные узлы для корректной подсветки на картинке
        start_nodes = [int(x) for x in v_inf.replace(',', ' ').split() if x.strip().isdigit()]
        if not start_nodes:
            start_nodes = [1]
            
        # Строим SVG-структуру графа
        svg_string = generate_graph_svg(graph_obj, start_nodes, {})
    except Exception:
        svg_string = None

    # 3. Создание ZIP в памяти
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Добавляем текст и dot-нотацию
        zip_file.writestr("simulation_statistics.txt", stats_content)
        
        # Если SVG успешно сгенерировался — бережно кладем его в архив
        if svg_string:
            zip_file.writestr("graph_visualization.svg", svg_string)

    zip_buffer.seek(0)

    response.set_header('Content-Type', 'application/zip')
    response.set_header('Content-Disposition', 'attachment; filename=bfs_simulation_results.zip')
    
    return zip_buffer.getvalue()



@route('/about')
def about():
    return template('about', title='Об авторах', year=2026, request_path=request.path)


if __name__ == '__main__':
    run(host='localhost', port=8080, debug=True, reloader=True)