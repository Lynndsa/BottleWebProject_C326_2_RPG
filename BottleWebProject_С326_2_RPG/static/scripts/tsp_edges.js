let rowCount = 0;

// ====== ИНИЦИАЛИЗАЦИЯ И НАСТРОЙКА ОБРАБОТЧИКОВ ======
document.addEventListener('DOMContentLoaded', function () {
    const nInput = document.querySelector('input[name="n"]');
    const mInput = document.querySelector('input[name="m"]');
    const kInput = document.querySelector('input[name="k"]');
    const sitesInput = document.querySelector('input[name="sites"]');

    const tbody = document.querySelector('#matrix-table tbody');
    if (tbody) {
        rowCount = tbody.querySelectorAll('tr').length;
    }

    // Кнопка вручную добавить строку
    const btnAdd = document.getElementById('btn-add-edge');
    if (btnAdd) {
        btnAdd.addEventListener('click', addEdgeRow);
    }

    // Слушатель на поле N: генерирует строки и пересчитывает лимиты/валидацию
    if (nInput) {
        nInput.addEventListener('input', () => {
            generateRowsFromN(nInput);
            updateHotelLimit(nInput, kInput);
            updateMMax(nInput, mInput);
            validateM(nInput, mInput);
            validateMatrixRows(nInput); // Перепроверка строк при изменении N
        });
    }

    // Валидация количества объектов M
    if (mInput && nInput) {
        mInput.addEventListener('input', () => validateM(nInput, mInput));
    }

    // Валидация вершины отеля K
    if (kInput && nInput) {
        kInput.addEventListener('input', () => validateK(nInput, kInput));
    }

    // Валидация строки достопримечательностей
    if (sitesInput) {
        sitesInput.addEventListener('input', () => validateSites(nInput, mInput, kInput, sitesInput));
    }

    // Стартовая инициализация лимитов при загрузке страницы
    if (nInput && kInput) updateHotelLimit(nInput, kInput);
    if (nInput && mInput) updateMMax(nInput, mInput);
});


// АВТОМАТИЧЕСКАЯ И РУЧНАЯ ГЕНЕРАЦИЯ СТРОК МАТРИЦЫ

// Добавление новой строки в таблицу
function addEdgeRow() {
    const tbody = document.querySelector('#matrix-table tbody');
    if (!tbody) return;

    rowCount++;
    const i = rowCount;
    const tr = document.createElement('tr');

    // Числовые инпуты с ограничением min="1"
    tr.innerHTML = `
        <td><strong>${i}</strong></td>
        <td>
            <input type="number" name="u_${i}" class="form-control-custom" min="1" placeholder="1">
        </td>
        <td>
            <input type="number" name="v_${i}" class="form-control-custom" min="1" placeholder="2">
        </td>
        <td>
            <input type="number" name="w_${i}" class="form-control-custom" min="1" placeholder="—">
        </td>
        <td style="text-align:center;">
            <button type="button" class="btn-delete-edge" onclick="removeEdgeRow(this)">🗑</button>
        </td>
    `;

    tbody.appendChild(tr);

    // Валидация полей новой строки в реальном времени при вводе
    const nInput = document.querySelector('input[name="n"]');
    tr.querySelectorAll('input').forEach(input => {
        input.addEventListener('input', () => validateMatrixRows(nInput));
    });

    const wrapper = document.getElementById('matrix-wrapper');
    if (wrapper) {
        wrapper.scrollTop = wrapper.scrollHeight;
    }
}

// Валидация значений в строках матрицы (вершины от 1 до N, вес > 0)
function validateMatrixRows(nInput) {
    const n = parseInt(nInput.value);
    const rows = document.querySelectorAll('#matrix-table tbody tr');

    rows.forEach(row => {
        const uInput = row.querySelector('input[name^="u_"]');
        const vInput = row.querySelector('input[name^="v_"]');
        const wInput = row.querySelector('input[name^="w_"]');

        // Проверка начальной вершины U
        if (uInput && uInput.value) {
            const u = parseInt(uInput.value);
            uInput.setCustomValidity('');
            if (u < 1 || (!isNaN(n) && u > n)) {
                uInput.setCustomValidity(`Номер вершины должен быть от 1 до ${isNaN(n) ? 'N' : n}`);
            }
            if (uInput.validationMessage) uInput.reportValidity();
        }

        // Проверка конечной вершины V
        if (vInput && vInput.value) {
            const v = parseInt(vInput.value);
            vInput.setCustomValidity('');
            if (v < 1 || (!isNaN(n) && v > n)) {
                vInput.setCustomValidity(`Номер вершины должен быть от 1 до ${isNaN(n) ? 'N' : n}`);
            }
            if (vInput.validationMessage) vInput.reportValidity();
        }

        // Проверка положительного веса ребра W
        if (wInput && wInput.value) {
            const w = parseInt(wInput.value);
            wInput.setCustomValidity('');
            if (w < 1) {
                wInput.setCustomValidity('Вес ребра должен быть больше 0');
            }
            if (wInput.validationMessage) wInput.reportValidity();
        }
    });
}

// Автоматическая генерация N + 3 строк
function generateRowsFromN(nInput) {
    const n = parseInt(nInput.value);
    if (isNaN(n) || n < 0 || n >= 20) return;

    const targetRows = n + 3;
    let tbody = document.querySelector('#matrix-table tbody');

    if (!tbody) {
        const wrapper = document.getElementById('matrix-wrapper');
        if (!wrapper) return;

        wrapper.innerHTML = `
            <table class="edges-file-table" id="matrix-table">
                <thead>
                    <tr>
                        <th style="width:10%;">#</th>
                        <th>Вершина u</th>
                        <th>Вершина v</th>
                        <th>Вес w</th>
                        <th style="width:60px;">🗑</th>
                    </tr>
                </thead>
                <tbody></tbody>
            </table>
        `;
        tbody = document.querySelector('#matrix-table tbody');
    }

    let currentRows = tbody.querySelectorAll('tr').length;

    while (currentRows < targetRows) {
        addEdgeRow();
        currentRows++;
    }

    rowCount = currentRows;
    validateMatrixRows(nInput); // Валидация при изменении структуры
}

// Удаление строки из таблицы
function removeEdgeRow(button) {
    const row = button.closest('tr');
    if (!row) return;
    row.remove();
    renumberRows();
}

// Перенумерация строк и имен инпутов после удаления
function renumberRows() {
    const rows = document.querySelectorAll('#matrix-table tbody tr');
    rows.forEach((row, index) => {
        const i = index + 1;
        row.querySelector('td strong').textContent = i;
        row.querySelector('input[name^="u_"]').name = `u_${i}`;
        row.querySelector('input[name^="v_"]').name = `v_${i}`;
        row.querySelector('input[name^="w_"]').name = `w_${i}`;
    });
    rowCount = rows.length;
}


// ====== ВАЛИДАЦИЯ ФОРМЫ (М, К, ДОСТОПРИМЕЧАТЕЛЬНОСТИ) ======

// Валидация поля количества объектов M
function validateM(nInput, mInput) {
    const n = parseInt(nInput.value);
    const m = parseInt(mInput.value);

    mInput.setCustomValidity('');
    if (isNaN(m)) return;

    if (!isNaN(n) && m > n - 1) {
        mInput.setCustomValidity(`Количество объектов не может превышать ${n - 1}`);
    }
    if (m > 8) {
        mInput.setCustomValidity('Количество объектов не должно превышать 8');
    }

    if (mInput.validationMessage) {
        mInput.reportValidity();
    }
}

// Динамическое обновление атрибута max для поля M
function updateMMax(nInput, mInput) {
    const n = parseInt(nInput.value);
    if (isNaN(n)) return;
    mInput.max = Math.min(8, n - 1);
}

// Динамическое обновление атрибута max для отеля K
function updateHotelLimit(nInput, kInput) {
    const n = parseInt(nInput.value);
    if (!isNaN(n) && n > 0) {
        kInput.max = n;
    }
}

// Валидация корректности вершины отеля K
function validateK(nInput, kInput) {
    const n = parseInt(nInput.value);
    const k = parseInt(kInput.value);

    kInput.setCustomValidity('');
    if (isNaN(n) || isNaN(k)) return;

    if (k < 1 || k > n) {
        kInput.setCustomValidity(`Отель должен быть в диапазоне от 1 до ${n}`);
    }
    if (kInput.validationMessage) {
        kInput.reportValidity();
    }
}

// Валидация списка достопримечательностей (разделитель - пробелы)
function validateSites(nInput, mInput, kInput, sitesInput) {
    const n = parseInt(nInput.value);
    const m = parseInt(mInput.value);
    const k = parseInt(kInput.value);
    const value = sitesInput.value.trim();

    sitesInput.setCustomValidity('');
    if (!value) return;

    if (isNaN(n)) {
        sitesInput.setCustomValidity('Сначала укажите количество вершин N');
        sitesInput.reportValidity();
        return;
    }
    if (isNaN(m)) {
        sitesInput.setCustomValidity('Сначала укажите количество объектов M');
        sitesInput.reportValidity();
        return;
    }

    const sites = value.split(/\s+/);
    if (sites.length > m) {
        sitesInput.setCustomValidity(`Можно указать не более ${m} достопримечательностей`);
        sitesInput.reportValidity();
        return;
    }

    const used = new Set();
    for (const s of sites) {
        const num = parseInt(s);

        if (isNaN(num)) {
            sitesInput.setCustomValidity('Достопримечательности должны быть числами');
            break;
        }
        if (num < 1 || num > n) {
            sitesInput.setCustomValidity(`Вершины должны быть от 1 до ${n}`);
            break;
        }
        if (!isNaN(k) && num === k) {
            sitesInput.setCustomValidity(`Отель (${k}) нельзя указывать как достопримечательность`);
            break;
        }
        if (used.has(num)) {
            sitesInput.setCustomValidity('Достопримечательности не должны повторяться');
            break;
        }
        used.add(num);
    }

    if (sitesInput.validationMessage) {
        sitesInput.reportValidity();
    }
}


// ====== СКРИПТ МАСШТАБИРОВАНИЯ И ЗУМА SVG ======
document.addEventListener('DOMContentLoaded', function () {
    var wrap = document.getElementById('tsp-wrap');
    var svg = document.getElementById('tsp-svg');
    var lbl = document.getElementById('tsp-lbl');
    if (!wrap || !svg) return;

    var scale = 1, tx = 0, ty = 0;
    var MIN_SCALE = 0.2, MAX_SCALE = 5;
    var dragging = false, startX = 0, startY = 0, startTx = 0, startTy = 0;

    function apply() {
        svg.style.transform = 'translate(' + tx + 'px,' + ty + 'px) scale(' + scale + ')';
        svg.style.transformOrigin = 'top left';
        svg.style.position = 'absolute';
        svg.style.top = '0';
        svg.style.left = '0';
        if (lbl) lbl.textContent = Math.round(scale * 100) + '%';
    }

    wrap.addEventListener('mousedown', function (e) {
        if (e.button !== 0) return;
        dragging = true;
        startX = e.clientX; startY = e.clientY;
        startTx = tx; startTy = ty;
        wrap.style.cursor = 'grabbing';
        e.preventDefault();
    });
    window.addEventListener('mousemove', function (e) {
        if (!dragging) return;
        tx = startTx + (e.clientX - startX);
        ty = startTy + (e.clientY - startY);
        apply();
    });
    window.addEventListener('mouseup', function () {
        dragging = false;
        wrap.style.cursor = 'grab';
    });

    wrap.addEventListener('wheel', function (e) {
        e.preventDefault();
        var rect = wrap.getBoundingClientRect();
        var mx = e.clientX - rect.left;
        var my = e.clientY - rect.top;
        var delta = e.deltaY < 0 ? 1.12 : 1 / 1.12;
        var ns = Math.min(MAX_SCALE, Math.max(MIN_SCALE, scale * delta));
        tx = mx - (mx - tx) * (ns / scale);
        ty = my - (my - ty) * (ns / scale);
        scale = ns; apply();
    }, { passive: false });

    wrap.addEventListener('dblclick', function () {
        scale = 1; tx = 0; ty = 0; apply();
    });

    function zoomBtn(dir) {
        var W = wrap.clientWidth, H = wrap.clientHeight;
        var cx = W / 2, cy = H / 2;
        var d = dir > 0 ? 1.25 : 1 / 1.25;
        var ns = Math.min(MAX_SCALE, Math.max(MIN_SCALE, scale * d));
        tx = cx - (cx - tx) * (ns / scale);
        ty = cy - (cy - ty) * (ns / scale);
        scale = ns; apply();
    }

    var btnIn = document.getElementById('tsp-btn-in');
    var btnOut = document.getElementById('tsp-btn-out');
    var btnRst = document.getElementById('tsp-btn-rst');
    if (btnIn) btnIn.onclick = function () { zoomBtn(1); };
    if (btnOut) btnOut.onclick = function () { zoomBtn(-1); };
    if (btnRst) btnRst.onclick = function () { scale = 1; tx = 0; ty = 0; apply(); };

    apply();
});