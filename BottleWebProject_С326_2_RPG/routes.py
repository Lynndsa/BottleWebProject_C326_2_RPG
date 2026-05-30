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
@route('/dfs')
def dfs_module():
    return template('dfs',
                    title='Модуль DFS',
                    year=2026,
                    request_path=request.path)

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