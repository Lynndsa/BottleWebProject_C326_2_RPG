% rebase('layout.tpl', title='Главная страница', year=year)

<link rel="stylesheet" type="text/css" href="/static/content/menu.css" />
<link rel="stylesheet" type="text/css" href="/static/content/tsp.css" />

<div class="container-tsp">

% _form        = defined('form')     and form     or {}
% _errors      = defined('errors')   and errors   or {}
% _result      = defined('result')   and result   or None
% _svg         = defined('svg_html') and svg_html or None

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

  % if _errors.get('global'):
    <div class="alert alert-danger tsp-alert-danger" style="margin-bottom: 20px;">
      ⚠️ {{_errors['global']}}
    </div>
  % end

  <div class="card-panel theory-card-wrapper" style="margin-bottom: 25px;">
    <details class="theory-accordion-clean" {{'open' if not _result else ''}}>
      <summary>📖 Справка: Теория и пошаговый разбор алгоритма TSP</summary>
      <div class="theory-content-white">

        <h3>Теоретическая база: Комбинация алгоритма Дейкстры и Полного перебора</h3>
        <p>Для поиска оптимального туристического маршрута (задачи коммивояжёра) в условиях неполного графа используется последовательный двухэтапный подход.</p>
        <ol>
          <li><strong>Этап 1: Алгоритм Дейкстры</strong> — расчёт кратчайших путей от одной вершины графа до всех остальных с помощью приоритетной очереди для построения матрицы расстояний.</li>
          <li><strong>Этап 2: Полный перебор перестановок (Brute Force)</strong> — генерация всех возможных последовательностей посещения объектов (M!) с возвратом в отель и выбором минимума.</li>
        </ol>
        <p>Временная сложность перебора составляет O(M!). При ограничении M ≤ 8 максимальное число комбинаций составляет 8! = 40 320.</p>

        <hr style="margin: 20px 0;">

        <div class="row align-items-center mb-4">
          <div class="col-md-6">
            <h4>Шаг 1: Построение матрицы кратчайших расстояний</h4>
            <table class="table table-bordered math-table math-table-custom mb-0" style="width:100%;">
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
            <div class="theory-img-wrapper" style="margin:0; text-align:center;">
              <img src="/static/content/image/excursion_theory_base.svg" alt="Схема графа" class="theory-img" style="max-height:220px;">
              <p class="theory-caption" style="margin-bottom:0;"><em>Рисунок 1. Исходная структура графа.</em></p>
            </div>
          </div>
        </div>

        <hr style="margin: 20px 0;">

        <div class="row align-items-center">
          <div class="col-md-6">
            <h4>Шаг 2: Все возможные маршруты</h4>
            <ul style="margin-bottom:15px;">
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
            <div class="theory-img-wrapper" style="margin:0; text-align:center;">
              <img src="/static/content/image/excursion_theory_path.svg" alt="Оптимальный маршрут" class="theory-img" style="max-height:220px;">
              <p class="theory-caption" style="margin-bottom:0;"><em>Рисунок 2. Оптимальный маршрут A→B→E→F→A.</em></p>
            </div>
          </div>
        </div>

      </div>
    </details>
  </div>

  <!-- ================================================================
       ФОРМА — охватывает ОБЕ карточки (параметры + таблица рёбер)
  ================================================================ -->
  <form action="/tsp" method="POST" enctype="multipart/form-data" id="tsp-form">

    <input type="file" name="txt_file" id="txt_file_input"
           accept=".txt" style="display:none"
           onchange="document.getElementById('tsp-form').submit()">

    <div class="row" style="display:flex; flex-wrap:wrap; gap:20px; align-items:stretch;">

      <!-- Левая карточка: параметры -->
      <div style="flex:1 1 340px; min-width:340px;">
        <div class="card-panel" style="margin-bottom:0; height:auto;">
          <h2 style="margin-top:0;">Параметры графа</h2>

          <div class="preset-buttons" style="display:flex; gap:10px; margin-bottom:18px;">
            <button type="submit" formaction="/tsp/random"
                    class="btn btn-light btn-sm btn-preset" style="flex:1;">
              🎲 Случайный
            </button>
            <button type="button" class="btn btn-light btn-sm btn-preset" style="flex:1;"
                    onclick="document.getElementById('txt_file_input').click()">
              📁 Загрузить из .txt
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
                     value="{{val_m}}" placeholder="4" min="1" max="8">
            </div>
            <div style="flex:1; min-width:0;">
              <label class="form-label-custom">Отель K</label>
              <input type="number" name="k"
                     class="form-control form-control-custom {{cls_k}}"
                     value="{{val_k}}" placeholder="1">
            </div>
          </div>

          <div class="form-group" style="margin-bottom:20px;">
            <label class="form-label-custom">Достопримечательности <small class="text-muted-dark">через пробел</small></label>
            <input type="text" name="sites"
                   class="form-control form-control-custom {{cls_sites}}"
                   value="{{val_sites}}" placeholder="2 3 4">
          </div>

          <button type="submit" class="btn btn-primary w-100 btn-submit-tsp">
            Найти оптимальный маршрут
          </button>

        </div>
      </div>

      <!-- Правая карточка: таблица рёбер -->
      <div class="card-panel edges-table-wrapper" style="flex:1 1 340px; min-width:340px;">
        <h2>Список рёбер графа</h2>

        % if _errors.get('edges'):
          <div class="alert alert-danger tsp-alert-danger" style="margin-bottom:12px;">
            ⚠️ {{_errors['edges']}}
          </div>
        % end

        <div class="table-responsive" id="matrix-wrapper" style="max-height:380px; overflow-y:auto;">
          % if val_n and val_n.isdigit() and int(val_n) > 0:
            % n_val = int(val_n)
            <table class="edges-file-table" id="matrix-table">
              <thead>
                <tr>
                  <th style="width:10%;">#</th>
                  <th>Вершина u (Откуда)</th>
                  <th>Вершина v (Куда)</th>
                  <th>Вес w (Расстояние)</th>
                </tr>
              </thead>
              <tbody>
                % for i in range(1, n_val + 1):
                <tr>
                  <td><strong>{{i}}</strong></td>
                  <td><input type="text"   name="u_{{i}}" class="form-control-custom"
                             value="{{_form.get('u_' + str(i), '')}}" placeholder="1"></td>
                  <td><input type="text"   name="v_{{i}}" class="form-control-custom"
                             value="{{_form.get('v_' + str(i), '')}}" placeholder="2"></td>
                  <td><input type="number" name="w_{{i}}" class="form-control-custom"
                             value="{{_form.get('w_' + str(i), '')}}" min="1" placeholder="—"></td>
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

        <div style="display:flex; gap:10px; margin-top:15px; align-items:center;">
          <button type="button" id="btn-add-edge"
                  class="btn btn-light btn-sm btn-preset">
            ➕ Добавить ребро
          </button>
        </div>

        <button type="submit" class="btn-submit-tsp"
                style="margin-top:15px; width:100%; max-width:320px;">
          Найти оптимальный маршрут
        </button>
      </div>

    </div>
  </form>

  <script src="/static/scripts/tsp_edges.js"></script>
  <!-- конец формы -->

  <!-- Визуализация -->
  <div style="margin-top:20px;">
    <div class="card-panel">
      <h2 style="margin-top:0;">Визуализация структуры графа и путей</h2>
      <div class="visual-container" style="min-height:250px;">
        % if _svg:
          <div class="graph-svg-output">{{!_svg}}</div>
        % elif _result:
          <div class="result-text-output">
            <h4>Результат расчёта:</h4>
            <p class="result-p"><strong>Оптимальный путь:</strong>
               <span class="text-highlight-blue" style="font-size:1.25rem;">{{_result.get('path_str', '')}}</span></p>
            <p class="result-p"><strong>Минимальное время:</strong>
               <span class="text-highlight-green" style="font-size:1.25rem;">{{_result.get('min_weight', '')}}</span> ед.</p>
          </div>
        % else:
          <p class="placeholder-text" style="padding:60px 0;">
            Заполните поля параметров и рёбер графа для генерации визуальной схемы
          </p>
        % end
      </div>
    </div>
  </div>

</div>
