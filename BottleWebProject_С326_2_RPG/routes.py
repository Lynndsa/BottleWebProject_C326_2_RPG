# -*- coding: utf-8 -*-
from bottle import Bottle, route, view, static_file
from datetime import datetime


@route('/favicon.ico')
def favicon():
    return static_file('favicon.ico', root='./static')

@route('/')
@view('about') 
def home():
    return dict(
        title='About',
        message='Your application description page.',
        year=datetime.now().year
    )

@route('/contact')
@view('contact')
def contact():
    """Renders the contact page."""
    return dict(
        title='Contact',
        message='Your contact page.',
        year=datetime.now().year
    )


@route('/about')
@view('about')
def about():
    """Renders the about page."""
    return dict(
        title='About',
        message='Your application description page.',
        year=datetime.now().year
    )
@route('/bfs')
@view('bfs')
def bfs():
    """Renders the Breadth-First Search (BFS) page."""
    return dict(
        title='Обход в ширину (BFS)',
        message='Визуализация или решение алгоритма BFS.',
        year=datetime.now().year
    )

@route('/dfs')
@view('dfs')
def dfs():
    """Renders the Depth-First Search (DFS) property page."""
    return dict(
        title='Обход в глубину (DFS)',
        message='Визуализация или решение алгоритма DFS.',
        year=datetime.now().year
    )

@route('/tsp')
@view('tsp')
def tsp():
    """Renders the Traveling Salesperson Problem (TSP) page."""
    return dict(
        title='Задача коммивояжёра (TSP)',
        message='Решение задачи коммивояжёра методами оптимизации.',
        year=datetime.now().year
    )
