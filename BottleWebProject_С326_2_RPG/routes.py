# routes.py
from bottle import route, run, template, static_file

# Главная страница с описанием задач
@route('/')
def index():
    return template('index', title='Главная', year=2026)

# Модуль BFS - распространение вируса
@route('/bfs')
def bfs_module():
    return template('bfs_module',
                   title='Модуль BFS',
                   year=2026)

# Модуль TSP - планирование экскурсий
@route('/tsp')
def tsp_module():
    return template('tsp_module',
                   title='Модуль TSP',
                   year=2026)

# Модуль DFS - анализ блокчейна
@route('/dfs')
def dfs_module():
    return template('dfs_module',
                   title='Модуль DFS',
                   year=2026)

# Статика (если не используешь StaticPlugin)
@route('/static/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root='./static')

# Страница "Об авторах"
@route('/about')
def about():
    return template('about',
                   title='Об авторах',
                   year=2026)

if __name__ == '__main__':
    run(host='localhost', port=8080, debug=True, reloader=True)