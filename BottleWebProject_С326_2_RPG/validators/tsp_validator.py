def parse_input(n, m, edges_text, hotel_k, sites_text):
    errors = {}

    # 1. Валидация N
    try:
        n_val = int(n)
        if not (1 <= n_val <= 20):
            errors['n'] = 'Число вершин от 1 до 20'
            n_val = None
    except (TypeError, ValueError):
        errors['n'] = 'Введите целое число'
        n_val = None

    # Инициализация графа (все ключи — СТРОКИ)
    graph = {}
    if n_val:
        for i in range(1, n_val + 1):
            graph[str(i)] = {}

    # 2. Валидация M
    try:
        m_val = int(m)
        if not (1 <= m_val <= 8):
            errors['m'] = 'Число объектов от 1 до 8'
        elif n_val and m_val > n_val - 1:
            errors['m'] = f'Количество объектов не может превышать {n_val - 1}'
    except (TypeError, ValueError):
        errors['m'] = 'Введите целое число'

    # 3. Валидация отеля
    hotel = None
    try:
        k_val = int(hotel_k)
        if n_val and not (1 <= k_val <= n_val):
            errors['k'] = f'Отель от 1 до {n_val}'
        else:
            hotel = str(k_val)
    except (TypeError, ValueError):
        errors['k'] = 'Введите целое число'

    # 4. Парсинг рёбер
    if edges_text:
        for line_num, line in enumerate(edges_text.strip().splitlines(), 1):
            parts = line.strip().split()
            if not parts: continue
            if len(parts) != 3:
                errors['edges'] = f'Строка {line_num}: формат "u v w"'
                break
            try:
                u, v, w = str(int(parts[0])), str(int(parts[1])), int(parts[2])
                if n_val and (int(u) > n_val or int(v) > n_val or int(u) < 1 or int(v) < 1):
                    errors['edges'] = f'Строка {line_num}: вершины должны быть от 1 до {n_val}'
                    break
                # Вес должен быть строго больше 0 (минимум 1)
                if w < 1:
                    errors['edges'] = f'Строка {line_num}: вес ребра должен быть больше 0'
                    break
                graph[u][v] = w
                graph[v][u] = w
            except ValueError:
                errors['edges'] = f'Строка {line_num}: нужны числа'
                break
    else:
        errors['edges'] = 'Введите рёбра'

    # 5. Парсинг достопримечательностей
    targets = []
    if sites_text:
        try:
            raw = [str(int(x)) for x in sites_text.strip().split()]
            if len(raw) > 8:
                errors['sites'] = 'Не более 8 объектов'
            elif n_val and any(not (1 <= int(x) <= n_val) for x in raw):
                errors['sites'] = f'Объекты от 1 до {n_val}'
            elif hotel and hotel in raw:
                errors['sites'] = 'Отель не может быть целью'
            elif len(raw) != len(set(raw)):
                # Проверка на уникальность элементов
                errors['sites'] = 'Достопримечательности не должны повторяться'
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
        ...
        sites: 2 3 4 ← последняя строка: достопримечательности
    """
    errors = {}
    form_data = {'n': '', 'm': '', 'k': '', 'edges': '', 'sites': ''}

    # Если файл вообще не читается или пустой
    if not file_content:
        errors['global'] = 'Не удалось прочитать файл или файл пустой'
        return form_data, errors

    try:
        # Очищаем от мусора по краям и режем на строки
        lines = [line.strip() for line in file_content.strip().splitlines()]
        lines = [line for line in lines if line]  # выкидываем пустые строки
    except Exception:
        errors['global'] = 'Ошибка чтения структуры файла. Убедитесь, что это текстовый файл (.txt)'
        return form_data, errors

    # Минимальная базовая проверка на длину
    if len(lines) < 2:
        errors['global'] = 'Файл поврежден или слишком короткий: нужна строка "N M K" и строка "sites:"'
        return form_data, errors

    # Проверка первой строки (N M K)
    first_parts = lines[0].split()
    if len(first_parts) != 3:
        errors['global'] = 'Первая строка файла сломана. Ожидалось три числа: N M K'
        return form_data, errors
    try:
        n, m, k = int(first_parts[0]), int(first_parts[1]), int(first_parts[2])
    except ValueError:
        errors['global'] = 'Ошибка в первой строке: N, M, K должны быть целыми числами'
        return form_data, errors

    # Проверка диапазонов первой строки
    if not (1 <= n <= 50):
        errors['global'] = f'Некорректный размер графа: N должно быть от 1 до 20 (получено {n})'
        return form_data, errors

    if not (1 <= m <= 8) or m > n - 1:
        errors['global'] = f'Некорректное M: должно быть от 1 до 8 и не превышать N-1 ({n-1})'
        return form_data, errors

    if not (1 <= k <= n):
        errors['global'] = f'Некорректный номер отеля: K должен быть от 1 до {n}'
        return form_data, errors

    form_data['n'] = str(n)
    form_data['m'] = str(m)
    form_data['k'] = str(k)

    # Проверка последней строки (sites:)
    last_line = lines[-1]
    if not last_line.lower().startswith('sites:'):
        errors['global'] = 'Файл поврежден: последняя строка должна начинаться с "sites:"'
        return form_data, errors

    sites_part = last_line[len('sites:'):].strip()
    if not sites_part:
        errors['global'] = 'В строке "sites:" не указаны номера достопримечательностей'
        return form_data, errors
    try:
        sites = [int(x) for x in sites_part.split()]
    except ValueError:
        errors['global'] = 'Список достопримечательностей содержит некорректные символы (нужны числа)'
        return form_data, errors

    # Валидация списка достопримечательностей
    if len(sites) != m:
        errors['global'] = f'Количество достопримечательностей ({len(sites)}) не соответствует указанному M={m}'
        return form_data, errors

    if any(s < 1 or s > n for s in sites):
        errors['global'] = f'Достопримечательности выходят за границы графа (должны быть от 1 до {n})'
        return form_data, errors

    if k in sites:
        errors['global'] = 'Конфликт данных: отель K не может быть достопримечательностью'
        return form_data, errors

    # Проверяем через set на дубликаты
    if len(sites) != len(set(sites)):
        errors['global'] = 'В списке достопримечательностей обнаружены дубликаты'
        return form_data, errors

    form_data['sites'] = ' '.join(str(s) for s in sites)

    # Убираем первую и последнюю строку(параметры графа и достопримечательности) 
    edge_lines = lines[1:-1]
    
    # Если строк всего 2 (первая и последняя), значит секция рёбер просто пустая
    if not edge_lines:
        errors['global'] = 'В файле отсутствует описание рёбер графа'
        return form_data, errors

    edges_result = []
    
    #Чтобы в ошибке указывать реальный номер строки в файле
    for line_num, line in enumerate(edge_lines, 2):
        parts = line.split()
        if len(parts) != 3:
            errors['global'] = f'Ошибка в строке {line_num}: формат ребра должен быть "u v w" (3 числа)'
            return form_data, errors
        
        try:
            u, v, w = int(parts[0]), int(parts[1]), int(parts[2])
        except ValueError:
            errors['global'] = f'Ошибка в строке {line_num}: вершины и вес должны быть целыми числами'
            return form_data, errors
            
        if u < 1 or u > n or v < 1 or v > n:
            errors['global'] = f'Ошибка в строке {line_num}: вершины {u} или {v} выходят за рамки N={n}'
            return form_data, errors
            
        if w < 1:
            errors['global'] = f'Ошибка в строке {line_num}: вес ребра должен быть строго больше 0'
            return form_data, errors
            
        edges_result.append(f'{u} {v} {w}')

    form_data['edges'] = '\n'.join(edges_result)

    return form_data, errors