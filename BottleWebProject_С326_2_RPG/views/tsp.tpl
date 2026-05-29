% rebase('layout.tpl', title='Главная страница', year=year)
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Планирование экскурсий — TSP</title>
  
  <link rel="stylesheet" type="text/css" href="/static/content/bootstrap.min.css" />
  <link rel="stylesheet" type="text/css" href="/static/content/menu.css" />
  <link rel="stylesheet" type="text/css" href="/static/content/tsp.css" />
</head>
<body>
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
    <div class="alert alert-danger" style="border-radius: 12px; font-weight: 700; margin-bottom: 25px; padding: 15px;">
      ⚠️ {{_errors['global']}}
    </div>
  % end

  <details class="theory-accordion" {{'open' if not _result else ''}}>
    <summary>📖 Справка: Теория и пошаговый разбор алгоритма TSP</summary>
    <div class="theory-content">
      <h3>Теоретическая база: Комбинация алгоритма Дейкстры и Полного перебора</h3>
      <p>Для поиска оптимального туристического маршрута (задачи коммивояжёра) в условиях неполного графа используется последовательный двухэтапный подход. Он гарантирует нахождение точного и кратчайшего циклического пути, даже если между отелем и ключевыми объектами нет прямых дорог.</p>
      
      <ol>
        <li><strong>Этап 1: Алгоритм Дейкстры</strong><br>
        Используется для расчёта кратчайших путей от одной вершины графа до всех остальных. С помощью приоритетной очереди алгоритм быстро находит скрытые оптимальные маршруты в обход промежуточных узлов. Этот шаг выполняется для отеля и каждой достопримечательности отдельно, чтобы построить <em>матрицу расстояний</em> между ними.</li>
        
        <li><strong>Этап 2: Полный перебор перестановок (Brute Force)</strong><br>
        Алгоритм берёт список из всех выбранных достопримечательностей и генерирует абсолютно все возможные последовательности их посещения. Общее число таких вариантов равно факториалу количества объектов (M!). Для каждого варианта вычисляется длина полного пути с обязательным возвратом в отель, после чего выбирается маршрут с минимальным временем.</li>
      </ol>
      <p>Временная сложность перебора составляет <strong>O(M!)</strong>. При ограничении количества объектов M &le; 8 максимальное число комбинаций составляет всего 8! = 40 320 вариантов, что обрабатывается алгоритмом практически мгновенно.</p>

      <hr style="border-color: #e2e8f0; margin: 20px 0;">

      <h3>Пошаговый разбор на конкретном примере</h3>
      <p>Исходные данные: <strong>Отель 'A'</strong>, выбранные достопримечательности для посещения: <strong>['B', 'E', 'F']</strong>.</p>

      <h4>Шаг 1: Построение матрицы кратчайших расстояний</h4>
      <p>Сначала алгоритм Дейкстры вычисляет реальные минимальные расстояния между ключевыми точками (например, кратчайший путь из А в Е физически проходит через промежуточные узлы B и D, а его общая стоимость равна 7). Результат заносится в таблицу:</p>
      
      <table class="table table-bordered math-table" style="max-width: 500px; background: #ffffff; border-radius: 8px; overflow: hidden; margin-bottom: 20px;">
        <thead style="background: #f1f5f9;">
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
            <td>0</td>
            <td>4</td>
            <td>7</td>
            <td>10</td>
          </tr>
          <tr>
            <td><strong>B (Объект)</strong></td>
            <td>4</td>
            <td>0</td>
            <td>3</td>
            <td>6</td>
          </tr>
          <tr>
            <td><strong>E (Объект)</strong></td>
            <td>7</td>
            <td>3</td>
            <td>0</td>
            <td>5</td>
          </tr>
          <tr>
            <td><strong>F (Объект)</strong></td>
            <td>10</td>
            <td>6</td>
            <td>5</td>
            <td>0</td>
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
      <p><strong>Оптимальный маршрут:</strong> A &rarr; B &rarr; E &rarr; F &rarr; A <br>
      <strong>Минимальное время:</strong> 22 ед.</p>
    </div>
  </details>

  <div class="row" style="margin-top: 25px; display: flex; align-items: stretch;">
    
    <div class="col-lg-5 col-md-12" style="margin-bottom: 25px; display: flex; flex-direction: column;">
      <form method="POST" action="/excursion" enctype="multipart/form-data" novalidate style="display: flex; flex-direction: column; flex-grow: 1;">
        <input type="hidden" id="buttonAction" name="action" value="solve">

        <div class="tsp-card" style="margin-top: 0; flex-grow: 1; display: flex; flex-direction: column; justify-content: space-between;">
          <div>
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; margin-bottom: 20px;">
              <h2 style="margin: 0; font-size: 20px;">Параметры графа</h2>
              
              <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                <button type="submit" onclick="document.getElementById('buttonAction').value='generate';" class="btn-generate-tsp" style="margin: 0; height: 38px; padding: 0 12px; font-size: 13px;">
                  🎲 Случайный
                </button>
                
                <label class="btn-generate-tsp" style="margin: 0; background-color: #f1f5f9; color: #0f172a; border: 1px solid #cbd5e1; display: inline-flex; align-items: center; justify-content: center; height: 38px; padding: 0 12px; font-size: 13px; cursor: pointer; font-weight: 700;">
                  📂 Загрузить из файла .txt
                  <input type="file" name="txt_file" accept=".txt" onchange="document.getElementById('buttonAction').value='load_txt'; this.form.submit();" style="display: none;">
                </label>
              </div>
            </div>
       
            <div class="fields-row">
       
              <div class="field">
                <label for="n">Вершины N <span class="hint">≤ 50</span></label>
                <input type="number" id="n" name="n" min="1" max="50" value="{{val_n}}" class="{{cls_n}}">
                % if _errors.get('n'):
                  <span class="error-msg">{{_errors['n']}}</span>
                % end
              </div>
       
              <div class="field">
                <label for="m">Объекты M <span class="hint">≤ 8</span></label>
                <input type="number" id="m" name="m" min="1" max="8" value="{{val_m}}" class="{{cls_m}}">
                % if _errors.get('m'):
                  <span class="error-msg">{{_errors['m']}}</span>
                % end
              </div>
       
              <div class="field">
                <label for="k">Отель K</label>
                <input type="number" id="k" name="k" min="1" value="{{val_k}}" class="{{cls_k}}">
                % if _errors.get('k'):
                  <span class="error-msg">{{_errors['k']}}</span>
                % end
              </div>
       
            </div>
       
            <div class="field field-full" style="margin-top: 15px;">
              <label for="edges">Рёбра графа <span class="hint">в строку: u v w</span></label>
              <textarea id="edges" name="edges" placeholder="1 2 5&#10;2 3 3&#10;1 3 10" style="height: 180px;" class="{{cls_edges}}">{{val_edges}}</textarea>
              % if _errors.get('edges'):
                <span class="error-msg">{{_errors['edges']}}</span>
              % end
            </div>
       
            <div class="field field-full">
              <label for="sites">Достопримечательности <span class="hint">через пробел</span></label>
              <input type="text" id="sites" name="sites" placeholder="2 3 4" value="{{val_sites}}" style="font-family:monospace" class="{{cls_sites}}">
              % if _errors.get('sites'):
                <span class="error-msg">{{_errors['sites']}}</span>
              % end
            </div>
          </div>
     
          <button type="submit" onclick="document.getElementById('buttonAction').value='solve';" class="btn-primary-tsp" style="width: 100%; padding: 14px; font-size: 16px; margin-top: 20px;">Найти оптимальный маршрут</button>
        </div>
      </form>
    </div>

    <div class="col-lg-7 col-md-12" style="margin-bottom: 25px; display: flex; flex-direction: column; gap: 25px;">
      
      <div class="tsp-card" style="margin-top: 0; margin-bottom: 0; flex-grow: 1; display: flex; flex-direction: column;">
        <h2>Визуализация структуры графа и путей</h2>
        <div class="canvas-container" id="canvas-container" style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; flex-grow: 1; display: flex; align-items: center; justify-content: center; min-height: 400px;">
          % if _svg:
            {{!_svg}}
          % else:
            <div class="canvas-placeholder" style="text-align: center; color: #64748b; padding: 40px; border: 2px dashed #cbd5e1; border-radius: 8px; background: #ffffff; width: 92%; height: 88%; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 10px;">
              <span style="font-size: 40px; opacity: 0.7;">🕸️</span>
              <div style="font-weight: 600; color: #334155; font-size: 15px;">Рабочая область графа пуста</div>
              <div style="font-size: 13px; color: #64748b; max-width: 320px; line-height: 1.4;">Заполните параметры слева, сгенерируйте случайный граф или загрузите готовый шаблон из файла .txt</div>
            </div>
          % end
        </div>
      </div>

      % if _result is not None:
        % if _result.get('reachable'):
          <div class="result-card" style="margin-bottom: 0;">
            <h2>Оптимальный маршрут</h2>
            <div class="result-badge">Маршрут найден</div>
     
            <div class="route-path" style="display: flex; flex-wrap: wrap; align-items: center; gap: 10px; margin: 20px 0;">
              % for idx, node in enumerate(_result['path']):
                % is_hotel = (idx == 0 or idx == len(_result['path']) - 1)
                % node_cls = 'route-node hotel' if is_hotel else 'route-node'
                <div class="{{node_cls}}">{{node}}</div>
                % if idx < len(_result['path']) - 1:
                  <span class="route-arrow" style="color: #64748b; font-weight: bold;">&#8594;</span>
                % end
              % end
            </div>
     
            <p class="total-time" style="font-size: 16px; margin: 0;">
              Суммарное время: <strong style="font-size: 20px; color: #1e40af;">{{_result['total_time']}}</strong> ед.
            </p>
          </div>
          
          % if _result.get('matrix') and _result.get('nodes'):
            <div class="tsp-card" style="margin-top: 0; margin-bottom: 0;">
              <h2 style="margin-bottom: 5px;">📊 Матрица кратчайших расстояний (Дейкстра)</h2>
              <p class="text-muted" style="font-size: 13px; margin-bottom: 15px;">
                Промежуточный этап расчёта: минимальное время перемещения между ключевыми точками, вычисленное алгоритмом Дейкстры.
              </p>
              
              <div class="table-responsive matrix-container">
                <table class="table matrix-table">
                  <thead>
                    <tr>
                      <th>От \ До</th>
                      % for node in _result['nodes']:
                        <th>
                          {{node}}
                          % if str(node) == str(val_k):
                            <span class="hotel-marker">ОТЕЛЬ</span>
                          % end
                        </th>
                      % end
                    </tr>
                  </thead>
                  <tbody>
                    % for u in _result['nodes']:
                      <tr>
                        <td class="row-header">
                          {{u}}
                        </td>
                        % for v in _result['nodes']:
                          % val = _result['matrix'].get(u, {}).get(v, float('inf'))
                          
                          % if val == float('inf'):
                            <td class="cell-value cell-muted">&infin;</td>
                          % elif u == v:
                            <td class="cell-value cell-muted">0</td>
                          % else:
                            <td class="cell-value">{{val}}</td>
                          % end
                        % end
                      </tr>
                    % end
                  </tbody>
                </table>
              </div>
            </div>
          % end

        % else:
          <div class="result-error" style="background: #fef2f2; border: 1px solid #fca5a5; color: #991b1b; padding: 15px; border-radius: 12px; font-weight: 700; margin-bottom: 0;">
            ⚠️ Маршрут не найден — граф несвязен или не все вершины достижимы из отеля.
          </div>
        % end
      % end
      
    </div>
  </div>
 
</div>
</body>
</html>