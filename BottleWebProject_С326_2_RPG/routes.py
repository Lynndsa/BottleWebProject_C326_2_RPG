# -*- coding: utf-8 -*-
from bottle import route, run, template, static_file, request
from tools.tsp_tools import generate_random_graph, log_to_file
from validators.tsp_validator import parse_input, parse_txt_file
from visual.tsp_visual import build_svg
from algorithms.tsp_algorithm import solve_tsp, get_full_path, dijkstra_simple
import json
from tools.tsp_tools import generate_random_graph
from bottle import route, view, static_file, run, template, request, response
from tools.dfs_tools    import generate_transactions, transactions_to_text
from validators.dfs_validator import parse_transactions, filter_valid, validate_params
from algorithms.dfs_algorithm import find_longest_path
from visual.dfs_visual    import render_graph_svg, render_graph_html
from algorithms.bfs_algorithm import ProbabilisticBFS
from validators.bfs_validator import validate_bfs_params
from tools.bfs_tools import create_graph_from_edges, generate_graph_svg, generate_infection_chart
import random



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
    """Вспомогательная функция для чтения файла"""
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

    threshold    = int(threshold_s)
    tx_count     = int(tx_count_s)
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

    result     = find_longest_path(valid_txs, threshold=threshold)
    graph_html = render_graph_html(valid_txs, suspicious_paths=result['paths'],
                                   container_height=520)
    defaults['graph_html'] = graph_html
    defaults['result']     = result

    return template('dfs', **defaults)



def _tsp_defaults():
    return dict(title='Модуль TSP', year=2026, request_path=request.path)


@route('/tsp', method='GET')
def tsp_get():
    return template('tsp', **_tsp_defaults())


@route('/tsp', method='POST')
def tsp_post():

    # 1. Загрузка из TXT
    upload = request.files.get('txt_file')

    if upload and upload.filename:

        try:
            content = upload.file.read().decode('utf-8')
        except Exception:
            return template(
                'tsp',
                **_tsp_defaults(),
                errors={'global': 'Не удалось прочитать файл'}
            )

        form_data, errors = parse_txt_file(content)

        if errors:
            return template(
                'tsp',
                **_tsp_defaults(),
                form=form_data,
                errors=errors
            )

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

        return template(
            'tsp',
            **_tsp_defaults(),
            form=form,
            errors={}
        )

    # 2. Ручной ввод
    n_raw = request.forms.get('n', '').strip()
    m = request.forms.get('m', '').strip()
    k = request.forms.get('k', '').strip()
    sites = request.forms.get('sites', '').strip()

    edges_lines = []

    form = {
        'n': n_raw,
        'm': m,
        'k': k,
        'sites': sites
    }

    i = 1

    while True:

        u = request.forms.get(f'u_{i}', '').strip()
        v = request.forms.get(f'v_{i}', '').strip()
        w = request.forms.get(f'w_{i}', '').strip()

        if u == '' and v == '' and w == '':

            if not any(
                request.forms.get(f'u_{j}')
                for j in range(i + 1, i + 3)
            ):
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
        edges_text,
        k,
        sites
    )

    if errors:
        return template(
            'tsp',
            **_tsp_defaults(),
            form=form,
            errors=errors
        )

    # 4. Проверка связности
    dists = dijkstra_simple(graph, hotel)

    unreachable = [
        t for t in targets
        if dists.get(t, float('inf')) == float('inf')
    ]

    if unreachable:

        svg_html = build_svg(
            graph,
            best_path=None,
            full_path=None,
            hotel=hotel
        )

        return template(
            'tsp',
            **_tsp_defaults(),
            form=form,
            svg_html=svg_html,
            errors={
                'global':
                f'Цели {unreachable} недостижимы из отеля {hotel}!'
            }
        )

    # 5. Решение TSP
    best_path, min_dist = solve_tsp(
        graph,
        hotel,
        targets
    )

    if best_path is None:

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
    
    # 7. Запись в файл 
    log_to_file(
        form_data={'hotel': hotel, 'targets': targets},
        result_data={'path': full_visual_path, 'dist': min_dist}
    )
    # 8. Визуализация

    svg_html = build_svg(
        graph,
        best_path=best_path,
        full_path=full_visual_path,
        hotel=hotel
    )
    result = {
        'path_str': ' → '.join(best_path),
        'full_path_str': ' → '.join(full_visual_path) if full_visual_path else '',
        'min_weight': min_dist,
    }
    
    return template(
        'tsp',
        **_tsp_defaults(),
        form=form,
        errors={},
        result=result,
        svg_html=svg_html
    )

@route('/static/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root='./static')


@route('/bfs', method=['GET', 'POST'])
def bfs_simulation():
    """Главная страница симуляции BFS"""
    
    base_vars = {
        'title': 'Модуль BFS',
        'year': 2026,
        'request_path': request.path
    }
    
    if request.method == 'GET':
        return template('bfs', **base_vars, form={}, errors={}, result=None, svg_html=None)
    
    # Получаем данные из формы
    n = request.forms.get('n', '')
    m = request.forms.get('m', '')
    p = request.forms.get('p', '')
    iterations = request.forms.get('iter', '')
    v_inf_str = request.forms.get('v_inf', '')
    
    # Собираем ребра
    edges = []
    for key, value in request.forms.items():
        if key.startswith('u_'):
            index = key.split('_')[1]
            v_key = f'v_{index}'
            if v_key in request.forms:
                u_val = value.strip()
                v_val = request.forms[v_key].strip()
                if u_val and v_val:
                    edges.append((u_val, v_val))
    
    # Валидация параметров (предполагается, что функция validate_bfs_params определена)
    is_valid, errors, infected_nodes = validate_bfs_params(n, m, p, iterations, v_inf_str, edges)
    
    if not is_valid:
        return template('bfs', **base_vars, form=request.forms, errors=errors, result=None, svg_html=None)
    
    try:
        n_int = int(n)
        p_float = float(p)
        iter_int = int(iterations)
        
        # Создаем граф (гарантирует наличие узлов от 1 до n_int)
        graph = create_graph_from_edges(edges, n_int)
        
        # Строгая фильтрация очагов: они должны быть строго в диапазоне существующих узлов графа
        valid_infected = [int(node) for node in infected_nodes if int(node) in graph]
        
        if not valid_infected:
            errors['global'] = f'Начальные очаги {v_inf_str} выходят за пределы количества узлов графа (1-{n_int})'
            return template('bfs', **base_vars, form=request.forms, errors=errors, result=None, svg_html=None)
        
        # Запускаем симуляцию Монте-Карло
        bfs_sim = ProbabilisticBFS(graph, valid_infected, p_float, iter_int)
        results = bfs_sim.run_monte_carlo()
        
        # Получаем корректно выровненную динамику
        progression = bfs_sim.get_infection_progression_avg()
        
        # Генерируем медиа-контент
        chart_base64 = generate_infection_chart(progression)
        svg_html = generate_graph_svg(graph, results['infection_frequency'], valid_infected)
        
        result_data = {
            'connectivity_max': results['theoretical_max'],
            'v_mean': f"{results['avg_duration']:.2f}",
            'p_final': f"{results['infection_rate']:.1f}",
            'chart_base64': chart_base64,
            'most_common_infected': results.get('most_common_infected', []),
            'most_common_percent': f"{results.get('most_common_percent', 0):.1f}",
            'iterations': iter_int,
            'avg_infected_count': f"{results['avg_infected']:.1f}",
            'max_infected': results['max_infected'],
            'min_infected': results['min_infected']
        }
        
        return template('bfs',
                       **base_vars,
                       form=request.forms,
                       result=result_data,
                       svg_html=svg_html,
                       errors=errors)
                       
    except Exception as e:
        errors['global'] = f'Ошибка при выполнении симуляции: {str(e)}'
        return template('bfs', **base_vars, form=request.forms, errors=errors, result=None, svg_html=None)


@route('/bfs/random', method='POST')
def generate_random_network():
    """Генерирует случайную сеть и подготавливает данные для формы ввода"""
    
    base_vars = {
        'title': 'Модуль BFS',
        'year': 2026,
        'request_path': request.path
    }
    
    n_str = request.forms.get('n', '').strip()
    m_str = request.forms.get('m', '').strip()
    
    if not n_str: n_str = '10'
    if not m_str: m_str = '12'  # Изменено на 12 для большей связности по умолчанию
    
    try:
        n_int = int(n_str)
        m_int = int(m_str)
        
        # Ограничения безопасности для веб-интерфейса
        n_int = max(2, min(50, n_int))
        m_int = max(1, min(100, m_int))
        
        edges = []
        edge_set = set()
        
        # Генерация уникальных случайных ребер
        max_possible_edges = (n_int * (n_int - 1)) // 2
        actual_m = min(m_int, max_possible_edges)
        
        while len(edges) < actual_m:
            u = random.randint(1, n_int)
            v = random.randint(1, n_int)
            if u != v and (u, v) not in edge_set and (v, u) not in edge_set:
                edges.append((str(u), str(v)))
                edge_set.add((u, v))
        
        # Формируем плоский словарь данных, имитирующий заполненную форму
        form_data = {
            'n': str(n_int),
            'm': str(len(edges)),
            'p': request.forms.get('p', '0.5').strip() or '0.5',
            'iter': request.forms.get('iter', '100').strip() or '100'
        }
        
        # Генерируем случайный очаг, входящий в новый диапазон узлов
        form_data['v_inf'] = str(random.randint(1, n_int))
        
        # Записываем сгенерированные ребра в формате u_1, v_1, u_2...
        for i, (u, v) in enumerate(edges, 1):
            form_data[f'u_{i}'] = u
            form_data[f'v_{i}'] = v
            
        return template('bfs', **base_vars, form=form_data, errors={}, result=None, svg_html=None)
        
    except ValueError:
        errs = {'global': 'Ошибка генерации сети: введите корректные целые числа для N и M.'}
        return template('bfs', **base_vars, form=request.forms, errors=errs, result=None, svg_html=None)
    except Exception as e:
        errs = {'global': f'Ошибка генерации сети: {str(e)}'}
        return template('bfs', **base_vars, form=request.forms, errors=errs, result=None, svg_html=None)

@route('/about')
def about():
    return template('about', title='Об авторах', year=2026, request_path=request.path)

if __name__ == '__main__':
    run(host='localhost', port=8080, debug=True, reloader=True)