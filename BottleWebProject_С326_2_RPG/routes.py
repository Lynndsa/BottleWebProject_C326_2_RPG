# -*- coding: utf-8 -*-
from bottle import route, run, template, static_file, request
from tools.tsp_tools import generate_random_graph, log_to_file
from validators.tsp_validator import parse_input, parse_txt_file
from visual.tsp_visual import build_svg
from algorithms.tsp_algorithm import solve_tsp, get_full_path,dijkstra_simple


@route('/favicon.ico')
def favicon():
    return static_file('favicon.ico', root='./static')

@route('/')
def index():
    return template('index', title='Описание задач', year=2026, request_path=request.path)

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