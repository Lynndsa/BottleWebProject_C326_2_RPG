# -*- coding: utf-8 -*-

def validate_dfs_form(forms, files=None):
    errors = {}
    
    # Порог
    try:
        threshold = int(forms.get('threshold', 4))
        if threshold < 2 or threshold > 20:
            errors['threshold'] = 'Порог должен быть от 2 до 20.'
    except ValueError:
        errors['threshold'] = 'Порог должен быть целым числом.'

    # Кол-во транзакций
    try:
        tx_count = int(forms.get('tx_count', 10))
        if tx_count < 1 or tx_count > 200:
            errors['tx_count'] = 'От 1 до 200 транзакций.'
    except ValueError:
        errors['tx_count'] = 'Должно быть целым числом.'

    # Кол-во кошельков
    try:
        wallet_count = int(forms.get('wallet_count', 6))
        if wallet_count < 2 or wallet_count > 50:
            errors['wallet_count'] = 'От 2 до 50 кошельков.'
    except ValueError:
        errors['wallet_count'] = 'Должно быть целым числом.'

    # Режим ввода
    mode = forms.get('input_mode', 'manual')

    if mode == 'manual':
        raw = forms.get('transactions', '').strip()
        if not raw:
            errors['transactions'] = 'Введите хотя бы одну транзакцию.'
        else:
            for i, line in enumerate(raw.splitlines(), 1):
                parts = line.split()
                if len(parts) != 4:
                    errors['transactions'] = f'Строка {i}: ожидается 4 поля (отправитель получатель сумма метка).'
                    break
                try:
                    float(parts[2])
                    int(parts[3])
                except ValueError:
                    errors['transactions'] = f'Строка {i}: сумма и метка времени должны быть числами.'
                    break

    elif mode == 'file':
        if files is None or not files.get('tx_file') or not files['tx_file'].filename:
            errors['tx_file'] = 'Файл не выбран.'

    return errors
