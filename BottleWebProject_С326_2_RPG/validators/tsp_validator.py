def parse_input(n,m, edges_text, hotel_k, sites_text):
    errors = {}

    #  Валидация N
    try:
        n_val = int(n)
        if not (1 <= n_val <= 50):
            errors['n'] = 'Число вершин от 1 до 50'
            n_val = None
    except (TypeError, ValueError):
        errors['n'] = 'Введите целое число'
        n_val = None

    #  Инициализация графа (все ключи — СТРОКИ)
    graph = {}
    if n_val:
        for i in range(1, n_val + 1):
            graph[str(i)] = {}

    # Валидация M
    try:
        m_val = int(m)
        if not (1 <= m_val <= 8):
            errors['m'] = 'Число объектов от 1 до 8'
    except (TypeError, ValueError):
        errors['m'] = 'Введите целое число'
    # Валидация отеля (приводим к строке сразу)
    hotel = None
    try:
        k_val = int(hotel_k)
        if n_val and not (1 <= k_val <= n_val):
            errors['k'] = f'Отель от 1 до {n_val}'
        else:
            hotel = str(k_val)
    except (TypeError, ValueError):
        errors['k'] = 'Введите целое число'

    # Парсинг рёбер
    if edges_text:
        for line_num, line in enumerate(edges_text.strip().splitlines(), 1):
            parts = line.strip().split()
            if not parts: continue
            if len(parts) != 3:
                errors['edges'] = f'Строка {line_num}: формат "u v w"'
                break
            try:
                # Везде приводим вершины к строкам
                u, v, w = str(int(parts[0])), str(int(parts[1])), int(parts[2])
                if n_val and (int(u) > n_val or int(v) > n_val):
                    errors['edges'] = f'Строка {line_num}: вершина > N'
                    break
                if w < 0:
                    errors['edges'] = f'Строка {line_num}: вес < 0'
                    break
                graph[u][v] = w
                graph[v][u] = w
            except ValueError:
                errors['edges'] = f'Строка {line_num}: нужны числа'
                break
    else:
        errors['edges'] = 'Введите рёбра'

    # Парсинг достопримечательностей
    targets = []
    if sites_text:
        try:
            # Приводим к строкам
            raw = [str(int(x)) for x in sites_text.strip().split()]
            if len(raw) > 8:
                errors['sites'] = 'Не более 8 объектов'
            elif n_val and any(int(x) > n_val for x in raw):
                errors['sites'] = f'Объекты от 1 до {n_val}'
            elif hotel and hotel in raw:
                errors['sites'] = 'Отель не может быть целью'
            else:
                targets = raw
        except ValueError:
            errors['sites'] = 'Введите номера через пробел'
    else:
        errors['sites'] = 'Введите достопримечательности'

    return graph, hotel, targets, errors


def parse_txt_file(file_content):
    """

    Ожидаемый формат файла:
        N M K        ← первая строка: вершины, объекты, отель
        u v w        ← рёбра графа (по одному на строку)
        u v w
        ...
        sites: 2 3 4 ← последняя строка: достопримечательности


    """
    errors = {}
    form_data = {'n': '', 'm': '', 'k': '', 'edges': '', 'sites': ''}

    if not file_content or not file_content.strip():
        errors['global'] = 'Файл пустой'
        return form_data, errors

    lines = [line.strip() for line in file_content.strip().splitlines()]
    lines = [line for line in lines if line]  # убираем пустые строки

    if len(lines) < 2:
        errors['global'] = 'Файл слишком короткий: нужна минимум строка с N M K и одно ребро'
        return form_data, errors

    # --- Первая строка: N M K ---
    first_parts = lines[0].split()
    if len(first_parts) != 3:
        errors['global'] = 'Первая строка должна содержать три числа: N M K'
        return form_data, errors

    try:
        n, m, k = int(first_parts[0]), int(first_parts[1]), int(first_parts[2])
    except ValueError:
        errors['global'] = 'Первая строка: N, M, K должны быть целыми числами'
        return form_data, errors

    if not (1 <= n <= 50):
        errors['global'] = f'N должно быть от 1 до 50, получено: {n}'
        return form_data, errors

    if not (1 <= m <= 8):
        errors['global'] = f'M должно быть от 1 до 8, получено: {m}'
        return form_data, errors

    if not (1 <= k <= n):
        errors['global'] = f'K (отель) должен быть от 1 до {n}, получено: {k}'
        return form_data, errors

    form_data['n'] = str(n)
    form_data['m'] = str(m)
    form_data['k'] = str(k)

    # --- Последняя строка: sites ---
    last_line = lines[-1]
    if not last_line.lower().startswith('sites:'):
        errors['global'] = 'Последняя строка должна быть в формате "sites: 2 3 4"'
        return form_data, errors

    sites_part = last_line[len('sites:'):].strip()
    if not sites_part:
        errors['global'] = 'Не указаны достопримечательности после "sites:"'
        return form_data, errors

    try:
        sites = [int(x) for x in sites_part.split()]
    except ValueError:
        errors['global'] = 'Достопримечательности должны быть целыми числами'
        return form_data, errors

    if len(sites) != m:
        errors['global'] = f'Количество достопримечательностей ({len(sites)}) не совпадает с M={m}'
        return form_data, errors

    if any(s < 1 or s > n for s in sites):
        errors['global'] = f'Все достопримечательности должны быть от 1 до {n}'
        return form_data, errors

    if k in sites:
        errors['global'] = 'Отель не может быть среди достопримечательностей'
        return form_data, errors

    form_data['sites'] = ' '.join(str(s) for s in sites)

    # --- Средние строки: рёбра ---
    edge_lines = lines[1:-1]
    if not edge_lines:
        errors['global'] = 'В файле нет рёбер графа'
        return form_data, errors

    edges_result = []
    for line_num, line in enumerate(edge_lines, 2):
        parts = line.split()
        if len(parts) != 3:
            errors['global'] = f'Строка {line_num}: ожидается формат "u v w"'
            return form_data, errors
        try:
            u, v, w = int(parts[0]), int(parts[1]), int(parts[2])
        except ValueError:
            errors['global'] = f'Строка {line_num}: u, v, w должны быть целыми числами'
            return form_data, errors
        if u < 1 or u > n or v < 1 or v > n:
            errors['global'] = f'Строка {line_num}: вершина выходит за пределы N={n}'
            return form_data, errors
        if w < 0:
            errors['global'] = f'Строка {line_num}: вес не может быть отрицательным'
            return form_data, errors
        edges_result.append(f'{u} {v} {w}')

    form_data['edges'] = '\n'.join(edges_result)

    return form_data, errors