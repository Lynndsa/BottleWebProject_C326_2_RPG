// ============================================================
//  tsp_edges.js — динамическое добавление строк таблицы рёбер
// ============================================================

let rowCount = 0; // текущее количество строк

// Инициализация — считаем сколько строк уже есть в таблице
document.addEventListener('DOMContentLoaded', function () {
    const tbody = document.querySelector('#matrix-table tbody');
    if (tbody) {
        rowCount = tbody.querySelectorAll('tr').length;
    }

    // Слушаем кнопку добавить ребро
    const btnAdd = document.getElementById('btn-add-edge');
    if (btnAdd) {
        btnAdd.addEventListener('click', addEdgeRow);
    }
});

function addEdgeRow() {
    const tbody = document.querySelector('#matrix-table tbody');
    if (!tbody) return;

    rowCount++;
    const i   = rowCount;
    const tr  = document.createElement('tr');
    tr.innerHTML = `
        <td><strong>${i}</strong></td>
        <td><input type="text"   name="u_${i}" class="form-control-custom" placeholder="1"></td>
        <td><input type="text"   name="v_${i}" class="form-control-custom" placeholder="2"></td>
        <td><input type="number" name="w_${i}" class="form-control-custom" min="1" placeholder="—"></td>
    `;
    tbody.appendChild(tr);

    // Скроллим вниз чтобы новая строка была видна
    const wrapper = document.getElementById('matrix-wrapper');
    if (wrapper) wrapper.scrollTop = wrapper.scrollHeight;
}
