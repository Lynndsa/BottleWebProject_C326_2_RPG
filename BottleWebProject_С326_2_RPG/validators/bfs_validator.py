# -*- coding: utf-8 -*-
import re

def validate_bfs_params(form_data):
    """
    Валидация параметров BFS симуляции
    """
    errors = {}
    validated = {}
    
    # Валидация N
    n_str = form_data.get('n', '')
    if not n_str:
        errors['n'] = 'Укажите количество узлов N'
    else:
        try:
            n = int(n_str)
            if n < 2 or n > 50:
                errors['n'] = 'N должно быть от 2 до 50'
            else:
                validated['n'] = n
        except ValueError:
            errors['n'] = 'N должно быть целым числом'
            
    # --- ДОБАВЛЯЕМ ВАЛИДАЦИЮ ОЧАГОВ / РЁБЕР (M) ---
    m_str = form_data.get('m', '')
    if not m_str:
        errors['m'] = 'Укажите количество рёбер M'
    else:
        try:
            m = int(m_str)
            if m < 0:
                errors['m'] = 'Значение не может быть меньше 0'
            elif 'n' in validated:
                # Наша проверка на максимальное количество рёбер полного графа
                n_val = validated['n']
                max_edges = (n_val * (n_val - 1)) // 2
                if m > max_edges:
                    errors['m'] = f'Максимум рёбер для {n_val} вершин — {max_edges} (полный граф)'
                else:
                    validated['m'] = m
            else:
                validated['m'] = m
        except ValueError:
            errors['m'] = 'M должно быть целым числом'
    
    # Валидация p
    p_str = form_data.get('p', '')
    if not p_str:
        errors['p'] = 'Укажите вероятность p'
    else:
        try:
            p = float(p_str)
            if p < 0 or p > 1:
                errors['p'] = 'p должно быть от 0 до 1'
            else:
                validated['p'] = p
        except ValueError:
            errors['p'] = 'p должно быть числом'
    
    # Валидация итераций
    iter_str = form_data.get('iter', '')
    if not iter_str:
        errors['iter'] = 'Укажите количество итераций'
    else:
        try:
            iterations = int(iter_str)
            if iterations < 1 or iterations > 1000:
                errors['iter'] = 'Итераций должно быть от 1 до 1000'
            else:
                validated['iter'] = iterations
        except ValueError:
            errors['iter'] = 'Итерации должны быть целым числом'
    
    # Валидация начальных очагов
    v_inf_str = form_data.get('v_inf', '')
    infected_nodes = []
    if v_inf_str:
        if 'n' in validated:
            n_val = validated['n']
            for part in v_inf_str.replace(',', ' ').split():
                if part.strip():
                    try:
                        node = int(part)
                        if 1 <= node <= n_val:
                            infected_nodes.append(node)
                        else:
                            errors['v_inf'] = f'Узел {node} вне диапазона 1..{n_val}'
                    except ValueError:
                        pass
    
    if not infected_nodes and 'v_inf' not in errors:
        infected_nodes = [1]
        if 'n' in validated:
            errors['v_inf'] = f'Указаны некорректные очаги, используем узел 1'
    
    validated['v_inf'] = infected_nodes
    
    return validated, errors