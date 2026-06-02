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
        for part in v_inf_str.replace(',', ' ').split():
            part = part.strip()
            if part:
                try:
                    node = int(part)
                    infected_nodes.append(node)
                except ValueError:
                    pass
    
    if not infected_nodes:
        infected_nodes = [1]
        if 'n' in validated:
            errors['v_inf'] = f'Указаны некорректные очаги, используем узел 1'
    
    validated['v_inf'] = infected_nodes
    
    return validated, errors