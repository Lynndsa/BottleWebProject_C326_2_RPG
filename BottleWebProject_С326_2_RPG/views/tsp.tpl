% rebase('layout.tpl', title='Главная страница', year=year)

<link rel="stylesheet" type="text/css" href="/static/content/menu.css" />
<link rel="stylesheet" type="text/css" href="/static/content/tsp.css" />

<div class="container-tsp">
 
% _form   = defined('form')   and form   or {}
% _errors = defined('errors') and errors or {}
% _result = defined('result') and result or None
% _svg    = defined('svg_html') and svg_html or None
 
% val_n     = _form.get('n',     '')
% val_m     = _form.get('m',     '')
% val_k     = _form.get('k',     '')
% val_edges = _form.get('edges', '')
% val_sites = _form.get('sites', '')
 
% cls_n     = 'is-error' if _errors.get('n')     else ''
% cls_m     = 'is-error' if _errors.get('m')     else ''
% cls_k     = 'is-error' if _errors.get('k')     else ''
% cls_edges = 'is-error' if _errors.get('edges') else ''
% cls_sites = 'is-error' if _errors.get('sites') else ''
 
  <h1 class="page-title">Планирование экскурсий</h1>
  <p class="subtitle">Оптимальный маршрут туриста — задача коммивояжёра (TSP)</p>
 
  % if _errors.get('global'):
    <div class="alert alert-danger tsp-alert-danger">
      ⚠️ {{_errors['global']}}
    </div>
  % end

  <div class="card-panel theory-card-wrapper">
    <details class="theory-accordion-clean" {{'open' if not _result else ''}}>
      <summary>📖 Справка: Теория и пошаговый разбор алгоритма TSP</summary>
      <div class="theory-content-white">
        
        <h3>Теоретическая база: Комбинация алгоритма Дейкстры и Полного перебора</h3>
        <p>Для поиска оптимального туристического маршрута (задачи коммивояжёра) в условиях неполного графа используется последовательный двухэтапный подход. Он гарантирует нахождение точного и кратчайшего циклического пути, даже если между отелем и ключевыми объектами нет прямых дорог.</p>
        
        <ol>
          <li><strong>Этап 1: Алгоритм Дейкстры</strong><br>
          Используется для расчёта кратчайших путей от одной вершины графа до всех остальных. С помощью приоритетной очереди алгоритм быстро находит скрытые оптимальные маршруты в обход промежуточных узлов. Этот шаг выполняется для отеля и каждой достопримечательности отдельно, чтобы построить <em>матрицу расстояний</em> между ними.</li>
          
          <li><strong>Этап 2: Полный перебор перестановок (Brute Force)</strong><br>
          Алгоритм берёт список из всех выбранных достопримечательностей и генерирует абсолютно все возможные последовательности их посещения. Общее число таких вариантов равно факториалу количества объектов (M!). Для каждого варианта вычисляется длина полного пути с обязательным возвратом в отель, после чего выбирается маршрут с минимальным временем.</li>
        </ol>
        <p>Временная сложность перебора составляет <strong>O(M!)</strong>. При ограничении количества объектов M &le; 8 максимальное число комбинаций составляет всего 8! = 40 320 вариантов, что обрабатывается алгоритмом практически мгновенно.</p>

        <hr>

        <h3>Пошаговый разбор на конкретном примере</h3>
        <p>Исходные данные: <strong>Отель 'A'</strong>, выбранные достопримечательности для посещения: <strong>['B', 'E', 'F']</strong>.</p>
        
        <div class="theory-img-wrapper">
          <img src="/static/content/image/excursion_theory_base.svg" alt="Схема исходного графа" class="theory-img">
          <p class="theory-caption"><em>Рисунок 1. Исходная структура графа. Темный узел — отель, голубые — объекты.</em></p>
        </div>

        <h4>Шаг 1: Построение матрицы кратчайших расстояний</h4>
        <p>Сначала алгоритм Дейкстры вычисляет реальные минимальные расстояния между ключевыми точками (например, кратчайший путь из А в Е физически проходит через промежуточные узлы B и D, а его общая стоимость равна 7). Результат заносится в таблицу:</p>
        
        <table class="table table-bordered math-table math-table-custom">
          <thead>
            <tr>
              <th>Ключевой узел</th>
              <th>До A (Отель)</th>
              <th>До B</th>
              <th>До E</th>
              <th>До F</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><strong>A (Отель)</strong></td>
              <td>0</td><td>4</td><td>7</td><td>10</td>
            </tr>
            <tr>
              <td><strong>B (Объект)</strong></td>
              <td>4</td><td>0</td><td>3</td><td>6</td>
            </tr>
            <tr>
              <td><strong>E (Объект)</strong></td>
              <td>7</td><td>3</td><td>0</td><td>5</td>
            </tr>
            <tr>
              <td><strong>F (Объект)</strong></td>
              <td>10</td><td>6</td><td>5</td><td>0</td>
            </tr>
          </tbody>
        </table>

        <h4>Шаг 2: Расчёт длин всех возможных замкнутых маршрутов</h4>
        <p>Для трёх объектов существует ровно 3! = 6 перестановок порядка их обхода. Алгоритм последовательно проверяет длину каждого получившегося цикла:</p>
        
        <ul>
          <li><code>A &rarr; B &rarr; E &rarr; F &rarr; A</code> = 4 + 3 + 5 + 10 = <strong>22</strong> (Оптимально)</li>
          <li><code>A &rarr; B &rarr; F &rarr; E &rarr; A</code> = 4 + 6 + 5 + 7 = <strong>22</strong> (Оптимально)</li>
          <li><code>A &rarr; E &rarr; B &rarr; F &rarr; A</code> = 7 + 3 + 6 + 10 = 26</li>
          <li><code>A &rarr; E &rarr; F &rarr; B &rarr; A</code> = 7 + 5 + 6 + 4 = <strong>22</strong> (Оптимально)</li>
          <li><code>A &rarr; F &rarr; B &rarr; E &rarr; A</code> = 10 + 6 + 3 + 7 = 26</li>
          <li><code>A &rarr; F &rarr; E &rarr; B &rarr; A</code> = 10 + 5 + 3 + 4 = <strong>22</strong> (Оптимально)</li>
        </ul>

        <h4>Итоговый результат</h4>
        <p>Минимальное время для полного обхода всех точек равно 22 единицам. Алгоритм фиксирует первую найденную цепочку вершин с таким весом и передаёт её для вывода на экран:</p>
        
        <div class="theory-img-wrapper">
          <img src="static/content/image/excursion_theory_path.svg" alt="Визуализация оптимального маршрута" class="theory-img">
          <p class="theory-caption"><em>Рисунок 2. Оптимальный замкнутый маршрут: A → B → E → F → A. Жирным выделены рёбра пути.</em></p>
        </div>

        <p><strong>Оптимальный маршрут:</strong> A &rarr; B &rarr; E &rarr; F &rarr; A <br>
        <strong>Минимальное время:</strong> 22 ед.</p>
      </div>
    </details>
  </div>

  <div class="tsp-grid">
    
    <div class="card-panel">
      <h2>Параметры графа</h2>
      
      <div class="preset-buttons">
        <button type="button" class="btn btn-light btn-sm btn-preset">🎲 Случайный</button>
        <button type="button" class="btn btn-light btn-sm btn-preset">📁 Из .txt</button>
      </div>
      
      <form action="/excursion" method="POST">
        <div class="inputs-inline-row">
          <div class="form-group form-group-flex">
            <label class="form-label-custom">Вершины N <small>&le; 50</small></label>
            <input type="number" name="n" class="form-control form-control-custom {{cls_n}}" value="{{val_n}}" placeholder="10" min="1" max="50">
          </div>
          <div class="form-group form-group-flex">
            <label class="form-label-custom">Объекты M <small>&le; 8</small></label>
            <input type="number" name="m" class="form-control form-control-custom {{cls_m}}" value="{{val_m}}" placeholder="4" min="1" max="8">
          </div>
          <div class="form-group form-group-flex">
            <label class="form-label-custom">Отель K</label>
            <input type="number" name="k" class="form-control form-control-custom {{cls_k}}" value="{{val_k}}" placeholder="1">
          </div>
        </div>

        <div class="form-group mb-20">
          <label class="form-label-custom">Рёбра графа <small class="text-muted-dark">в строку: u v w</small></label>
          <textarea name="edges" class="form-control form-control-custom {{cls_edges}}" rows="5" placeholder="1 2 5&#10;2 3 3&#10;1 3 10">{{val_edges}}</textarea>
        </div>

        <div class="form-group mb-25">
          <label class="form-label-custom">Достопримечательности <small class="text-muted-dark">через пробел</small></label>
          <input type="text" name="sites" class="form-control form-control-custom {{cls_sites}}" value="{{val_sites}}" placeholder="2 3 4">
        </div>

        <button type="submit" class="btn btn-primary w-100 btn-submit-tsp">
          Найти оптимальный маршрут
        </button>
      </form>
    </div>

    <div class="card-panel">
      <h2>Визуализация структуры графа и путей</h2>
      
      <div class="visual-container">
        % if _svg:
          <div class="graph-svg-output">
            {{!_svg}}
          </div>
        % elif _result:
          <div class="result-text-output">
            <h4>Результат расчёта:</h4>
            <p class="result-p"><strong>Оптимальный путь:</strong> <span class="text-highlight-blue">{{_result.get('path_str', '')}}</span></p>
            <p class="result-p"><strong>Минимальное время:</strong> <span class="text-highlight-green">{{_result.get('min_weight', '')}}</span> ед.</p>
          </div>
        % else:
          <p class="placeholder-text">
            Заполните поля параметров и рёбер графа для генерации визуальной схемы
          </p>
        % end
      </div>
    </div>

  </div>
</div>
