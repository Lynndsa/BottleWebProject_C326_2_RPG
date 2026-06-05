import re
import random

def generate_random_bfs_network(n_str, m_str, p_str, iter_str):
    """Генерирует случайную структуру сети строго с M рёбрами"""
    n_str = n_str.strip() if n_str else '10'
    m_str = m_str.strip() if m_str else '12'  
    p_str = p_str.strip() if p_str else '0.3'
    iter_str = iter_str.strip() if iter_str else '50'

    n_int = int(n_str) if n_str.isdigit() else 10
    m_int = int(m_str) if m_str.isdigit() else 2
    
    n_int = max(2, min(50, n_int))
    max_possible_edges = (n_int * (n_int - 1)) // 2
    actual_m = max(0, min(max_possible_edges, m_int))
    
    edges = []
    edge_set = set()
    
    # Генерируем ровно actual_m случайных рёбер (БЕЗ базового связного дерева)
    while len(edges) < actual_m:
        u = random.randint(1, n_int)
        v = random.randint(1, n_int)
        if u != v:
            edge = (min(u, v), max(u, v))
            if edge not in edge_set:
                edges.append((str(u), str(v)))
                edge_set.add(edge)
            
    form_data = {
        'n': str(n_int),
        'm': str(actual_m),
        'p': p_str if p_str else '0.3',
        'iter': iter_str if iter_str else '50'
    }
    
    # Придумываем случайные начальные очаги заражения (вершины)
    # Например, выберем случайное количество вершин от 1 до 3, но не больше N
    count_start_nodes = random.randint(1, min(3, n_int))
    random_start_nodes = random.sample(range(1, n_int + 1), count_start_nodes)
    form_data['v_inf'] = " ".join(map(str, sorted(random_start_nodes)))
    
    for i, (u, v) in enumerate(edges, 1):
        form_data[f'u_{i}'] = u
        form_data[f'v_{i}'] = v
        
    return form_data


def parse_bfs_config_file(file_obj):
    """Парсит текстовый файл конфигурации"""
    form_data = {}
    errors = {}
    
    try:
        # Читаем содержимое файла
        if hasattr(file_obj, 'file'):
            content = file_obj.file.read().decode('utf-8')
        else:
            content = file_obj.read().decode('utf-8')
            
        lines = [line.strip() for line in content.splitlines() if line.strip()]
        
        if len(lines) < 3:
            errors['global'] = "Некорректная структура файла. Минимум 3 строки."
            return form_data, errors
            
        # Первая строка: N M p I
        meta_parts = lines[0].split()
        if len(meta_parts) < 4:
            errors['global'] = "Первая строка: N M p I"
            return form_data, errors
            
        form_data['n'] = meta_parts[0]
        form_data['m'] = meta_parts[1]
        form_data['p'] = meta_parts[2]
        form_data['iter'] = meta_parts[3]
        
        # Вторая строка: начальные очаги
        form_data['v_inf'] = lines[1]
        
        # Остальные строки: рёбра
        edge_index = 1
        for line in lines[2:]:
            nodes = re.findall(r'\d+', line)
            if len(nodes) >= 2:
                form_data[f'u_{edge_index}'] = nodes[0]
                form_data[f'v_{edge_index}'] = nodes[1]
                edge_index += 1
                
    except UnicodeDecodeError:
        errors['global'] = "Ошибка кодировки. Используйте UTF-8."
    except Exception as e:
        errors['global'] = f"Ошибка: {str(e)}"
        
    return form_data, errors