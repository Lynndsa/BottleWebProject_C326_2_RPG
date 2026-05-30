# -*- coding: utf-8 -*-
from bottle import Bottle, route, view, static_file
from datetime import datetime


@route('/favicon.ico')
def favicon():
    return static_file('favicon.ico', root='./static')

# routes.py
from bottle import route, run, template, static_file, request
from randoms.tsp_random import generate_random_graph
# -*- coding: utf-8 -*-
from bottle import Bottle, route, view, static_file, run, template, request
from datetime import datetime

# Главная страница с описанием задач
@route('/favicon.ico')
def favicon():
    return static_file('favicon.ico', root='./static')
  
@route('/')
def index():
    return template('index',
                    title='Описание задач',
                    year=2026,
                    request_path=request.path)

# Модуль BFS - распространение вируса
@route('/bfs')
def bfs_module():
    return template('bfs',
                    title='Модуль BFS',
                    year=2026,
                    request_path=request.path)

# Модуль TSP - планирование экскурсий
@route('/tsp', method=['GET', 'POST'])
def tsp_module():
    return template('tsp',
                    title='Модуль TSP',
                    year=2026,
                    request_path=request.path)
@route('/tsp/random', method=['POST'])
def tsp_random():
    form_data = generate_random_graph()
    return template('tsp',
                    title='Модуль TSP',
                    year=2026,
                    request_path=request.path,
                    form=form_data,
                    errors={})
# Модуль DFS - анализ блокчейна


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
        graph_svg=None,
        result=None,
    )

    if request.method == 'POST':
        mode = request.forms.get('input_mode', 'manual')
        defaults['input_mode']    = mode
        defaults['threshold']     = request.forms.get('threshold', 4)
        defaults['tx_count']      = request.forms.get('tx_count', 10)
        defaults['wallet_count']  = request.forms.get('wallet_count', 6)

        errors = validate_dfs_form(request.forms, request.files)

        if errors:
            defaults['errors'] = errors
            defaults['transactions'] = request.forms.get('transactions', '')
            return template('dfs', **defaults)

        if mode == 'random':
            raw = generate_transactions(
                int(request.forms.get('tx_count', 10)),
                int(request.forms.get('wallet_count', 6))
            )
        elif mode == 'file':
            raw = read_transactions_from_file(request.files.get('tx_file'))
        else:
            raw = request.forms.get('transactions', '')

        defaults['transactions'] = raw
        defaults['result'] = run_dfs(raw, int(request.forms.get('threshold', 4)))

    return template('dfs', **defaults)

# Статика
@route('/static/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root='./static')

# Страница "Об авторах"
@route('/about')
def about():
    return template('about',
                    title='Об авторах',
                    year=2026,
                    request_path=request.path)

if __name__ == '__main__':
    run(host='localhost', port=8080, debug=True, reloader=True)