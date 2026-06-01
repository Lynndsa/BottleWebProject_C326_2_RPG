# -*- coding: utf-8 -*-
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
# Вызывается fetch()-ом со страницы, возвращает строки для таблицы
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
        graph_html=None,   # <-- было graph_svg, теперь graph_html
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

    # random больше не обрабатывается здесь — он идёт через /dfs/random-json
    # но на случай если JS отключён — оставляем fallback
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
@route('/bfs')
def bfs_module():
    return template('bfs', title='Модуль BFS', year=2026, request_path=request.path)


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
            return template(
                'tsp',
                **_tsp_defaults(),
                errors={'global': 'Не удалось прочитать файл'}
            )

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
        m,
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
    log_to_file(
    form_data={'hotel': hotel, 'targets': targets},
    result_data={'path': full_visual_path, 'dist': min_dist}
)

    os.makedirs('tmp_results', exist_ok=True)
    existing = [f for f in os.listdir('tmp_results') if f.endswith('.pkl')]
    result_id = str(len(existing) + 1)

    with open(f'tmp_results/{result_id}.pkl', 'wb') as f:
        pickle.dump({
            'graph':      graph,
            'best_path':  best_path,
            'full_path':  full_visual_path,
            'hotel':      hotel,
            'unreachable': None,
            'log': {
                'hotel':   hotel,
                'targets': targets,
                'path':    full_visual_path,
                'dist':    min_dist
            }
        }, f)
    
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
        svg_html=svg_html,
        result_id=result_id
    )

@route('/static/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root='./static')

@route('/about')
def about():
    return template('about', title='Об авторах', year=2026, request_path=request.path)

if __name__ == '__main__':
    run(host='localhost', port=8080, debug=True, reloader=True)