/**
 * tx_table.js — интерактивная таблица транзакций
 */
(function () {
    'use strict';

    const tbody = document.getElementById('tx-table-body');
    const tmpl = document.getElementById('tx-row-template');
    const btnAdd = document.getElementById('tx-add-row');
    const btnSave = document.getElementById('tx-save-file');
    const btnReset = document.getElementById('tx-reset-table');
    const btnRun = document.getElementById('tx-run');
    const btnRandom = document.getElementById('btn-random');
    const countEl = document.getElementById('tx-row-count');
    const hiddenInput = document.getElementById('tx-hidden-input');
    const tableEl = document.getElementById('tx-main-table');

    // Блок для вывода ошибок валидации
    let errorBox = document.getElementById('tx-validation-errors');
    if (!errorBox) {
        errorBox = document.createElement('div');
        errorBox.id = 'tx-validation-errors';
        errorBox.style.cssText = 'display:none;margin-top:8px;padding:8px 12px;background:#fff3f3;border:1px solid #e57373;border-radius:4px;color:#c62828;font-size:0.9em;';
        if (tableEl && tableEl.parentNode) {
            tableEl.parentNode.insertBefore(errorBox, tableEl.nextSibling);
        }
    }

    if (!tbody || !tmpl || !hiddenInput) return;

    let rows = [];
    let nextId = 1;

    /* ── Инициализация из server-side данных ── */
    function init() {
        let initial = [];
        try {
            const raw = tableEl && tableEl.dataset.initialRows;
            if (raw) initial = JSON.parse(raw);
        } catch (e) { }

        if (initial.length > 0) {
            initial.forEach(r => addRow(r));
        } else {
            addRow();
        }
        syncHidden();
        updateUI();
    }

    /* ── Добавить строку ── */
    function addRow(data) {
        const id = nextId++;
        const node = tmpl.content.cloneNode(true);
        const tr = node.querySelector('tr');
        tr.dataset.id = id;

        const fields = ['sender', 'receiver', 'amount', 'timestamp'];
        fields.forEach(f => {
            const cell = tr.querySelector(`[data-field="${f}"]`);
            if (!cell) return;
            if (data && data[f] != null && data[f] !== '') cell.textContent = data[f];
            cell.addEventListener('input', () => { syncHidden(); updateUI(); });
            cell.addEventListener('blur', () => validateCell(cell, f));
            cell.addEventListener('focus', () => cell.classList.remove('tx-cell--error'));
            cell.addEventListener('keydown', e => handleKeydown(e, tr, f));
        });

        tr.querySelector('.tx-btn-delete').addEventListener('click', () => removeRow(id));
        tbody.appendChild(tr);
        rows.push({ id, el: tr });
        return tr;
    }

    /* ── Удалить строку ── */
    function removeRow(id) {
        const idx = rows.findIndex(r => r.id === id);
        if (idx === -1) return;
        rows[idx].el.remove();
        rows.splice(idx, 1);
        syncHidden();
        updateUI();
    }

    /* ── Синхронизировать скрытый textarea ── */
    function syncHidden() {
        const lines = [];
        rows.forEach(r => {
            const v = getRowValues(r.el);
            if (v.sender || v.receiver || v.amount || v.timestamp) {
                lines.push(`${v.sender} ${v.receiver} ${v.amount} ${v.timestamp}`.trim());
            }
        });
        hiddenInput.value = lines.join('\n');
    }

    function getRowValues(tr) {
        const get = f => {
            const el = tr.querySelector(`[data-field="${f}"]`);
            return el ? el.textContent.trim() : '';
        };
        return {
            sender: get('sender'), receiver: get('receiver'),
            amount: get('amount'), timestamp: get('timestamp')
        };
    }

    /* ── Валидация ячейки ── */
    function validateCell(cell, field) {
        const val = cell.textContent.trim();
        let ok = true;
        if (field === 'amount') {
            ok = val === '' || (!isNaN(parseFloat(val)) && parseFloat(val) > 0);
        } else if (field === 'timestamp') {
            ok = val === '' || (/^\d+$/.test(val) && parseInt(val, 10) >= 0);
        } else {
            ok = val === '' || /^\S+$/.test(val);
        }
        cell.classList.toggle('tx-cell--error', !ok);
        return ok;
    }

    /* ── Получить список ошибок по всем строкам ── */
    function collectErrors() {
        const messages = [];
        rows.forEach((r, i) => {
            const v = getRowValues(r.el);
            const rowNum = i + 1;

            // Проверяем только непустые строки
            const hasAny = v.sender || v.receiver || v.amount || v.timestamp;
            if (!hasAny) return;

            if (v.sender && v.receiver && v.sender === v.receiver) {
                messages.push(`Строка ${rowNum}: отправитель и получатель совпадают («${v.sender}»).`);
            }
            if (v.amount !== '' && (isNaN(parseFloat(v.amount)) || parseFloat(v.amount) <= 0)) {
                messages.push(`Строка ${rowNum}: сумма должна быть числом больше 0 (введено: «${v.amount}»).`);
            }
            if (v.timestamp !== '' && (!/^\d+$/.test(v.timestamp) || parseInt(v.timestamp, 10) < 0)) {
                messages.push(`Строка ${rowNum}: метка времени должна быть неотрицательным целым числом (введено: «${v.timestamp}»).`);
            }
        });
        return messages;
    }

    /* ── Показать / скрыть блок ошибок ── */
    function showErrors(messages) {
        if (!errorBox) return;
        if (messages.length === 0) {
            errorBox.style.display = 'none';
            errorBox.innerHTML = '';
        } else {
            errorBox.innerHTML = '<strong>⚠ Ошибки в таблице:</strong><ul style="margin:4px 0 0 16px;padding:0">' +
                messages.map(m => `<li>${m}</li>`).join('') + '</ul>';
            errorBox.style.display = 'block';
        }
    }

    /* ── Навигация клавишами ── */
    function handleKeydown(e, tr, field) {
        const fields = ['sender', 'receiver', 'amount', 'timestamp'];
        const fi = fields.indexOf(field);
        if (e.key === 'Enter') {
            e.preventDefault();
            if (fi < fields.length - 1) {
                focusCell(tr, fields[fi + 1]);
            } else {
                const newTr = addRow(); syncHidden(); updateUI();
                setTimeout(() => focusCell(newTr, 'sender'), 0);
            }
        } else if (e.key === 'Tab' && !e.shiftKey && fi === fields.length - 1) {
            e.preventDefault();
            const newTr = addRow(); syncHidden(); updateUI();
            setTimeout(() => focusCell(newTr, 'sender'), 0);
        } else if (e.key === 'ArrowDown') {
            e.preventDefault();
            const idx = rows.findIndex(r => r.el === tr);
            if (idx < rows.length - 1) focusCell(rows[idx + 1].el, field);
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            const idx = rows.findIndex(r => r.el === tr);
            if (idx > 0) focusCell(rows[idx - 1].el, field);
        }
    }

    function focusCell(tr, field) {
        const cell = tr.querySelector(`[data-field="${field}"]`);
        if (!cell) return;
        cell.focus();
        const range = document.createRange();
        const sel = window.getSelection();
        range.selectNodeContents(cell);
        range.collapse(false);
        sel.removeAllRanges();
        sel.addRange(range);
    }

    /* ── Обновить UI ── */
    function updateUI() {
        rows.forEach((r, i) => {
            r.el.querySelector('.tx-cell-num').textContent = i + 1;
        });

        // Подсчёт заполненных строк
        const validCount = rows.filter(r => {
            const v = getRowValues(r.el);
            return v.sender && v.receiver && v.amount && v.timestamp;
        }).length;
        if (countEl) countEl.textContent = validCount;

        // Собираем ошибки
        const errorMessages = collectErrors();
        showErrors(errorMessages);

        // Блокируем кнопки при наличии ошибок или пустой таблице
        const hasErrors = errorMessages.length > 0;
        const isDisabled = validCount === 0 || hasErrors;

        if (btnRun) {
            btnRun.disabled = isDisabled;
            btnRun.classList.toggle('btn--primary--disabled', isDisabled);
        }
        if (btnSave) {
            btnSave.disabled = isDisabled;
            btnSave.style.opacity = isDisabled ? '0.5' : '';
            btnSave.style.cursor = isDisabled ? 'not-allowed' : '';
        }
    }

    /* ── Загрузить строки в таблицу (сброс + заполнение) ── */
    function loadRows(dataArray) {
        rows.forEach(r => r.el.remove());
        rows = [];
        if (dataArray.length === 0) { addRow(); }
        else { dataArray.forEach(r => addRow(r)); }
        syncHidden();
        updateUI();
    }

    /* ── Публичный API для handleFileUpload ── */
    window.txTableLoadFile = function (text, filename) {
        const lines = text.split('\n').map(l => l.trim()).filter(l => l && !l.startsWith('#'));

        if (lines.length === 0) {
            if (window.showFileError) showFileError('❌ Файл не содержит данных (все строки пустые или комментарии).');
            return;
        }

        const data = lines.map(line => {
            const parts = line.split(/\s+/);
            return parts.length >= 4
                ? { sender: parts[0], receiver: parts[1], amount: parts[2], timestamp: parts[3] }
                : null;
        });

        const valid = data.filter(r => r !== null);
        if (valid.length === 0) {
            if (window.showFileError) showFileError('❌ Некорректный формат данных. Каждая строка должна содержать: отправитель получатель сумма метка_времени');
            return;
        }

        if (valid.length < data.length) {
            if (window.showFileError) showFileError(`⚠ Загружено ${valid.length} из ${data.length} строк. Остальные пропущены (неверный формат).`);
        } else {
            if (window.hideFileError) hideFileError();
        }

        loadRows(valid);
    };

    /* ── Кнопка «Случайный» — fetch без перезагрузки ── */
    if (btnRandom) {
        btnRandom.addEventListener('click', async () => {
            const txCount = document.getElementById('tx_count')?.value || '10';
            const walletCount = document.getElementById('wallet_count')?.value || '6';

            btnRandom.disabled = true;
            const origText = btnRandom.textContent;
            btnRandom.textContent = '⏳ Генерация...';

            try {
                const fd = new FormData();
                fd.append('tx_count', txCount);
                fd.append('wallet_count', walletCount);
                const res = await fetch('/dfs/random-json', { method: 'POST', body: fd });
                const data = await res.json();
                if (data.rows && data.rows.length > 0) loadRows(data.rows);
            } catch (e) {
                console.error('Random fetch failed:', e);
            } finally {
                btnRandom.disabled = false;
                btnRandom.textContent = origText;
            }
        });
    }

    /* ── Сохранить в .txt ── */
    if (btnSave) {
        btnSave.addEventListener('click', () => {
            if (btnSave.disabled) return;
            const lines = rows
                .map(r => getRowValues(r.el))
                .filter(v => v.sender && v.receiver && v.amount && v.timestamp)
                .map(v => `${v.sender} ${v.receiver} ${v.amount} ${v.timestamp}`);
            if (!lines.length) return;
            const now = new Date();
            const pad = n => String(n).padStart(2, '0');
            const dateStr = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())} ` +
                `${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`;
            const header = `# Сохранено: ${dateStr}`;
            const fileDate = `${now.getFullYear()}${pad(now.getMonth() + 1)}${pad(now.getDate())}_` +
                `${pad(now.getHours())}${pad(now.getMinutes())}`;
            const text = [header, ...lines].join('\n');
            const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url; a.download = `transactions_${fileDate}.txt`; a.click();
            URL.revokeObjectURL(url);
        });
    }

    if (btnReset) {
        btnReset.addEventListener('click', () => {
            if (!confirm('Очистить таблицу? Все введённые данные будут удалены.')) return;
            loadRows([]);
        });
    }

    if (btnAdd) {
        btnAdd.addEventListener('click', () => {
            const tr = addRow(); syncHidden(); updateUI();
            setTimeout(() => focusCell(tr, 'sender'), 0);
        });
    }

    init();
})();
