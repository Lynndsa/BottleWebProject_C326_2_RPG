import re

def validate_bfs_params(n, m, p, iterations, v_inf_str, edges):
    """
    Валидация параметров BFS симуляции
    
    Returns:
        tuple: (is_valid, errors_dict, infected_nodes)
    """
    errors = {}
    infected_nodes = []
    
    # Валидация N
    if not n or n == '':
        errors['n'] = 'Пожалуйста, укажите количество узлов N'
    else:
        try:
            n_int = int(n)
            if n_int < 2 or n_int > 100:
                errors['n'] = 'N должно быть от 2 до 100'
        except ValueError:
            errors['n'] = 'N должно быть целым числом'
    
    # Валидация M (количество ребер)
    if not m or m == '':
        errors['m'] = 'Пожалуйста, укажите количество ребер M'
    else:
        try:
            m_int = int(m)
            if m_int < 1 or m_int > 100:
                errors['m'] = 'M должно быть от 1 до 100'
        except ValueError:
            errors['m'] = 'M должно быть целым числом'
    
    # Валидация p
    if not p or p == '':
        errors['p'] = 'Пожалуйста, укажите вероятность заражения p'
    else:
        try:
            p_float = float(p)
            if p_float < 0 or p_float > 1:
                errors['p'] = 'p должно быть от 0 до 1'
        except ValueError:
            errors['p'] = 'p должно быть числом'
    
    # Валидация iterations
    if not iterations or iterations == '':
        errors['iter'] = 'Пожалуйста, укажите количество итераций I'
    else:
        try:
            iter_int = int(iterations)
            if iter_int < 1 or iter_int > 1000:
                errors['iter'] = 'I должно быть от 1 до 1000'
        except ValueError:
            errors['iter'] = 'I должно быть целым числом'
    
    # Валидация начальных зараженных узлов
    if v_inf_str and v_inf_str.strip():
        try:
            infected_nodes = [int(x.strip()) for x in v_inf_str.split() if x.strip()]
            if not infected_nodes:
                errors['v_inf'] = 'Укажите хотя бы один начальный очаг'
        except ValueError:
            errors['v_inf'] = 'ID узлов должны быть целыми числами'
    else:
        # Если не указаны, пробуем использовать узел 1
        infected_nodes = [1]
    
    # Валидация ребер - только если они предоставлены
    if edges:
        for i, (u, v) in enumerate(edges):
            if not u or not v:
                errors['edges'] = f'Заполните оба поля для ребра #{i+1}'
            else:
                try:
                    u_int = int(u)
                    v_int = int(v)
                    if u_int < 1 or v_int < 1:
                        errors['edges'] = f'ID узлов в ребре #{i+1} должны быть положительными'
                except ValueError:
                    errors['edges'] = f'ID узлов в ребре #{i+1} должны быть целыми числами'
    else:
        # Если ребер нет, это допустимо (граф без связей)
        pass
    
    return len(errors) == 0, errors, infected_nodes