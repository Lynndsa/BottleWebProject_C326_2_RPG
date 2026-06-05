% rebase('layout.tpl', title='Главная страница', year=year)

<link rel="stylesheet" type="text/css" href="/static/content/menu.css" />
<link rel="stylesheet" type="text/css" href="/static/content/tsp.css" />

<div class="container-tsp">

% _form   = get('form',     {})
% _errors = get('errors',   {})
% _svg    = get('svg_html', None)
% _result = get('result', None)

% val_n     = _form.get('n',     '')
% val_m     = _form.get('m',     '')
% val_k     = _form.get('k',     '')
% val_sites = _form.get('sites', '')

% cls_n     = 'is-error' if _errors.get('n')     else ''
% cls_m     = 'is-error' if _errors.get('m')     else ''
% cls_k     = 'is-error' if _errors.get('k')     else ''
% cls_sites = 'is-error' if _errors.get('sites') else ''

  <h1 class="page-title">Планирование экскурсий</h1>
  <p class="subtitle">Оптимальный маршрут туриста — задача коммивояжёра (TSP)</p>

  <div class="card-panel theory-card-wrapper">
    <details class="theory-accordion-clean">
      <summary>📖 Справка: Теория и пошаговый разбор алгоритма TSP</summary>
      <div class="theory-content-white">

        <h2>Теоретическая база: Комбинация алгоритма Дейкстры и Полного перебора</h2>
        <p>Для поиска оптимального туристического маршрута (задачи коммивояжёра) в условиях неполного графа используется последовательный двухэтапный подход.</p>
        <ol>
          <li><strong>Этап 1: Алгоритм Дейкстры</strong> — расчёт кратчайших путей от одной вершины графа до всех остальных с помощью приоритетной очереди для построения матрицы расстояний.</li>
          <li><strong>Этап 2: Полный перебор перестановок (Brute Force)</strong> — генерация всех возможных последовательностей посещения объектов (M!) с возвратом в отель и выбором минимума.</li>
        </ol>
        <p>Временная сложность перебора составляет O(M!). При ограничении M ≤ 8 максимальное число комбинаций составляет 8! = 40 320.</p>

        <hr>

        <div class="row align-items-center mb-4">
          <div class="col-md-6">
            <h3>Шаг 1: Построение матрицы кратчайших расстояний</h3>
            <table class="table table-bordered math-table math-table-custom mb-0 maxwidth">
              <thead>
                <tr><th>Ключевой узел</th><th>До A</th><th>До B</th><th>До E</th><th>До F</th></tr>
              </thead>
              <tbody>
                <tr><td><strong>A (Отель)</strong></td><td>0</td><td>4</td><td>7</td><td>10</td></tr>
                <tr><td><strong>B (Объект)</strong></td><td>4</td><td>0</td><td>3</td><td>6</td></tr>
                <tr><td><strong>E (Объект)</strong></td><td>7</td><td>3</td><td>0</td><td>5</td></tr>
                <tr><td><strong>F (Объект)</strong></td><td>10</td><td>6</td><td>5</td><td>0</td></tr>
              </tbody>
            </table>
          </div>
          <div class="col-md-6">
            <div class="theory-img-wrapper centermargin">
              <img src="/static/content/image/excursion_theory_base.svg" alt="Схема графа" class="theory-img">
              <p class="theory-caption" style="margin-bottom:0;"><em>Рисунок 1. Исходная структура графа.</em></p>
            </div>
          </div>
        </div>

        <hr class="otsup1">

        <div class="row align-items-center">
          <div class="col-md-6">
            <h3>Шаг 2: Все возможные маршруты</h3>
            <ul>
              <li><code>A→B→E→F→A</code> = 4+3+5+10 = <strong>22</strong> ✓</li>
              <li><code>A→B→F→E→A</code> = 4+6+5+7 = <strong>22</strong> ✓</li>
              <li><code>A→E→B→F→A</code> = 7+3+6+10 = 26</li>
              <li><code>A→E→F→B→A</code> = 7+5+6+4 = <strong>22</strong> ✓</li>
              <li><code>A→F→B→E→A</code> = 10+6+3+7 = 26</li>
              <li><code>A→F→E→B→A</code> = 10+5+3+4 = <strong>22</strong> ✓</li>
            </ul>
            <p><strong>Оптимальный маршрут:</strong> A→B→E→F→A<br><strong>Минимальное время:</strong> 22 ед.</p>
          </div>
          <div class="col-md-6">
            <div class="theory-img-wrapper">
              <img src="/static/content/image/excursion_theory_path.svg" alt="Оптимальный маршрут" class="theory-img">
              <p class="theory-caption"><em>Рисунок 2. Оптимальный маршрут A→B→E→F→A.</em></p>
            </div>
          </div>
        </div>

      </div>
    </details>
  </div>

  <form action="/tsp" method="POST" enctype="multipart/form-data" id="tsp-form">
    <input type="file" name="txt_file" id="txt_file_input"
           accept=".txt,.json" style="display:none"
           onchange="document.getElementById('tsp-form').submit()">

    <div class="two-card">

      <div style="flex:1 1 340px; min-width:340px;">
        <div class="card-panel" style="margin-bottom:0;">
          <h3 style="margin-top:0;">Параметры графа</h3>

          <div class="preset-buttons random">
            <button type="submit" formaction="/tsp/random"
                    class="btn btn-light btn-sm btn-preset" style="flex:1;">
              🎲 Случайный
            </button>
            <button type="button" class="btn btn-light btn-sm btn-preset" style="flex:1;"
                    onclick="document.getElementById('txt_file_input').click()">
              📁 Загрузить из файла
            </button>
          </div>

          <div style="display:flex; gap:10px; margin-bottom:16px;">
            <div style="flex:1; min-width:0;">
              <label class="form-label-custom">Вершины N</label>
              <input type="number" name="n" id="input-n"
                     class="form-control form-control-custom {{cls_n}}"
                     value="{{val_n}}" placeholder="10" min="1" max="50">
            </div>
            <div style="flex:1; min-width:0;">
              <label class="form-label-custom">Объекты M</label>
              <input type="number" name="m"
                     class="form-control form-control-custom {{cls_m}}"
                     value="{{val_m}}" placeholder="4" min="1">
            </div>
            <div style="flex:1; min-width:0;">
              <label class="form-label-custom">Отель K</label>
              <input type="number" name="k" id="input-k"
                     class="form-control form-control-custom {{cls_k}}"
                     value="{{val_k}}" placeholder="1" min="1"
                     max="{{val_n if val_n else 20}}">
            </div>
          </div>

          <div class="form-group" style="margin-bottom:20px;">
            <label class="form-label-custom">Достопримечательности <small class="text-muted-dark">через пробел</small></label>
            <input type="text" name="sites"
                   class="form-control form-control-custom {{cls_sites}}"
                   value="{{val_sites}}" placeholder="2 3 4">
          </div>

          <button type="submit" class="btn-submit-tsp">
            Найти оптимальный маршрут
          </button>

          % if _errors.get('global'):
          <div class="alert alert-danger tsp-alert-danger" style="margin-top:15px; margin-bottom:0;">
            ⚠️ {{_errors['global']}}
          </div>
          % end

        </div>
      </div>

      <div class="card-panel edges-table-wrapper naming">
        <h3>Список рёбер графа</h3>

        % if _errors.get('edges'):
        <div class="alert alert-danger tsp-alert-danger" style="margin-bottom:12px;">
          ⚠️ {{_errors['edges']}}
        </div>
        % end

        <div class="table-responsive table" id="matrix-wrapper">
          % if val_n and val_n.isdigit() and int(val_n) > 0 and int(val_n) < 50:
            % edge_count = len([key for key in _form.keys() if key.startswith('u_')])
            % if edge_count == 0:
              % edge_count = int(val_n)
            % end
            <table class="edges-file-table" id="matrix-table">
              <thead>
                <tr>
                  <th style="width:10%;">#</th>
                  <th>Вершина u (Откуда)</th>
                  <th>Вершина v (Куда)</th>
                  <th>Вес w (Расстояние)</th>
                  <th>Удалить</th>
                </tr>
              </thead>
              <tbody>
                % for i in range(1, edge_count + 1):
                <tr>
                  <td><strong>{{i}}</strong></td>
                  <td><input type="text" name="u_{{i}}" class="form-control-custom"
                             value="{{_form.get('u_' + str(i), '')}}" placeholder="1"></td>
                  <td><input type="text" name="v_{{i}}" class="form-control-custom"
                             value="{{_form.get('v_' + str(i), '')}}" placeholder="2"></td>
                  <td><input type="number" name="w_{{i}}" class="form-control-custom"
                             value="{{_form.get('w_' + str(i), '')}}" min="1" max="20" placeholder="—"></td>
                  <td style="text-align:center;">
                    <button type="button" class="btn-delete-edge" onclick="removeEdgeRow(this)">
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polyline points="3 6 5 6 21 6"></polyline>
                        <path d="M19 6l-1 14H6L5 6"></path>
                        <path d="M10 11v6M14 11v6"></path>
                        <path d="M9 6V4h6v2"></path>
                      </svg>
                    </button>
                  </td>
                </tr>
                % end
              </tbody>
            </table>
          % else:
            <p class="placeholder-text placeholder-empty-table">
              Укажите количество вершин N, выберите случайный пресет или загрузите файл.
            </p>
          % end
        </div>

        <div class="count-vershin">
          <button type="button" id="btn-add-edge" class="btn btn-light btn-sm btn-preset">
            ➕ Добавить ребро
          </button>
        </div>

      </div>

    </div>
    </form>

  <script src="/static/scripts/tsp_edges.js"></script>

  <div class="visual-ostup" id="result-anchor">
    <div class="card-panel">
      <h3 class="visual-text">Визуализация структуры графа и путей</h3>
      <div class="visual-container">
        % if _svg:
          <div id="tsp-wrap" class="graph-svg-output">
            {{!_svg}}
            <div class="visual-navigation">
              <button id="tsp-btn-in" class="btn btn-light btn-sm">+</button>
              <button id="tsp-btn-out" class="btn btn-light btn-sm">−</button>
              <button id="tsp-btn-rst" class="btn btn-light btn-sm">⟳</button>
              <span id="tsp-lbl" class="style">100%</span>
            </div>
          </div>
        % elif _result:
          <div class="result-text-output">
            <h4>Результат расчёта:</h4>
            <p class="result-p">
              <strong>Оптимальный путь:</strong>
              <span class="text-highlight-blue out">
                {{_result.get('path_str', '')}}
              </span>
            </p>
            <p class="result-p">
              <strong>Минимальное время:</strong>
              <span class="text-highlight-green out">
                {{_result.get('min_weight', '')}}
              </span> ед.
            </p>
          </div>
        % else:
          <p class="placeholder-text error">
            Заполните поля параметров и рёбер графа для генерации визуальной схемы
          </p>
        % end
      </div>
    </div>
    
    % _result_id = get('result_id', None)
    % if _result and _result_id:
      <div class="otsup">
        <a href="/tsp/download/{{_result_id}}">
          <button type="button" class="btn-submit-tsp">
            💾 Скачать результат (ZIP)
          </button>
        </a>
      </div>
    % end
  </div>

</div>