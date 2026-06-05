% rebase('layout.tpl', title=title, year=year)

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
    <div class="alert alert-danger bfs-alert-danger">
      ⚠️ {{_errors['global']}}
    </div>
  % end

  <div class="card-panel theory-card-wrapper-clean">
    <details class="theory-accordion-clean">
      <summary>
        📖 Справка: Теория и пошаговый разбор стохастического BFS
      </summary>
      
      <div class="theory-content-white">
        <h2>Теоретическая база: Вероятностный обход графа в ширину (Probabilistic BFS)</h2>
        <p>
          Для симуляции распространения инфекций по топологии контактов применяется модифицированный алгоритм BFS, совмещённый со стохастическим моделированием методом Монте-Карло.
        </p>
        
        <ol>
          <li><strong>Препроцессинг (BFS Connectivity):</strong> Алгоритм проверяет граф от стартовых очагов на связность, вычисляя теоретически достижимый максимум вершин X. При обнаружении изолированных кластеров генерируется предупреждение.</li>
          <li><strong>Стохастическая симуляция:</strong> На каждом шаге (уровне волны BFS) вирус пытается заразить восприимчивых соседей текущего фронта. Для каждого ребра генерируется случайное число: если Rand(0..1) менее p, узел переходит в статус заражённого и помещается в очередь Q.</li>
          <li><strong>Метод Монте-Карло:</strong> Из-за случайного характера процесса симуляция повторяется циклически I раз, после чего рассчитываются средние статистические показатели.</li>
        </ol>

        <hr class="theory-divider">

        <div class="theory-flex-row">
          <div class="theory-col-main">
            <h3>Разбор примера симуляции (при вероятности заражения p = 0.50)</h3>
            
            <h4>Шаг 1: Инициализация и первый очаг</h4>
            <p>
              В качестве стартового очага выбран <strong>Узел 1</strong>. Очередь инфекционного фронта: <code class="code-badge-q">Q = [1]</code>. Текущий шаг времени <code class="code-badge-bold">Step = 0</code>.
            </p>

            <h4>Шаг 2: Первая волна распространения (Step = 1)</h4>
            <p>
              Узел 1 извлекается из очереди. Его соседи в сети — узлы 2 и 3. Для каждой связи генерируется случайное число:
            </p>
            <ul>
              <li>Ребро (1 → 2): сгенерировано <code class="code-badge-bold">0.34</code>. Так как 0.34 &lt; 0.50 — <strong class="code-badge-bold">Узел 2 заражён</strong>. <span class="mark-success">✓</span></li>
              <li>Ребро (1 → 3): сгенерировано <code class="code-badge-bold">0.71</code>. Так как 0.71 &ge; 0.50 — узел 3 устоял (здоров). <span class="mark-fail">✗</span></li>
            </ul>
            <p>
              Новая очередь фронта: <code class="code-badge-q">Q = [2]</code>.
            </p>

            <h5>Шаг 3: Вторая волна распространения (Step = 2)</h5>
            <p>
              Узел 2 извлекается из очереди. Его невылеченный и восприимчивый сосед — Узел 4.
            </p>
            <ul>
              <li>Ребро (2 → 4): сгенерировано <code class="code-badge-bold">0.12</code>. Так как 0.12 &lt; 0.50 — <strong class="code-badge-bold">Узел 4 заражён</strong>. <span class="mark-success">✓</span></li>
            </ul>
            <p>
              Очередь: <code class="code-badge-q">Q = [4]</code>. На следующем шаге у узла 4 нет здоровых соседей. Симуляция завершена.
            </p>

            <p class="simulation-summary text-box-simulation">
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
              <span class="visual-scheme-title">СХЕМА ПЕРЕДАЧИ ИНФЕКЦИИ В ПРИМЕРЕ</span>
              <div class="visual-nodes-chain">
                <div class="node-circle root">1</div>
                <div class="node-arrow">──&gt;</div>
                <div class="node-circle wave1">2</div>
                <div class="node-arrow">──&gt;</div>
                <div class="node-circle wave2">4</div>
              </div>
              <div class="scheme-failure-text">
                <span>Узел [3]</span> <span class="failure-badge">❌ p-тест провален</span>
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

  <form action="/bfs" method="POST" enctype="multipart/form-data" id="bfs-form" onsubmit="prepareVInfString()">

    <input type="file" name="txt_file" id="txt_file_input" accept=".txt" style="display:none" onchange="document.getElementById('bfs-form').submit()">
    <input type="hidden" name="v_inf" id="hidden-v-inf" value="{{val_v_inf}}">

    <div class="bfs-grid-row">

      <div class="grid-col-settings">
        <div class="card-panel settings-panel">
          <h2>Параметры симуляции</h2>

          <div class="preset-buttons">
            <button type="submit" formaction="/bfs/random" class="btn-preset form-flex-btn">
              Сгенерировать сеть
            </button>
            <button type="button" class="btn-preset form-flex-btn" onclick="document.getElementById('txt_file_input').click()">
              Файл конфигурации (.txt)
            </button>
          </div>

          <div class="inputs-inline-row">
            <div class="flex-input-n">
              <label class="form-label-custom">Узлы (N)</label>
              <input type="number" name="n" id="input-n" class="form-control-custom {{cls_n}}" value="{{val_n}}" placeholder="50" min="1" max="50">
            </div>
            <div class="flex-input-m">
              <label class="form-label-custom">Очаги (M)</label>
              <input id="m_input" type="number" name="m" class="form-control-custom {{cls_m}}" value="{{val_m}}" placeholder="12" min="1" max="80">
            </div>
            <div class="flex-input-p">
              <label class="form-label-custom">Вероятность (p)</label>
              <input type="number" name="p" step="0.01" class="form-control-custom {{cls_p}}" value="{{val_p}}" placeholder="0.5" min="0" max="1">
            </div>
            <div class="flex-input-iter">
              <label class="form-label-custom">Итераций (I)</label>
              <input type="number" name="iter" class="form-control-custom {{cls_iter}}" value="{{val_iter}}" placeholder="100" min="1" max="1000">
            </div>
          </div>

          <div class="form-group-container">
            <label class="form-label-custom label-block">Начальные очаги заражения (ID вершин)</label>
            <div id="infected-inputs-container" class="infected-chips-wrapper"></div>
            
            % if _errors.get('v_inf'):
              <div class="error-msg-v-inf">⚠️ {{_errors['v_inf']}}</div>
            % end
          </div>

          <button type="submit" class="btn-submit-bfs">
            Запустить симуляцию вспышки
          </button>

        </div>
      </div>

      <div class="card-panel edges-table-wrapper grid-col-edges">
        <h2>Связи в сети (Рёбра графа)</h2>

        % if _errors.get('edges'):
          <div class="alert alert-danger bfs-alert-danger">
            ⚠️ {{_errors['edges']}}
          </div>
        % end

        <div class="table-responsive" id="matrix-wrapper">
          % if val_n and val_n.isdigit() and int(val_n) > 0:
            % edge_count = len([key for key in _form.keys() if key.startswith('u_')])
            % if edge_count == 0:
              % edge_count = int(val_n)
            % end
            <table class="edges-file-table" id="matrix-table">
              <thead>
                <tr>
                  <th class="col-width-id">#</th>
                  <th>Узел u</th>
                  <th>Узел v</th>
                  <th class="col-width-actions">🗑</th>
                </tr>
              </thead>
              <tbody>
                % for i in range(1, edge_count + 1):
                <tr>
                  <td><strong>{{i}}</strong></td>
                  <td>
                    <input type="text" name="u_{{i}}" class="form-control-custom" value="{{_form.get('u_' + str(i), '')}}" placeholder="1">
                  </td>
                  <td>
                    <input type="text" name="v_{{i}}" class="form-control-custom" value="{{_form.get('v_' + str(i), '')}}" placeholder="2">
                  </td>
                  <td class="cell-center">
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

 <!-- Блок аналитики и результатов -->
 % if _result or _svg:
 <div class="results-wrapper-block">
   <div class="card-panel analytics-master-panel">
     
     <div style="text-align: right; margin-bottom: 20px;">
       <a href="/bfs/download-results" class="btn-preset" style="display: inline-block; background-color: #28a745; color: white; padding: 10px 20px; border-radius: 4px; font-weight: bold; text-decoration: none; text-align: center;">
         📦 Скачать архив результатов (.zip)
       </a>
     </div>

     <h2 class="analytics-main-title">
       📊 Аналитика результатов моделирования
     </h2>
     
     % if _result:
       <div class="analytics-main-row" style="display: flex; flex-wrap: wrap; gap: 25px; margin-bottom: 30px; align-items: flex-start;">
         
         <div class="analytics-text-column" style="flex: 1 1 500px; max-width: 100%;">
           <div class="analytics-text-container" style="padding-right: 10px;">
             <h4 class="analytics-section-title" style="margin-top: 0;">
               Статистические данные метода Монте-Карло:
             </h4>
             
             <div class="analytics-metric-row">
               <strong>Теоретическая достижимость инфекции (X):</strong> 
               <span class="analytics-metric-value">{{_result.get('connectivity_max', 0)}}</span> из {{val_n if val_n else '?'}} узлов популяции.
             </div>
             
             <div class="analytics-metric-row">
               <strong>Средняя длительность вспышки:</strong> 
               <span class="analytics-metric-value">{{_result.get('v_mean', '')}}</span> шагов времени (уровней BFS).
             </div>
             
             <div class="analytics-highlight-badge-row">
               <strong>Средний итоговый уровень заражения:</strong> 
               <span class="analytics-badge-accent">{{_result.get('p_final', '')}}%</span> населения 
               <span class="analytics-badge-subtext">(в среднем ≈ {{_result.get('avg_infected_count', '?')}} узлов из {{val_n if val_n else '?'}})</span>
             </div>
             
             <hr class="analytics-dashed-line">
             
             <p class="analytics-subheading">Дополнительные метрики распределения (по результатам {{_result.get('iterations', 100)}} симуляций):</p>
             <ul class="analytics-extra-metrics-list">
                 <li>Максимальный зафиксированный охват: <strong class="dark-accent-text">{{_result.get('max_infected', 0)}}</strong> узлов ({{"%.1f" % ((_result.get('max_infected', 0) / int(val_n) * 100) if val_n else 0)}}%)</li>
                 <li>Минимальный зафиксированный охват: <strong class="dark-accent-text">{{_result.get('min_infected', 0)}}</strong> узлов</li>
                 <li>Наиболее вероятный исходовый паттерн: <code class="analytics-code-pattern">{{_result.get('most_common_infected', [])}}</code> (встретился в {{_result.get('most_common_percent', 0)}}% всех запусков)</li>
             </ul>
             
             <div class="analytics-info-disclaimer" style="margin-bottom: 0;">
                 <strong>ℹ️ Примечание к расчётам:</strong> Финальный показатель уровня заражения ({{_result.get('p_final', '')}}%) является результатом 
                 математического усреднения по всем итерациям. Исход конкретного единичного случая может иметь отклонения в силу стохастической природы алгоритма.
             </div>
           </div>
         </div>

         <div class="analytics-chart-column" style="flex: 1 1 400px; display: flex; flex-direction: column;">
           % if _result.get('chart_base64'):
             <div class="chart-container-side" style="background: #f8f9fa; border: 1px solid #e3e6f0; border-radius: 6px; padding: 15px; height: 100%;">
               <div class="chart-image-wrapper" style="text-align: center;">
                 <img src="data:image/png;base64,{{_result['chart_base64']}}" alt="Кривая динамики заражения" class="chart-img-fluid" style="max-width: 100%; height: auto; border-radius: 4px;">
               </div>
             </div>
           % end
         </div>

       </div>
     % end

     % if _svg:
       <hr class="analytics-dashed-line" style="margin: 25px 0;">
       <div class="visual-container-full" style="width: 100%;">
         <div class="graph-svg-output-full" style="width: 100%; overflow: auto; text-align: center;">
             {{!_svg}}
         </div>
       </div>
     % end

   </div>
 </div>
 % end
</div>