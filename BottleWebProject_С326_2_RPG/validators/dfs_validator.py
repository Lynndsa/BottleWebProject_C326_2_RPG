def parse_transactions(raw_text: str) -> tuple[list[dict], list[str]]:
    """
    Парсит сырой текст транзакций — по одной на строку в формате:
        sender receiver amount timestamp

    Возвращает кортеж (parsed_rows, global_errors):
    - parsed_rows  : список словарей по каждой строке (включая невалидные, с полем error)
    - global_errors: список общих ошибок (например, ни одной валидной строки)
    """
    if not raw_text or not raw_text.strip():
        return [], ['Поле транзакций не может быть пустым.']

    lines = raw_text.strip().splitlines()
    parsed: list[dict] = []
    global_errors: list[str] = []

    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue

        parts = line.split()
        row: dict = {
            'sender':    '—',
            'receiver':  '—',
            'amount':    '—',
            'timestamp': '—',
            'valid':     False,
            'error':     None,
        }

        if len(parts) < 4:
            row['error'] = f'Строка {i + 1}: ожидается 4 поля, найдено {len(parts)}'
            parsed.append(row)
            continue

        sender, receiver, amount_str, ts_str = parts[0], parts[1], parts[2], parts[3]

        if sender == receiver:
            row['sender']   = sender
            row['receiver'] = receiver
            row['error'] = f'Строка {i + 1}: отправитель и получатель совпадают'
            parsed.append(row)
            continue

        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError('Сумма должна быть положительной')
        except ValueError as e:
            row['sender']   = sender
            row['receiver'] = receiver
            row['amount']   = amount_str
            row['error']    = f'Строка {i + 1}: некорректная сумма — {e}'
            parsed.append(row)
            continue

        try:
            ts = int(ts_str)
            if ts < 0:
                raise ValueError('Метка не может быть отрицательной')
        except ValueError as e:
            row['sender']    = sender
            row['receiver']  = receiver
            row['amount']    = f'{amount:.2f}'
            row['timestamp'] = ts_str
            row['error']     = f'Строка {i + 1}: некорректная метка времени — {e}'
            parsed.append(row)
            continue

        parsed.append({
            'sender':    sender,
            'receiver':  receiver,
            'amount':    amount,
            'timestamp': ts,
            'valid':     True,
            'error':     None,
        })

    valid_rows = [r for r in parsed if r['valid']]
    if not valid_rows and parsed:
        global_errors.append(
            'Не найдено ни одной корректной транзакции. Проверьте формат входных данных.'
        )

    return parsed, global_errors


def validate_params(threshold_str: str, tx_count_str: str, wallet_count_str: str) -> dict[str, str]:
    """
    Валидирует параметры формы. Возвращает словарь {поле: сообщение_об_ошибке};
    пустой словарь означает, что все параметры корректны.
    """
    errors: dict[str, str] = {}

    try:
        t = int(threshold_str)
        if not (2 <= t <= 20):
            errors['threshold'] = 'Порог должен быть от 2 до 20.'
    except (ValueError, TypeError):
        errors['threshold'] = 'Введите целое число от 2 до 20.'

    try:
        c = int(tx_count_str)
        if not (1 <= c <= 50):
            errors['tx_count'] = 'Количество транзакций: от 1 до 50.'
    except (ValueError, TypeError):
        errors['tx_count'] = 'Введите целое число от 1 до 50.'

    try:
        w = int(wallet_count_str)
        if not (2 <= w <= 20):
            errors['wallet_count'] = 'Количество кошельков: от 2 до 20.'
    except (ValueError, TypeError):
        errors['wallet_count'] = 'Введите целое число от 2 до 20.'

    return errors


def filter_valid(parsed_rows: list[dict]) -> list[dict]:
    """Оставляет только валидные строки и возвращает их в виде чистых словарей транзакций."""
    return [
        {
            'sender':    r['sender'],
            'receiver':  r['receiver'],
            'amount':    r['amount'],
            'timestamp': r['timestamp'],
        }
        for r in parsed_rows
        if r['valid']
    ]