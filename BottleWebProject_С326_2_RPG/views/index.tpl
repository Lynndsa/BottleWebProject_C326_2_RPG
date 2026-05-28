% rebase('layout.tpl', title='Главная страница', year=year)

<main class="graph-tasks-wrapper">
    <div class="page-header">
        <h1>Варианты задач</h1>
        <small>графовое моделирование</small>
        <p class="lead">Выберите задачу для изучения алгоритма или перехода к интерактивной демонстрации</p>
    </div>

    <div class="tasks-grid">
        <section class="task-card">
            <div class="card-header">
                <span class="badge">BFS</span>
                <h3>Вирус</h3>
            </div>
            <div class="card-body">
                <p>Моделирование распространения заражения в неориентированном графе.</p>
                
                <div class="card-help-box">
                    <strong>Поиск в ширину</strong> — обход графа слой за слоем, идеален для поиска кратчайших путей в невзвешенных графах.
                </div>

                <ul class="params-list">
                    <li><strong>Старт:</strong> <code>K</code> заражённых вершин</li>
                    <li><strong>Шаг:</strong> заражение всех соседей</li>
                    <li><strong>Modification:</strong> вероятность <code>p &lt; 1</code></li>
                </ul>
            </div>
            <div class="card-footer">
                <a href="/bfs" class="btn btn-blue">Запустить модуль</a>
            </div>
        </section>

        <section class="task-card">
            <div class="card-header">
                <span class="badge">TSP</span>
                <h3>Экскурсии</h3>
            </div>
            <div class="card-body">
                <p>Оптимальный маршрут туриста по достопримечательностям города.</p>
                
                <div class="card-help-box">
                    <strong>Задача коммивояжера</strong> — поиск гамильтонова цикла минимального веса; для <code>M &le; 8</code> решается полным перебором или динамикой по подмножествам.
                </div>

                <ul class="params-list">
                    <li><strong>Вершин:</strong> <code>N &le; 50</code></li>
                    <li><strong>Посетить:</strong> <code>M &le; 8</code></li>
                    <li><strong>Финиш:</strong> возврат в отель (вершина <code>K</code>)</li>
                </ul>
            </div>
            <div class="card-footer">
                <a href="/tsp" class="btn btn-cyan">Запустить модуль</a>
            </div>
        </section>

        <section class="task-card">
            <div class="card-header">
                <span class="badge">DFS</span>
                <h3>Блокчейн</h3>
            </div>
            <div class="card-body">
                <p>Анализ цепочек транзакций для выявления подозрительных паттернов.</p>
                
                <div class="card-help-box">
                    <strong>Поиск в глубину</strong> — рекурсивный обход с отслеживанием посещённых вершин, подходит для поиска путей и циклов.
                </div>

                <ul class="params-list">
                    <li><strong>Граф:</strong> ориентированный (кошельки &rarr; переводы)</li>
                    <li><strong>Цель:</strong> самый длинный путь без циклов</li>
                    <li><strong>Применение:</strong> поиск отмывания средств</li>
                </ul>
            </div>
            <div class="card-footer">
                <a href="/dfs" class="btn btn-teal">Запустить модуль</a>
            </div>
        </section>
    </div>
</main>