

let rowCount = 0;

// Инициализаци

document.addEventListener('DOMContentLoaded', function () {

    const tbody = document.querySelector('#matrix-table tbody');

    if (tbody) {
        rowCount = tbody.querySelectorAll('tr').length;
    }

    // Кнопка "Добавить ребро"
    const btnAdd = document.getElementById('btn-add-edge');

    if (btnAdd) {
        btnAdd.addEventListener('click', addEdgeRow);
    }

    // Поле N
    const nInput = document.getElementById('input-n');

    if (nInput) {
        nInput.addEventListener('input', generateRowsFromN);
    }
});


// Добавление строки вручную


function addEdgeRow() {

    const tbody = document.querySelector('#matrix-table tbody');

    if (!tbody) return;

    rowCount++;

    const i = rowCount;

    const tr = document.createElement('tr');

    tr.innerHTML = `
        <td><strong>${i}</strong></td>

        <td>
            <input type="text"
                   name="u_${i}"
                   class="form-control-custom"
                   placeholder="1">
        </td>

        <td>
            <input type="text"
                   name="v_${i}"
                   class="form-control-custom"
                   placeholder="2">
        </td>

        <td>
            <input type="number"
                   name="w_${i}"
                   class="form-control-custom"
                   min="1"
                   placeholder="—">
        </td>

        <td style="text-align:center;">
            <button type="button"
                    class="btn-delete-edge"
                    onclick="removeEdgeRow(this)">
                🗑
            </button>
        </td>
    `;

    tbody.appendChild(tr);

    const wrapper = document.getElementById('matrix-wrapper');

    if (wrapper) {
        wrapper.scrollTop = wrapper.scrollHeight;
    }
}

// Автоматическая генерация по N

function generateRowsFromN() {

    const nInput = document.getElementById('input-n');

    if (!nInput) return;

    const n = parseInt(nInput.value);

    if (isNaN(n) || n <= 0) return;

    const targetRows = n + 3;

    let tbody = document.querySelector('#matrix-table tbody');

    if (!tbody) {

        const wrapper = document.getElementById('matrix-wrapper');

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
}


// Удаление строки

function removeEdgeRow(button) {

    const row = button.closest('tr');

    if (!row) return;

    row.remove();

    renumberRows();
}


// Перенумерация после удаления

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