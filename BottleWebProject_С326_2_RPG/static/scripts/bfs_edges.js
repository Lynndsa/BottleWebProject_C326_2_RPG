// ТВОЯ РАБОЧАЯ ФУНКЦИЯ ДОБАВЛЕНИЯ СТРОКИ
function addNewEdgeRow() {
    const tbody = document.querySelector('#matrix-table tbody');
    const rowCount = tbody.querySelectorAll('tr').length;
    const nextIndex = rowCount + 1;

    const newRow = document.createElement('tr');
    newRow.innerHTML = `
        <td><strong>${nextIndex}</strong></td>
        <td><input type="text" name="u_${nextIndex}" value="" class="form-control-custom" placeholder=""></td>
        <td><input type="text" name="v_${nextIndex}" value="" class="form-control-custom" placeholder=""></td>
        <td class="cell-center">
            <button type="button" class="btn-delete-edge" onclick="removeEdgeRow(this)">
                🗑️
            </button>
        </td>
    `;
    tbody.appendChild(newRow);
    updateMInputValue(nextIndex);
}

document.addEventListener('DOMContentLoaded', () => {
    const mInput = document.getElementById('m_input');
    if (mInput) {
        // Каждый раз, когда пользователь меняет число вручную, таблица перестраивается
        mInput.addEventListener('input', (e) => {
            adjustTableRows(e.target.value);
        });
    }

    // --- ИСПРАВЛЕНИЕ ДЛЯ СБРОСА ДО ОТПРАВКИ НА СЕРВЕР ---
    const fileInput = document.getElementById('txt_file_input');
    const bfsForm = document.getElementById('bfs-form');

    if (fileInput && mInput && bfsForm) {
        // Убираем старый onchange, который отправлял форму мгновенно без ведома JS
        fileInput.removeAttribute('onchange');

        // Вешаем правильное событие изменения файла
        fileInput.addEventListener('change', () => {
            // 1. Принудительно ставим M в 0 перед отправкой
            mInput.value = '0';

            // 2. Очищаем строки в таблице фронтенда
            adjustTableRows(0);

            // 3. И только теперь отправляем форму на бэкенд
            bfsForm.submit();
        });
    }
});

// ТВОЯ РАБОЧАЯ ФУНКЦИЯ УДАЛЕНИЯ СТРОКИ
function removeEdgeRow(button) {
    const row = button.closest('tr');
    if (row) {
        row.remove();
        reindexRows();
    }
}

// ТВОЯ РАБОЧАЯ ПЕРЕИНДЕКСАЦИЯ
function reindexRows() {
    const rows = document.querySelectorAll('#matrix-table tbody tr');
    rows.forEach((row, index) => {
        const rowNumber = index + 1;
        row.querySelector('td strong').innerText = rowNumber;

        const inputU = row.querySelector('input[name^="u_"]');
        const inputV = row.querySelector('input[name^="v_"]');
        if (inputU) inputU.setAttribute('name', `u_${rowNumber}`);
        if (inputV) inputV.setAttribute('name', `v_${rowNumber}`);
    });
    updateMInputValue(rows.length);
}

function updateMInputValue(count) {
    const mInput = document.getElementById('m_input');
    if (mInput) {
        mInput.value = count;
    }
}

// ТВОЯ РАБОЧАЯ ДИНАМИЧЕСКАЯ ГЕНЕРАЦИЯ СТРОК
function adjustTableRows(targetValue) {
    const count = parseInt(targetValue, 10);
    if (isNaN(count) || count < 0) return;

    const tbody = document.querySelector('#matrix-table tbody');
    let currentRows = tbody.querySelectorAll('tr');

    if (count > currentRows.length) {
        for (let i = currentRows.length + 1; i <= count; i++) {
            const newRow = document.createElement('tr');
            newRow.innerHTML = `
                <td><strong>${i}</strong></td>
                <td><input type="text" name="u_${i}" value="" class="form-control-custom" placeholder=""></td>
                <td><input type="text" name="v_${i}" value="" class="form-control-custom" placeholder=""></td>
                <td class="cell-center">
                    <button type="button" class="btn-delete-edge" onclick="removeEdgeRow(this)">
                        🗑️
                    </button>
                </td>
            `;
            tbody.appendChild(newRow);
        }
    }
    else if (count < currentRows.length) {
        for (let i = currentRows.length - 1; i >= count; i--) {
            currentRows[i].remove();
        }
    }
}
// --- РАСШИРЕННЫЙ БЛОК ЖИВОЙ ВАЛИДАЦИИ (С УЧЁТОМ СВЯЗЕЙ С N) ---
const inputN = document.getElementById('input-n');
const inputM = document.getElementById('m_input');
const inputP = document.querySelector('input[name="p"]');
const inputIter = document.querySelector('input[name="iter"]');
const submitBtn = document.querySelector('.btn-submit-bfs');

const constraints = {
    n: { min: 1, max: 50 },
    m: { min: 1, max: 80 },
    p: { min: 0, max: 1 },
    iter: { min: 1, max: 1000 }
};

// Основная функция валидации базовых полей
function validateField(input, type) {
    if (!input) return true;

    const value = parseFloat(input.value);
    const config = constraints[type];
    let isValid = true;

    if (isNaN(value) || value < config.min || value > config.max) {
        isValid = false;
    }

    // Проверка лимита рёбер M в зависимости от N
    if (type === 'm' && inputN && isValid) {
        const nVal = parseInt(inputN.value, 10);
        if (!isNaN(nVal) && nVal > 1) {
            const maxPossibleEdges = (nVal * (nVal - 1)) / 2;
            if (value > maxPossibleEdges) {
                isValid = false;
            }
        }
    }

    if (isValid) {
        input.classList.remove('is-error');
    } else {
        input.classList.add('is-error');
    }

    // Перепроверяем всю форму, включая динамические элементы
    checkFormValidity();
    return isValid;
}

// ВАЛИДАЦИЯ ДИНАМИЧЕСКИХ ОЧАГОВ ЗАРАЖЕНИЯ (ЧИПСОВ)
function validateInfectedChips() {
    const nVal = inputN ? parseInt(inputN.value, 10) : NaN;
    if (isNaN(nVal)) return;

    const chipInputs = document.querySelectorAll('.infected-node-input-field');
    chipInputs.forEach(input => {
        const val = parseInt(input.value, 10);
        // Если узел выходит за границы [1 .. N]
        if (isNaN(val) || val < 1 || val > nVal) {
            input.classList.add('is-error');
        } else {
            input.classList.remove('is-error');
        }
    });
}

// ВАЛИДАЦИЯ ИНПУТОВ В ТАБЛИЦЕ РЁБЕР (УЗЛЫ U И V)
function validateTableInputs() {
    const nVal = inputN ? parseInt(inputN.value, 10) : NaN;
    if (isNaN(nVal)) return;

    const tableInputs = document.querySelectorAll('#matrix-table tbody input[type="text"]');
    tableInputs.forEach(input => {
        const val = parseInt(input.value, 10);
        // Если значение в таблице рёбер превышает N или меньше 1
        if (isNaN(val) || val < 1 || val > nVal) {
            input.classList.add('is-error');
        } else {
            input.classList.remove('is-error');
        }
    });
}

// Общая проверка на доступность кнопки отправки
function checkFormValidity() {
    // Проверяем базовые инпуты
    const hasBaseErrors = [inputN, inputM, inputP, inputIter].some(input => {
        return input && input.classList.contains('is-error');
    });

    // Проверяем наличие ошибок в чипсах и таблице
    const hasDynamicErrors = document.querySelectorAll('.infected-node-input-field.is-error, #matrix-table tbody input.is-error').length > 0;

    const totalErrors = hasBaseErrors || hasDynamicErrors;

    if (submitBtn) {
        submitBtn.disabled = totalErrors;
        submitBtn.style.opacity = totalErrors ? "0.6" : "1";
        submitBtn.style.cursor = totalErrors ? "not-allowed" : "pointer";
    }
}

// Навешиваем события на базовые инпуты
[
    { el: inputN, type: 'n' },
    { el: inputM, type: 'm' },
    { el: inputP, type: 'p' },
    { el: inputIter, type: 'iter' }
].forEach(item => {
    if (item.el) {
        item.el.addEventListener('input', () => {
            validateField(item.el, item.type);
            if (item.type === 'n') {
                validateInfectedChips();
                validateTableInputs();
            }
        });
    }
});

// Делегирование событий для динамических элементов (чипсы и таблица рёбер)
// Слушаем любые изменения ввода в контейнере параметров и таблице
document.getElementById('infected-inputs-container').addEventListener('input', () => {
    validateInfectedChips();
    checkFormValidity();
});

const matrixTable = document.getElementById('matrix-table');
if (matrixTable) {
    matrixTable.addEventListener('input', () => {
        validateTableInputs();
        checkFormValidity();
    });
}

// Глобальный запуск первоначальной проверки при загрузка страницы
setTimeout(() => {
    validateInfectedChips();
    validateTableInputs();
    checkFormValidity();
}, 100);