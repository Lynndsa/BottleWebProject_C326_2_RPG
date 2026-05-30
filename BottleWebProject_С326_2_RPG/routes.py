# -*- coding: utf-8 -*-
from bottle import route, run, template, static_file, request
from randoms.tsp_random import generate_random_graph
from validators.tsp_validator import parse_input, parse_txt_file
from visual.tsp_visual import build_svg
from algorithms.tsp_algorithm import solve_tsp


@route('/favicon.ico')
def favicon():
    return static_file('favicon.ico', root='./static')

@route('/')
def index():
    return template('index', title='Описание задач', year=2026, request_path=request.path)

@route('/bfs')
def bfs_module():
    return template('bfs', title='Модуль BFS', year=2026, request_path=request.path)


# ================================================================
#  Модуль TSP
# ================================================================

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


@route('/tsp', method='POST')
def tsp_post():

    # --- Загрузка из .txt ---
    upload = request.files.get('txt_file')
    if upload and upload.filename:
        try:
            content = upload.file.read().decode('utf-8')
        except Exception:
            return template('tsp', **_tsp_defaults(),
                            errors={'global': 'Не удалось прочитать файл'})

        form_data, errors = parse_txt_file(content)
        form = {k: v for k, v in form_data.items() if k != 'edges'}
        for i, line in enumerate(form_data.get('edges', '').strip().splitlines(), 1):
            parts = line.strip().split()
            if len(parts) == 3:
                form[f'u_{i}'] = parts[0]
                form[f'v_{i}'] = parts[1]
                form[f'w_{i}'] = parts[2]
        return template('tsp', **_tsp_defaults(), form=form, errors=errors)

    # --- Читаем основные поля ---
    n_raw = request.forms.get('n',     '').strip()
    m     = request.forms.get('m',     '').strip()
    k     = request.forms.get('k',     '').strip()
    sites = request.forms.get('sites', '').strip()

    # --- Собираем ВСЕ рёбра из таблицы (включая добавленные кнопкой) ---
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

    # --- Валидация ---
    graph, hotel, targets, errors = parse_input(n_raw, edges_text, k, sites)

    if errors:
        return template('tsp', **_tsp_defaults(), form=form, errors=errors)

    # --- Алгоритм ---
    best_path, min_dist = solve_tsp(graph, hotel, targets)

    if best_path is None:
        return template('tsp', **_tsp_defaults(), form=form,
                        errors={'global': 'Маршрут невозможен: граф несвязный или вершины недостижимы'})

    # --- Визуализация ---
    svg_html = build_svg(graph, best_path=best_path, hotel=hotel)

    result = {
        'path_str':   ' → '.join(best_path),
        'min_weight': min_dist,
    }

    return template('tsp', **_tsp_defaults(),
                    form=form, errors={},
                    result=result, svg_html=svg_html)



@route('/dfs', method=['GET', 'POST'])
def dfs_module():
    return template('dfs', title='Модуль DFS', year=2026, request_path=request.path)

@route('/static/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root='./static')

@route('/about')
def about():
    return template('about', title='Об авторах', year=2026, request_path=request.path)

if __name__ == '__main__':
    run(host='localhost', port=8080, debug=True, reloader=True)