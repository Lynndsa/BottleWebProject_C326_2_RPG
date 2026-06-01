# -*- coding: utf-8 -*-
import json
from tools.tsp_tools import generate_random_graph
from bottle import route, view, static_file, run, template, request, response

from tools.dfs_tools    import generate_transactions, transactions_to_text
from validators.dfs_validator import parse_transactions, filter_valid, validate_params
from algorithms.dfs_algorithm import find_longest_path
from visual.dfs_visual    import render_graph_svg, render_graph_html


def _read_file(upload) -> str:
    if upload is None:
        return ''
    try:
        return upload.file.read().decode('utf-8')
    except Exception:
        return ''


@route('/favicon.ico')
def favicon():
    return static_file('favicon.ico', root='./static')


@route('/')
def index():
    return template('index', title='Описание задач', year=2026, request_path=request.path)


@route('/bfs')
def bfs_module():
    return template('bfs', title='Модуль BFS', year=2026, request_path=request.path)


@route('/tsp', method=['GET', 'POST'])
def tsp_module():
    return template('tsp', title='Модуль TSP', year=2026, request_path=request.path)


@route('/tsp/random', method=['POST'])
def tsp_random():
    form_data = generate_random_graph()
    return template('tsp', title='Модуль TSP', year=2026,
                    request_path=request.path, form=form_data, errors={})


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


@route('/static/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root='./static')


@route('/about')
def about():
    return template('about', title='Об авторах', year=2026, request_path=request.path)


if __name__ == '__main__':
    run(host='localhost', port=8080, debug=True, reloader=True)