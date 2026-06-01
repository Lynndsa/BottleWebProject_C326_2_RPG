% rebase('layout.tpl', title='Моделирование распространения вируса', year=year)

<link rel="stylesheet" type="text/css" href="/static/content/menu.css" />
<link rel="stylesheet" type="text/css" href="/static/content/bfs.css" />

<div class="container-bfs">

% _form         = defined('form')     and form     or {}
% _errors      = defined('errors')   and errors   or {}
% _result      = defined('result')   and result   or None
% _svg         = defined('svg_html') and svg_html or None

% val_n        = _form.get('n',        '')
% val_m        = _form.get('m',        '')
% val_p        = _form.get('p',        '')
% val_iter     = _form.get('iter',     '')
% val_v_inf    = _form.get('v_inf',    '')

% cls_n        = 'is-error' if _errors.get('n')        else ''
% cls_m        = 'is-error' if _errors.get('m')        else ''
% cls_p        = 'is-error' if _errors.get('p')        else ''
% cls_iter     = 'is-error' if _errors.get('iter')     else ''
% cls_v_inf    = 'is-error' if _errors.get('v_inf')    else ''

  <h1 class="page-title">Эпидемиология и сетевая безопасность</h1>
  <p class="subtitle">Моделирование распространения вируса в популяции — вероятностный BFS</p>

  % if _errors.get('global'):
    <div class="alert alert-danger bfs-alert-danger" style="margin-bottom: 20px;">
      ⚠️ {{_errors['global']}}
    </div>
  % end

  <div class="card-panel theory-card-wrapper" style="margin-bottom: 25px;">
    <details class="theory-accordion-clean" {{'open' if not _result else ''}}>
      <summary>📖 Справка: Теория и пошаговый разбор стохастического BFS</summary>
      <div class="theory-content-white">

        <h3>Теоретическая база: Вероятностный обход графа в ширину (Probabilistic BFS)</h3>
        <p>Для симуляции распространения инфекций по топологии контактов применяется модифицированный алгоритм BFS, совмещённый со стохастическим моделированием методом Монте-Карло.</p>
        <ol>
          <li><strong>Препроцессинг (BFS Connectivity):</strong> Алгоритм проверяет граф от стартовых очагов на связность, вычисляя теоретически достижимый максимум вершин X. При обнаружении изолированных кластеров генерируется предупреждение.</li>
          <li><strong>Стохастическая симуляция:</strong> На каждом шаге (уровне волны BFS) вирус пытается заразить восприимчивых соседей текущего фронта. Для каждого ребра генерируется случайное число: если Rand(0..1) менее p, узел переходит в статус заражённого и помещается в очередь Q.</li>
          <li><strong>Метод Монте-Карло:</strong> Из-за случайного характера процесса симуляция повторяется циклически I раз, после чего рассчитываются средние статистические показатели.</li>
        </ol>

        <hr style="margin: 25px 0; border: 0; border-top: 1px solid #e2e8f0;">

        <div class="theory-flex-row">
          
          <div class="theory-col-main">
            <h4>Разбор примера симуляции (при вероятности заражения p = 0.50)</h4>
            
            <h5>Шаг 1: Инициализация и первый очаг</h5>
            <p>
              В качестве стартового очага выбран <strong>Узел 1</strong>. Очередь инфекционного фронта: <code class="code-badge-q">Q = [1]</code>. Текущий шаг времени <code class="code-badge-bold">Step = 0</code>.
            </p>

            <h5>Шаг 2: Первая волна распространения (Step = 1)</h5>
            <p>
              Узел 1 извлекается из очереди. Его соседи в сети — узлы 2 и 3. Для каждой связи генерируется случайное число:
            </p>
            <ul>
              <li>Ребро (1 → 2): сгенерировано <code class="code-badge-bold">0.34</code>. Так как 0.34 &lt; 0.50 — <strong class="code-badge-bold">Узел 2 заражён</strong>. <span style="color: #16a34a; font-weight: bold;">✓</span></li>
              <li>Ребро (1 → 3): сгенерировано <code class="code-badge-bold">0.71</code>. Так как 0.71 &ge; 0.50 — узел 3 устоял (здоров). <span style="color: #dc2626; font-weight: bold;">✗</span></li>
            </ul>
            <p>
              Новая очередь фронта: <code class="code-badge-q">Q = [2]</code>.
            </p>

            <h5>Шаг 3: Вторая волна распространения (Step = 2)</h5>
            <p>
              Узел 2 извлекается из очереди. Его невылеченный и восприимчивый сосед — Узел 4.
            </p>
            <ul>
              <li>Ребро (2 → 4): сгенерировано <code class="code-badge-bold">0.12</code>. Так как 0.12 &lt; 0.50 — <strong class="code-badge-bold">Узел 4 заражён</strong>. <span style="color: #16a34a; font-weight: bold;">✓</span></li>
            </ul>
            <p>
              Очередь: <code class="code-badge-q">Q = [4]</code>. На следующем шаге у узла 4 нет здоровых соседей. Симуляция завершена.
            </p>

            <p class="simulation-summary">
              <strong>Итог данной итерации:</strong> Длительность вспышки = <span class="text-steps-count">2 шага</span>. Заражено узлов: 1, 2, 4. Охват популяции = <span class="text-percent-count">75%</span>.
            </p>
          </div>

          <div class="theory-col-side">
            
            <div class="status-legend-box">
              <strong class="status-legend-title">📌 Параметры состояний вершин:</strong>
              <div class="status-row">
                <code class="code-status-healthy">Status[v] == 0</code> — Здоров / Восприимчив
              </div>
              <div class="status-row">
                <code class="code-status-infected">Status[v] == 1</code> — Инфицирован / Активен
              </div>
            </div>

            <div class="visual-scheme-box">
              <span class="visual-scheme-title">Схема передачи инфекции в примере</span>
              
              <div class="visual-nodes-chain">
                <div class="node-circle root">1</div>
                <div class="node-arrow">──&gt;</div>
                <div class="node-circle wave1">2</div>
                <div class="node-arrow">──&gt;</div>
                <div class="node-circle wave2">4</div>
              </div>
              
              <div class="scheme-failure-text">
                <span>Узел [3]</span> 
                <span style="color: #dc2626; font-weight: bold;">❌ p-тест провален</span>
              </div>

              <span class="scheme-caption">
                Рисунок 1. Граф прохождения вирусного фронта по шагам.
              </span>
            </div>

          </div>
          
        </div>

      </div>
    </details>
  </div>

  <form action="/bfs" method="POST" enctype="multipart/form-data" id="bfs-form">

    <input type="file" name="txt_file" id="txt_file_input"
           accept=".txt" style="display:none"
           onchange="document.getElementById('bfs-form').submit()">

    <div class="row" style="display:flex; flex-wrap:wrap; gap:20px; align-items:stretch;">

      <div style="flex:1 1 360px; min-width:360px;">
        <div class="card-panel" style="margin-bottom:0; height:auto;">
          <h2>Параметры симуляции</h2>

          <div class="preset-buttons" style="display:flex; gap:10px; margin-bottom:18px;">
            <button type="submit" formaction="/bfs/random"
                    class="btn-preset" style="flex:1;">
              🎲 Сгенерировать сеть
            </button>
            <button type="button" class="btn-preset" style="flex:1;"
                    onclick="document.getElementById('txt_file_input').click()">
              📁 Файл конфигурации (.txt)
            </button>
          </div>

          <div style="display:flex; gap:10px; margin-bottom:16px;">
            <div style="flex:1.2; min-width:0;">
              <label class="form-label-custom">Узлы (N)</label>
              <input type="number" name="n" id="input-n"
                     class="form-control-custom {{cls_n}}"
                     value="{{val_n}}" placeholder="50" min="1" max="50">
            </div>
            <div style="flex:1.2; min-width:0;">
              <label class="form-label-custom">Очаги (M)</label>
              <input type="number" name="m"
                     class="form-control-custom {{cls_m}}"
                     value="{{val_m}}" placeholder="2" min="1" max="50">
            </div>
            <div style="flex:1.5; min-width:0;">
              <label class="form-label-custom">Вероятность (p)</label>
              <input type="number" name="p" step="0.01"
                     class="form-control-custom {{cls_p}}"
                     value="{{val_p}}" placeholder="0.5" min="0" max="1">
            </div>
            <div style="flex:1.3; min-width:0;">
              <label class="form-label-custom">Итераций (I)</label>
              <input type="number" name="iter"
                     class="form-control-custom {{cls_iter}}"
                     value="{{val_iter}}" placeholder="100" min="1" max="1000">
            </div>
          </div>

          <div class="form-group" style="margin-bottom:20px;">
            <label class="form-label-custom">ID начальных зараженных вершин <small class="text-muted-dark">через пробел</small></label>
            <input type="text" name="v_inf"
                   class="form-control-custom {{cls_v_inf}}"
                   value="{{val_v_inf}}" placeholder="1 5">
          </div>

          <button type="submit" class="btn-submit-bfs">
            Запустить симуляцию вспышки
          </button>

        </div>
      </div>

      <div class="card-panel edges-table-wrapper" style="flex:1 1 340px; min-width:340px;">
        <h2>Связи в сети (Рёбра графа)</h2>

        % if _errors.get('edges'):
          <div class="alert alert-danger bfs-alert-danger" style="margin-bottom:12px;">
            ⚠️ {{_errors['edges']}}
          </div>
        % end

        <div class="table-responsive" id="matrix-wrapper" style="max-height:380px; overflow-y:auto;">
          % if val_n and val_n.isdigit() and int(val_n) > 0:
            % edge_count = len([key for key in _form.keys() if key.startswith('u_')])
            % if edge_count == 0:
              % edge_count = int(val_n)
            % end
            <table class="edges-file-table" id="matrix-table">
              <thead>
                <tr>
                  <th style="width:12%;">#</th>
                  <th>Узел u</th>
                  <th>Узел v</th>
                  <th style="width:60px;">🗑</th>
                </tr>
              </thead>
              <tbody>
                % for i in range(1, edge_count + 1):
                <tr>
                  <td><strong>{{i}}</strong></td>
                  <td>
                    <input type="text" name="u_{{i}}" class="form-control-custom"
                           value="{{_form.get('u_' + str(i), '')}}" placeholder="1">
                  </td>
                  <td>
                    <input type="text" name="v_{{i}}" class="form-control-custom"
                           value="{{_form.get('v_' + str(i), '')}}" placeholder="2">
                  </td>
                  <td style="text-align:center;">
                    <button type="button" class="btn-delete-edge" onclick="removeEdgeRow(this)">🗑</button>
                  </td>
                </tr>
                % end
              </tbody>
            </table>
          % else:
            <p class="placeholder-text placeholder-empty-table">
              Задайте размер популяции N, сгенерируйте случайную сеть или импортируйте её структуру из текстового файла.
            </p>
          % end
        </div>
      </div>

    </div>
  </form>

  <script src="/static/scripts/bfs_edges.js"></script>

  % if _result or _svg:
  <div style="margin-top:20px;">
    <div class="card-panel">
      <h2 style="margin-top:0;">Аналитика результатов и визуализация графа</h2>
      
      <div class="row" style="display:flex; flex-wrap:wrap; gap:20px;">
        
        % if _result:
        <div style="flex:1 1 300px;">
          <div class="result-text-output" style="padding:15px; background:#f8f9fa; border-radius:4px; border-left:4px solid #4caf50;">
            <h4>Статистические данные Монте-Карло:</h4>
            <hr style="margin:10px 0; border: 0; border-top: 1px solid #e2e8f0;">
            <p class="result-p" style="margin-bottom:8px;">
              <strong>Теоретическая достижимость (X):</strong> 
              <span class="text-highlight-blue" style="font-weight:bold;">{{_result.get('connectivity_max', 0)}}</span> из {{val_n}} узлов.
            </p>
            <p class="result-p" style="margin-bottom:8px;">
              <strong>Длительность вспышки (V_mean):</strong> 
              <span class="text-highlight-blue" style="font-weight:bold; font-size:1.1rem;">{{_result.get('v_mean', '')}}</span> шагов времени.
            </p>
            <p class="result-p" style="margin-bottom:0;">
              <strong>Итоговый уровень заражения (P_final):</strong> 
              <span class="text-highlight-green" style="font-weight:bold; font-size:1.2rem;">{{_result.get('p_final', '')}}%</span> населения.
            </p>
          </div>
          
          % if _result.get('chart_base64'):
          <div class="chart-container" style="margin-top:15px; text-align:center;">
            <h5>График интенсивности заражения по шагам</h5>
            <img src="data:image/png;base64,{{_result['chart_base64']}}" alt="Динамика BFS симуляции" style="max-width:100%; border-radius:4px; border:1px solid #ddd;">
          </div>
          % end
        </div>
        % end

        % if _svg:
        <div style="flex:1.3 1 400px; display:flex; flex-direction:column;">
          <div class="visual-container" style="border:1px solid #e0e0e0; border-radius:4px; padding:10px; background:#fff; flex:1; display:flex; align-items:center; justify-content:center;">
            <div class="graph-svg-output" style="width:100%; text-align:center;">{{!_svg}}</div>
          </div>
          <p class="theory-caption" style="text-align:center; margin-top:5px; font-size:0.85rem; color:#666;">
            <em>Цветовая разметка: красные узлы — первичные очаги V_inf, насыщенность градиента рёбер отражает частоту прохождения вирусного фронта.</em>
          </p>
        </div>
        % end

      </div>

    </div>
  </div>
  % end

</div>