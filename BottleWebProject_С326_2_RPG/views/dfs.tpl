% rebase('layout.tpl', title=title, year=year)
<link rel="stylesheet" href="/static/content/dfs.css" />

<div class="container-tx">

% _errors = defined('errors') and errors or {}
% _result = defined('result') and result or None
% _mode   = defined('input_mode') and input_mode or 'manual'
% _parsed_file = defined('parsed_file') and parsed_file or None

    <h1 class="page-title">Анализ финансовых транзакций</h1>
    <p class="subtitle">Поиск максимальных бесциклических путей в графе блокчейн-переводов для выявления схем отмывания денег.</p>

    <!-- ТЕОРИЯ -->
    <div class="accordion">
        <button class="accordion-header" type="button">
            <span>📖 Описание алгоритма и теоретическая справка</span>
            <span class="accordion-icon">▼</span>
        </button>
        <div class="accordion-body">
            <div class="accordion-content">
                <div class="theory-intro">
                    <p>Входные данные — множество финансовых транзакций вида <strong>(отправитель, получатель, сумма, временная метка)</strong>. Операции моделируются в виде <strong>ориентированного взвешенного графа</strong>, где вершины — кошельки, дуги — денежные переводы.</p>
                    <p>Цель — обнаружение длинных последовательностей переводов, характерных для стадии <strong>слоинга (Layering)</strong> при сокрытии происхождения средств.</p>
                </div>

                <h3>⚙ Этапы работы алгоритма</h3>
                <div class="algo-flow">
                    <div class="flow-step">Транзакции</div><div class="flow-arrow">→</div>
                    <div class="flow-step">Построение графа</div><div class="flow-arrow">→</div>
                    <div class="flow-step">DFS</div><div class="flow-arrow">→</div>
                    <div class="flow-step">Поиск цепочек</div><div class="flow-arrow">→</div>
                    <div class="flow-step danger">Подозрительные пути</div>
                </div>
                <ol class="theory-list">
                    <li><strong>Индексация вершин</strong> — каждому адресу присваивается внутренний идентификатор.</li>
                    <li><strong>Построение списка смежности</strong> — для каждой вершины сохраняются исходящие переводы.</li>
                    <li><strong>Сортировка транзакций</strong> — рёбра упорядочиваются по временной метке.</li>
                    <li><strong>Поиск в глубину (DFS)</strong> — обход графа с возвратом (backtracking).</li>
                    <li><strong>Контроль циклов</strong> — запрещается повторное посещение уже пройденных вершин.</li>
                    <li><strong>Выделение подозрительных путей</strong> — цепочки длиннее порога отмечаются как опасные.</li>
                </ol>

                <h3>📊 Используемые структуры данных</h3>
                <table class="theory-table">
                    <thead><tr><th>Структура данных</th><th>Назначение</th></tr></thead>
                    <tbody>
                        <tr><td>Список смежности</td><td>Хранение графа транзакций</td></tr>
                        <tr><td>Set visited</td><td>Предотвращение циклов</td></tr>
                        <tr><td>Stack DFS</td><td>Обход графа в глубину</td></tr>
                        <tr><td>List paths</td><td>Сохранение найденных маршрутов</td></tr>
                    </tbody>
                </table>

                <h3>📈 Вычислительная сложность</h3>
                <table class="theory-table">
                    <thead><tr><th>Этап</th><th>Сложность</th></tr></thead>
                    <tbody>
                        <tr><td>Построение графа</td><td>O(E)</td></tr>
                        <tr><td>Сортировка транзакций</td><td>O(E log E)</td></tr>
                        <tr><td>DFS обход</td><td>O(V + E)</td></tr>
                        <tr><td>Анализ всех путей</td><td>O(V · (V + E))</td></tr>
                    </tbody>
                </table>

                <h3>⚠ Признаки подозрительной активности</h3>
                <div class="warning-box">
                    <ul>
                        <li>Длинные последовательности переводов между адресами.</li>
                        <li>Большое число промежуточных кошельков.</li>
                        <li>Быстрое перемещение средств по цепочке.</li>
                        <li>Дробление крупных сумм на множество мелких переводов.</li>
                        <li>Попытка скрыть исходный источник средств.</li>
                    </ul>
                </div>

                <div class="example-block">
                    <strong>Формат списка смежности:</strong><br><br>
                    <code>adj[v] = {(u, w, t)}</code><br><br>
                    где <strong>u</strong> — получатель, <strong>w</strong> — сумма, <strong>t</strong> — метка времени.<br>
                    Условие перехода: <code>u ∉ visited</code> и <code>t &gt; last_ts</code>
                </div>
            </div>
        </div>
    </div>

    <!-- ПРИМЕР РАЗБОРА -->
    <div class="example-walkthrough">
        <div class="ew-header">
            <span class="ew-badge">📋 Пример</span>
            <h2>Разбор входных данных</h2>
            <p>Ниже показан конкретный набор транзакций и то, как алгоритм строит по ним граф и находит подозрительные цепочки. Используйте этот формат при ручном вводе.</p>
        </div>

        <div class="ew-body">
            <!-- Левая часть: входные данные -->
            <div class="ew-section">
                <div class="ew-section-title">① Входные транзакции <span class="ew-hint">формат: отправитель получатель сумма временная_метка</span></div>
                <div class="ew-input-block">
                    <table class="ew-table">
                        <thead>
                            <tr><th>#</th><th>Отправитель</th><th>Получатель</th><th>Сумма (BTC)</th><th>Метка времени</th><th>Дата (UTC)</th></tr>
                        </thead>
                        <tbody>
                            <tr class="ex-row-sus">
                                <td>1</td><td class="addr">A1B2C3</td><td class="addr">D4E5F6</td>
                                <td class="amount">50 000.00</td><td>1700000001</td><td>14.11.2023 22:13</td>
                            </tr>
                            <tr class="ex-row-sus">
                                <td>2</td><td class="addr">D4E5F6</td><td class="addr">G7H8I9</td>
                                <td class="amount">49 500.00</td><td>1700000120</td><td>14.11.2023 22:15</td>
                            </tr>
                            <tr class="ex-row-sus">
                                <td>3</td><td class="addr">G7H8I9</td><td class="addr">J0K1L2</td>
                                <td class="amount">49 000.00</td><td>1700000300</td><td>14.11.2023 22:18</td>
                            </tr>
                            <tr class="ex-row-sus">
                                <td>4</td><td class="addr">J0K1L2</td><td class="addr">M3N4O5</td>
                                <td class="amount">48 200.00</td><td>1700000540</td><td>14.11.2023 22:22</td>
                            </tr>
                            <tr>
                                <td>5</td><td class="addr">P6Q7R8</td><td class="addr">S9T0U1</td>
                                <td class="amount">1 200.00</td><td>1700001000</td><td>14.11.2023 22:30</td>
                            </tr>
                            <tr>
                                <td>6</td><td class="addr">S9T0U1</td><td class="addr">V2W3X4</td>
                                <td class="amount">600.00</td><td>1700001200</td><td>14.11.2023 22:33</td>
                            </tr>
                            <tr>
                                <td>7</td><td class="addr">A1B2C3</td><td class="addr">P6Q7R8</td>
                                <td class="amount">3 000.00</td><td>1699999800</td><td>14.11.2023 22:10</td>
                            </tr>
                        </tbody>
                    </table>
                    <div class="ew-copy-hint">
                        <span class="ew-copy-label">Текст для вставки в форму:</span>
                        <pre class="ew-pre">A1B2C3 D4E5F6 50000.00 1700000001
D4E5F6 G7H8I9 49500.00 1700000120
G7H8I9 J0K1L2 49000.00 1700000300
J0K1L2 M3N4O5 48200.00 1700000540
P6Q7R8 S9T0U1 1200.00 1700001000
S9T0U1 V2W3X4 600.00 1700001200
A1B2C3 P6Q7R8 3000.00 1699999800</pre>
                        <button class="btn btn-copy" onclick="copyExample()">📋 Скопировать</button>
                    </div>
                </div>
            </div>

            <!-- Правая часть: граф и результат -->
            <div class="ew-section">
                <div class="ew-section-title">② Граф транзакций и найденные цепочки</div>

                <!-- Граф схема -->
                <div class="ew-graph">
                    <svg viewBox="0 0 520 220" xmlns="http://www.w3.org/2000/svg" class="ew-svg">
                        <defs>
                            <marker id="arr-sus" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
                                <path d="M0,0 L0,6 L8,3 z" fill="#ef4444"/>
                            </marker>
                            <marker id="arr-norm" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
                                <path d="M0,0 L0,6 L8,3 z" fill="#0ea5e9"/>
                            </marker>
                        </defs>
                        <!-- Подозрительная цепочка -->
                        <line x1="72" y1="70" x2="152" y2="70" stroke="#ef4444" stroke-width="2.5" marker-end="url(#arr-sus)"/>
                        <text x="112" y="62" text-anchor="middle" font-size="9" fill="#ef4444" font-weight="700">50 000</text>
                        <line x1="192" y1="70" x2="272" y2="70" stroke="#ef4444" stroke-width="2.5" marker-end="url(#arr-sus)"/>
                        <text x="232" y="62" text-anchor="middle" font-size="9" fill="#ef4444" font-weight="700">49 500</text>
                        <line x1="312" y1="70" x2="392" y2="70" stroke="#ef4444" stroke-width="2.5" marker-end="url(#arr-sus)"/>
                        <text x="352" y="62" text-anchor="middle" font-size="9" fill="#ef4444" font-weight="700">49 000</text>
                        <line x1="432" y1="70" x2="492" y2="70" stroke="#ef4444" stroke-width="2.5" marker-end="url(#arr-sus)"/>
                        <text x="462" y="62" text-anchor="middle" font-size="9" fill="#ef4444" font-weight="700">48 200</text>
                        <!-- Боковая ветка -->
                        <line x1="40" y1="90" x2="40" y2="150" stroke="#0ea5e9" stroke-width="2" marker-end="url(#arr-norm)"/>
                        <text x="52" y="125" font-size="9" fill="#0284c7" font-weight="700">3 000</text>
                        <line x1="60" y1="168" x2="140" y2="168" stroke="#0ea5e9" stroke-width="2" marker-end="url(#arr-norm)"/>
                        <text x="100" y="160" text-anchor="middle" font-size="9" fill="#0284c7" font-weight="700">1 200</text>
                        <line x1="180" y1="168" x2="260" y2="168" stroke="#0ea5e9" stroke-width="2" marker-end="url(#arr-norm)"/>
                        <text x="220" y="160" text-anchor="middle" font-size="9" fill="#0284c7" font-weight="700">600</text>
                        <!-- Узлы подозрительные -->
                        <circle cx="40" cy="70" r="28" fill="#fff5f5" stroke="#ef4444" stroke-width="2.5"/>
                        <text x="40" y="67" text-anchor="middle" font-size="8.5" font-weight="800" fill="#b91c1c">A1B2C3</text>
                        <text x="40" y="79" text-anchor="middle" font-size="7" fill="#ef4444">исток</text>
                        <circle cx="172" cy="70" r="28" fill="#fff5f5" stroke="#ef4444" stroke-width="2.5"/>
                        <text x="172" y="67" text-anchor="middle" font-size="8.5" font-weight="800" fill="#b91c1c">D4E5F6</text>
                        <text x="172" y="79" text-anchor="middle" font-size="7" fill="#ef4444">слой 1</text>
                        <circle cx="292" cy="70" r="28" fill="#fff5f5" stroke="#ef4444" stroke-width="2.5"/>
                        <text x="292" y="67" text-anchor="middle" font-size="8.5" font-weight="800" fill="#b91c1c">G7H8I9</text>
                        <text x="292" y="79" text-anchor="middle" font-size="7" fill="#ef4444">слой 2</text>
                        <circle cx="412" cy="70" r="28" fill="#fff5f5" stroke="#ef4444" stroke-width="2.5"/>
                        <text x="412" y="67" text-anchor="middle" font-size="8.5" font-weight="800" fill="#b91c1c">J0K1L2</text>
                        <text x="412" y="79" text-anchor="middle" font-size="7" fill="#ef4444">слой 3</text>
                        <circle cx="504" cy="70" r="14" fill="#fff5f5" stroke="#ef4444" stroke-width="2"/>
                        <text x="504" y="67" text-anchor="middle" font-size="7.5" font-weight="800" fill="#b91c1c">M3N4</text>
                        <text x="504" y="78" text-anchor="middle" font-size="6.5" fill="#ef4444">финал</text>
                        <!-- Узлы нормальные -->
                        <circle cx="40" cy="168" r="22" fill="#f0f9ff" stroke="#0ea5e9" stroke-width="2"/>
                        <text x="40" y="165" text-anchor="middle" font-size="8" font-weight="700" fill="#0c4a6e">P6Q7R8</text>
                        <text x="40" y="176" text-anchor="middle" font-size="6.5" fill="#0284c7">промеж.</text>
                        <circle cx="160" cy="168" r="22" fill="#f0f9ff" stroke="#0ea5e9" stroke-width="2"/>
                        <text x="160" y="165" text-anchor="middle" font-size="8" font-weight="700" fill="#0c4a6e">S9T0U1</text>
                        <text x="160" y="176" text-anchor="middle" font-size="6.5" fill="#0284c7">промеж.</text>
                        <circle cx="280" cy="168" r="22" fill="#f0f9ff" stroke="#0ea5e9" stroke-width="2"/>
                        <text x="280" y="165" text-anchor="middle" font-size="8" font-weight="700" fill="#0c4a6e">V2W3X4</text>
                        <text x="280" y="176" text-anchor="middle" font-size="6.5" fill="#0284c7">конечн.</text>
                        <!-- Легенда -->
                        <rect x="320" y="145" width="180" height="60" rx="8" fill="white" stroke="#e2e8f0" stroke-width="1.5"/>
                        <line x1="332" y1="162" x2="356" y2="162" stroke="#ef4444" stroke-width="2.5"/>
                        <text x="362" y="166" font-size="9" fill="#475569" font-weight="600">⚠ Подозрительная цепочка</text>
                        <line x1="332" y1="182" x2="356" y2="182" stroke="#0ea5e9" stroke-width="2"/>
                        <text x="362" y="186" font-size="9" fill="#475569" font-weight="600">✓ Нормальная ветка</text>
                    </svg>
                </div>

                <!-- Найденные пути -->
                <div class="ew-section-title" style="margin-top:1rem;">③ Результат DFS (порог = 4)</div>
                <div class="ew-paths">
                    <div class="ew-path ew-path--sus">
                        <div class="ew-path-head">
                            <span class="ew-path-num">#1</span>
                            <span class="chain-tag suspicious">⚠ Подозрительный</span>
                            <span class="ew-path-stat">4 транзакции · 196 700 BTC</span>
                        </div>
                        <div class="ew-path-route">
                            <span class="ew-node ew-node--start">A1B2C3</span>
                            <span class="ew-arrow ew-arrow--sus">→</span>
                            <span class="ew-node ew-node--sus">D4E5F6</span>
                            <span class="ew-arrow ew-arrow--sus">→</span>
                            <span class="ew-node ew-node--sus">G7H8I9</span>
                            <span class="ew-arrow ew-arrow--sus">→</span>
                            <span class="ew-node ew-node--sus">J0K1L2</span>
                            <span class="ew-arrow ew-arrow--sus">→</span>
                            <span class="ew-node ew-node--sus">M3N4O5</span>
                        </div>
                        <div class="ew-path-explain">
                            DFS стартует из <code>A1B2C3</code>, последовательно обходит соседей в порядке возрастания временных меток.
                            Каждый переход: <code>t_следующий &gt; t_текущий</code>, вершина не в <code>visited</code>.
                            Длина цепочки 4 ≥ порогу 4 → <strong>помечено как подозрительное</strong>.
                        </div>
                    </div>
                    <div class="ew-path ew-path--norm">
                        <div class="ew-path-head">
                            <span class="ew-path-num">#2</span>
                            <span class="chain-tag normal">✓ Нормальный</span>
                            <span class="ew-path-stat">2 транзакции · 1 800 BTC</span>
                        </div>
                        <div class="ew-path-route">
                            <span class="ew-node ew-node--start">P6Q7R8</span>
                            <span class="ew-arrow">→</span>
                            <span class="ew-node">S9T0U1</span>
                            <span class="ew-arrow">→</span>
                            <span class="ew-node">V2W3X4</span>
                        </div>
                        <div class="ew-path-explain">
                            Длина цепочки 2 &lt; порогу 4 → обычная активность.
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- ОСНОВНОЙ РЯД: ФОРМА + ГРАФ -->
    <div class="tx-layout">
        <div class="tx-form">
            <form method="POST" action="/dfs" enctype="multipart/form-data" novalidate class="card">
                <input type="hidden" id="input_mode" name="input_mode" value="{{_mode}}">

                <div class="card-header">
                    <h2>Параметры задачи</h2>
                    <div class="actions-group">
                        <button type="submit" onclick="document.getElementById('input_mode').value='random';" class="btn">🎲 Случайный</button>
                        <label class="btn">📂 Из файла .txt
                            <input type="file" name="tx_file" accept=".txt" onchange="document.getElementById('input_mode').value='file'; this.form.submit();" style="display: none;">
                        </label>
                    </div>
                </div>

                <div class="form-field">
                    <label class="form-label" for="threshold">Порог подозрительности <span class="hint">(кол-во транзакций)</span></label>
                    <div class="threshold-control">
                        <input type="range" id="threshold-range" min="2" max="20" step="1" value="{{threshold or 4}}"
                               oninput="document.getElementById('threshold-display').textContent=this.value; document.getElementById('threshold').value=this.value;">
                        <div class="threshold-value" id="threshold-display">{{threshold or 4}}</div>
                    </div>
                    <input type="number" id="threshold" name="threshold" value="{{threshold or 4}}" style="display:none;">
                    % if _errors.get('threshold'):
                    <span class="error-msg">{{_errors['threshold']}}</span>
                    % end
                </div>

                <div class="form-row">
                    <div class="form-field">
                        <label class="form-label" for="tx_count">Транзакций <span class="hint">для генерации</span></label>
                        <input type="number" id="tx_count" name="tx_count" min="1" max="200" value="{{tx_count or 10}}" class="form-input">
                        % if _errors.get('tx_count'):
                        <span class="error-msg">{{_errors['tx_count']}}</span>
                        % end
                    </div>
                    <div class="form-field">
                        <label class="form-label" for="wallet_count">Кошельков <span class="hint">вершин</span></label>
                        <input type="number" id="wallet_count" name="wallet_count" min="2" max="50" value="{{wallet_count or 6}}" class="form-input">
                        % if _errors.get('wallet_count'):
                        <span class="error-msg">{{_errors['wallet_count']}}</span>
                        % end
                    </div>
                </div>

                <div class="form-field">
                    <label class="form-label" for="transactions">
                        Транзакции
                        <span class="hint">отправитель получатель сумма метка — по одной на строку</span>
                    </label>
                    <textarea id="transactions" name="transactions"
                              class="form-textarea {{'is-error' if _errors.get('transactions') else ''}}"
                              placeholder="A1B2C3 D4E5F6 50000.00 1700000001&#10;D4E5F6 G7H8I9 49500.00 1700000120&#10;G7H8I9 J0K1L2 49000.00 1700000300&#10;J0K1L2 M3N4O5 48200.00 1700000540">{{transactions or ''}}</textarea>
                    % if _errors.get('transactions'):
                    <span class="error-msg">{{_errors['transactions']}}</span>
                    % end
                    % if _errors.get('tx_file'):
                    <span class="error-msg">{{_errors['tx_file']}}</span>
                    % end
                </div>

                <button type="submit" onclick="document.getElementById('input_mode').value='manual';" class="btn btn--primary">🔍 Запустить анализ</button>
            </form>
        </div>

        <div class="tx-graph">
            <div class="card">
                <h2>Визуализация графа транзакций</h2>
                <div class="canvas-container">
                    % if defined('graph_svg') and graph_svg:
                        {{!graph_svg}}
                    % else:
                        <div class="canvas-placeholder">
                            <div class="icon">🕸️</div>
                            <div class="title">Рабочая область графа пуста</div>
                            <div class="desc">Введите транзакции вручную, сгенерируйте случайные или загрузите файл .txt</div>
                        </div>
                    % end
                </div>
            </div>
        </div>
    </div>

    <!-- ТАБЛИЦА ПРЕДПРОСМОТРА ФАЙЛА -->
    % if _mode == 'file' and _parsed_file and len(_parsed_file) > 0:
    <div class="card card--file-preview">
        <div class="file-preview-header">
            <h2>📂 Данные из загруженного файла</h2>
            <span class="file-preview-badge">{{len(_parsed_file)}} строк</span>
        </div>
        <p class="file-preview-desc">Все транзакции, считанные из файла .txt. Строки с ошибками не войдут в анализ.</p>
        <div class="tx-table-wrapper">
            <table class="tx-table tx-table--preview">
                <thead>
                    <tr>
                        <th>#</th><th>Отправитель</th><th>Получатель</th><th>Сумма</th><th>Временная метка</th><th>Статус</th>
                    </tr>
                </thead>
                <tbody>
                    % for i, row in enumerate(_parsed_file):
                    % is_valid = row.get('valid', True)
                    <tr class="{{'row-invalid' if not is_valid else ''}}">
                        <td>{{i + 1}}</td>
                        <td class="addr">{{row.get('sender', '—')}}</td>
                        <td class="addr">{{row.get('receiver', '—')}}</td>
                        <td class="amount">{{row.get('amount', '—')}}</td>
                        <td>{{row.get('timestamp', '—')}}</td>
                        <td>
                            % if is_valid:
                            <span class="status-ok">✓ ОК</span>
                            % else:
                            <span class="status-err">✗ Ошибка</span>
                            % end
                        </td>
                    </tr>
                    % end
                </tbody>
            </table>
        </div>
    </div>
    % end

    % if defined('error') and error:
    <div class="result-error">❌ {{error}}</div>
    % end

    % if _result:
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Всего транзакций</div>
                <div class="stat-value">{{_result['total_tx']}}</div>
                <div class="stat-sub">рёбер в графе</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Кошельков (вершин)</div>
                <div class="stat-value">{{_result['total_wallets']}}</div>
                <div class="stat-sub">уникальных адресов</div>
            </div>
            <div class="stat-card highlight">
                <div class="stat-label">Макс. длина цепочки</div>
                <div class="stat-value">{{_result['max_chain_len']}}</div>
                <div class="stat-sub">транзакций подряд</div>
            </div>
            <div class="stat-card {{'alert' if _result['suspicious_count'] > 0 else ''}}">
                <div class="stat-label">Подозрительных путей</div>
                <div class="stat-value">{{_result['suspicious_count']}}</div>
                <div class="stat-sub">порог: {{_result['threshold']}}</div>
            </div>
        </div>

        % if _result['suspicious_count'] > 0:
        <div class="warning-banner">⚠️ Обнаружено {{_result['suspicious_count']}} подозрительных цепочек с глубиной ≥ {{_result['threshold']}}. Возможен слоинг.</div>
        % end

        <div class="card card--results">
            <h2>🔎 Максимальные бесциклические пути <span class="result-badge">{{len(_result['paths'])}} путей</span></h2>
            % if _result['paths']:
            <div class="chains-list">
                % for idx, path in enumerate(_result['paths']):
                <div class="chain-card {{'suspicious' if path['is_suspicious'] else ''}}">
                    <div class="chain-meta">
                        <div class="chain-rank">#{{idx + 1}}</div>
                        <div class="chain-tag {{'suspicious' if path['is_suspicious'] else 'normal'}}">
                            {{'⚠ Подозрительный' if path['is_suspicious'] else '✓ Нормальный'}}
                        </div>
                    </div>
                    <div class="chain-route">
                        % for i, node in enumerate(path['nodes']):
                        <div class="route-node {{'start' if i == 0 else ''}} {{'suspicious' if path['is_suspicious'] else ''}}">{{node[:6]}}</div>
                        % if i < len(path['nodes']) - 1:
                        <div class="route-arrow {{'danger' if path['is_suspicious'] else ''}}">→</div>
                        % end
                        % end
                    </div>
                    <div class="chain-stats">
                        <div class="stat-chip">Транзакций: <span class="val">{{path['edge_count']}}</span></div>
                        <div class="stat-chip">Объём: <span class="val">{{path['total_amount']}}</span></div>
                        <div class="stat-chip">Начало: <span class="val">{{path['start_ts']}}</span></div>
                        <div class="stat-chip">Конец: <span class="val">{{path['end_ts']}}</span></div>
                    </div>
                </div>
                % end
            </div>
            % else:
            <p style="color: var(--slate-500); font-size: 0.95rem; font-weight: 600;">Пути не найдены. Проверьте входные данные.</p>
            % end
        </div>

        <div class="card">
            <h2>📋 Список транзакций</h2>
            <div class="tx-table-wrapper">
                <table class="tx-table">
                    <thead>
                        <tr><th>#</th><th>Отправитель</th><th>Получатель</th><th>Сумма</th><th>Временная метка</th><th>В пути</th></tr>
                    </thead>
                    <tbody>
                        % for i, tx in enumerate(_result['transactions']):
                        <tr class="{{'highlighted' if tx['in_suspicious_path'] else ''}}">
                            <td>{{i + 1}}</td>
                            <td class="addr">{{tx['sender']}}</td>
                            <td class="addr">{{tx['receiver']}}</td>
                            <td class="amount">{{tx['amount']}}</td>
                            <td>{{tx['timestamp']}}</td>
                            <td>{{'⚠ Да' if tx['in_suspicious_path'] else '—'}}</td>
                        </tr>
                        % end
                    </tbody>
                </table>
            </div>
        </div>
    % end
</div>

<script>
document.addEventListener('DOMContentLoaded', () => {
    const accordion = document.querySelector('.accordion');
    const header    = accordion.querySelector('.accordion-header');
    header.addEventListener('click', () => accordion.classList.toggle('open'));
});

function copyExample() {
    const text = `A1B2C3 D4E5F6 50000.00 1700000001\nD4E5F6 G7H8I9 49500.00 1700000120\nG7H8I9 J0K1L2 49000.00 1700000300\nJ0K1L2 M3N4O5 48200.00 1700000540\nP6Q7R8 S9T0U1 1200.00 1700001000\nS9T0U1 V2W3X4 600.00 1700001200\nA1B2C3 P6Q7R8 3000.00 1699999800`;
    navigator.clipboard.writeText(text).then(() => {
        const btn = document.querySelector('.btn-copy');
        const orig = btn.textContent;
        btn.textContent = '✅ Скопировано!';
        setTimeout(() => btn.textContent = orig, 2000);
    });
}
</script>
