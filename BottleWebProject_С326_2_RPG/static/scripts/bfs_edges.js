// Функция добавления ОДНОЙ новой строки рёбер вручную через кнопку
function addNewEdgeRow() {
    const tbody = document.querySelector('#matrix-table tbody');
    const rowCount = tbody.querySelectorAll('tr').length;
    const nextIndex = rowCount + 1;

    const newRow = document.createElement('tr');
    newRow.innerHTML = `
        <td><strong>${nextIndex}</strong></td>
        <td><input type="text" name="u_${nextIndex}" value="" class="form-control table-input text-center" placeholder=""></td>
        <td><input type="text" name="v_${nextIndex}" value="" class="form-control table-input text-center" placeholder=""></td>
        <td class="text-center">
            <button type="button" class="btn btn-sm btn-delete-row" onclick="removeEdgeRow(this)">
                <span>🗑️</span>
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
});

// Удаление строки из таблицы
function removeEdgeRow(button) {
    const row = button.closest('tr');
    if (row) {
        row.remove();
        reindexRows();
    }
}

// Автоматическая переиндексация name и номеров строк после манипуляций с DOM
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

// ДИНАМИЧЕСКАЯ ГЕНЕРАЦИЯ СТРОК ПРИ ИЗМЕНЕНИИ ПОЛЯ M НА СТРАНИЦЕ
function adjustTableRows(targetValue) {
    const count = parseInt(targetValue, 10);
    if (isNaN(count) || count < 0) return;

    const tbody = document.querySelector('#matrix-table tbody');
    let currentRows = tbody.querySelectorAll('tr');

    // Если в поле M число больше текущего количества строк - генерируем новые пустые
    if (count > currentRows.length) {
        for (let i = currentRows.length + 1; i <= count; i++) {
            const newRow = document.createElement('tr');
            newRow.innerHTML = `
                <td><strong>${i}</strong></td>
                <td><input type="text" name="u_${i}" value="" class="form-control table-input text-center" placeholder=""></td>
                <td><input type="text" name="v_${i}" value="" class="form-control table-input text-center" placeholder=""></td>
                <td class="text-center">
                    <button type="button" class="btn btn-sm btn-delete-row" onclick="removeEdgeRow(this)">
                        <span>🗑️</span>
                    </button>
                </td>
            `;
            tbody.appendChild(newRow);
        }
    }
    // Если число в M уменьшили - стираем лишние строки снизу таблицы связей
    else if (count < currentRows.length) {
        for (let i = currentRows.length - 1; i >= count; i--) {
            currentRows[i].remove();
        }
    }
}