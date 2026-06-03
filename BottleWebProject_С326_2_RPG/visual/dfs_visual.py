import math

# ---------------------------------------------------------------------------
# Цветовая палитра
# ---------------------------------------------------------------------------
COLOR_SUS_FILL   = '#fff5f5'
COLOR_SUS_STROKE = '#ef4444'
COLOR_SUS_TEXT   = '#b91c1c'
COLOR_SUS_EDGE   = '#ef4444'

COLOR_NORM_FILL   = '#f0f9ff'
COLOR_NORM_STROKE = '#38bdf8'
COLOR_NORM_TEXT   = '#0c4a6e'
COLOR_NORM_EDGE   = '#0ea5e9'

COLOR_START_FILL  = '#0f172a'
COLOR_START_TEXT  = '#ffffff'

COLOR_BG   = '#f8fafc'
COLOR_GRID = '#e2e8f0'


# ---------------------------------------------------------------------------
# Layout: исток в центре, остальные по кругу (или двум кольцам)
# ---------------------------------------------------------------------------
def _circular_layout(
    nodes: list[str],
    sources: set[str],
    suspicious_nodes: set[str],
    width: int,
    height: int,
) -> dict[str, tuple[float, float]]:
    if not nodes:
        return {}

    cx, cy = width / 2, height / 2
    pos: dict[str, tuple[float, float]] = {}

    src_list  = [n for n in nodes if n in sources]
    rest_list = [n for n in nodes if n not in sources]

    # Сортируем: подозрительные узлы группируем вместе на кольце
    rest_list.sort(key=lambda n: (0 if n in suspicious_nodes else 1, n))

    total_outer = len(rest_list)

    if len(src_list) == 1 and total_outer > 0:
        # Один исток — в центре, остальные по кругу
        pos[src_list[0]] = (cx, cy)

        r_outer = min(cx, cy) - 60
        for i, node in enumerate(rest_list):
            # Начинаем с верхней точки (-π/2), по часовой
            angle = -math.pi / 2 + 2 * math.pi * i / total_outer
            pos[node] = (cx + r_outer * math.cos(angle),
                         cy + r_outer * math.sin(angle))

    elif len(src_list) == 0:
        # Нет явного истока — все по кругу
        all_nodes = rest_list
        r = min(cx, cy) - 60
        for i, node in enumerate(all_nodes):
            angle = -math.pi / 2 + 2 * math.pi * i / max(len(all_nodes), 1)
            pos[node] = (cx + r * math.cos(angle),
                         cy + r * math.sin(angle))

    else:
        # Несколько истоков — внутреннее кольцо + внешнее
        n_inner = len(src_list)
        n_outer = total_outer

        r_inner = min(cx, cy) * 0.38
        r_outer = min(cx, cy) - 60

        for i, node in enumerate(src_list):
            angle = -math.pi / 2 + 2 * math.pi * i / max(n_inner, 1)
            pos[node] = (cx + r_inner * math.cos(angle),
                         cy + r_inner * math.sin(angle))

        for i, node in enumerate(rest_list):
            angle = -math.pi / 2 + 2 * math.pi * i / max(n_outer, 1)
            pos[node] = (cx + r_outer * math.cos(angle),
                         cy + r_outer * math.sin(angle))

    return pos


# ---------------------------------------------------------------------------
# SVG-примитивы
# ---------------------------------------------------------------------------
def _svg_marker(marker_id: str, color: str) -> str:
    return (
        f'<marker id="{marker_id}" markerWidth="8" markerHeight="8" '
        f'refX="6" refY="4" orient="auto" markerUnits="strokeWidth">'
        f'<path d="M0,0 L0,8 L8,4 z" fill="{color}"/>'
        f'</marker>'
    )


def _node_radius(label: str) -> int:
    return max(28, min(38, 10 + len(label) * 3))


def _svg_edge_curve(
    x1: float, y1: float,
    x2: float, y2: float,
    r1: int, r2: int,
    tx_number: int,
    color: str,
    marker_id: str,
    curvature: float = 0.0,   # 0 = прямая, >0 = кривая влево, <0 = вправо
) -> str:
    """
    Рисует квадратичную кривую Безье между двумя узлами.
    curvature задаёт насколько сильно и в какую сторону изогнута линия.
    """
    dx, dy = x2 - x1, y2 - y1
    dist = math.hypot(dx, dy) or 1
    ux, uy = dx / dist, dy / dist
    # перпендикуляр
    px, py = -uy, ux

    # Контрольная точка Безье — смещение перпендикулярно к середине
    mid_x = (x1 + x2) / 2 + px * curvature
    mid_y = (y1 + y2) / 2 + py * curvature

    # Начало и конец у границ узлов
    # Для кривой Безье направление в начале/конце определяется контрольной точкой
    # Находим направление от start к control point и от control к end
    def border_point(ox, oy, tx, ty, r):
        ddx, ddy = tx - ox, ty - oy
        d = math.hypot(ddx, ddy) or 1
        return ox + ddx / d * r, oy + ddy / d * r

    sx, sy = border_point(x1, y1, mid_x, mid_y, r1)
    ex, ey = border_point(x2, y2, mid_x, mid_y, r2)

    # Середина кривой для бейджика (параметр t=0.5 квадратичного Безье)
    bx = 0.25 * x1 + 0.5 * mid_x + 0.25 * x2
    by = 0.25 * y1 + 0.5 * mid_y + 0.25 * y2
    # Немного смещаем бейджик чтобы не лежал прямо на линии
    badge_off = 12 if curvature >= 0 else -12
    bx += px * badge_off * 0.3
    by += py * badge_off * 0.3

    path = (
        f'<path d="M{sx:.1f},{sy:.1f} Q{mid_x:.1f},{mid_y:.1f} {ex:.1f},{ey:.1f}" '
        f'fill="none" stroke="{color}" stroke-width="2.5" opacity="0.85" '
        f'marker-end="url(#{marker_id})"/>'
    )
    badge = (
        f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="11" '
        f'fill="white" stroke="{color}" stroke-width="1.5" opacity="0.97"/>'
    )
    num_label = (
        f'<text x="{bx:.1f}" y="{by + 4:.1f}" '
        f'text-anchor="middle" font-size="9" font-weight="800" fill="{color}" '
        f'font-family="inherit">{tx_number}</text>'
    )
    return path + '\n' + badge + '\n' + num_label


def _svg_node(
    x: float, y: float, r: int,
    label: str,
    fill: str, stroke: str, text_color: str,
    is_start: bool = False,
) -> str:
    circle = (
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="2.5"/>'
    )
    if len(label) > 6:
        top, bot = label[:6], label[6:]
        texts = (
            f'<text x="{x:.1f}" y="{y - 5:.1f}" text-anchor="middle" '
            f'font-size="9" font-weight="800" fill="{text_color}" '
            f'font-family="inherit">{top}</text>'
            f'<text x="{x:.1f}" y="{y + 7:.1f}" text-anchor="middle" '
            f'font-size="9" font-weight="800" fill="{text_color}" '
            f'font-family="inherit">{bot}</text>'
        )
    else:
        dy = -3 if is_start else 4
        sub = (
            f'<text x="{x:.1f}" y="{y + 14:.1f}" text-anchor="middle" '
            f'font-size="7" fill="{stroke}" font-family="inherit">исток</text>'
        ) if is_start else ''
        texts = (
            f'<text x="{x:.1f}" y="{y + dy:.1f}" text-anchor="middle" '
            f'font-size="9.5" font-weight="800" fill="{text_color}" '
            f'font-family="inherit">{label}</text>'
        ) + sub
    return circle + '\n' + texts


# ---------------------------------------------------------------------------
# Легенда и заглушка
# ---------------------------------------------------------------------------
def _svg_legend(width: int, height: int) -> str:
    lw, lh = 200, 60
    lx = width - lw - 12
    ly = height - lh - 12
    return (
        f'<rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" rx="8" '
        f'fill="white" stroke="{COLOR_GRID}" stroke-width="1.5" opacity="0.95"/>'
        f'<line x1="{lx+12}" y1="{ly+18}" x2="{lx+38}" y2="{ly+18}" '
        f'stroke="{COLOR_SUS_EDGE}" stroke-width="2.5"/>'
        f'<text x="{lx+44}" y="{ly+22}" font-size="9.5" fill="#475569" '
        f'font-weight="600" font-family="inherit">⚠ Подозрительная цепочка</text>'
        f'<line x1="{lx+12}" y1="{ly+40}" x2="{lx+38}" y2="{ly+40}" '
        f'stroke="{COLOR_NORM_EDGE}" stroke-width="2"/>'
        f'<text x="{lx+44}" y="{ly+44}" font-size="9.5" fill="#475569" '
        f'font-weight="600" font-family="inherit">✓ Обычный перевод</text>'
    )


def _empty_svg(width: int, height: int) -> str:
    return (
        f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'style="width:100%;height:100%;display:block;">'
        f'<rect width="{width}" height="{height}" fill="{COLOR_BG}" rx="14"/>'
        f'<text x="{width//2}" y="{height//2}" text-anchor="middle" '
        f'font-size="14" fill="#94a3b8" font-weight="600" font-family="inherit">'
        f'Нет данных для отображения</text>'
        f'</svg>'
    )


# ---------------------------------------------------------------------------
# Основная функция: только SVG
# ---------------------------------------------------------------------------
def render_graph_svg(
    transactions: list[dict],
    suspicious_paths: list[dict] | None = None,
    width: int = 720,
    height: int = 520,
) -> str:

    if not transactions:
        return _empty_svg(width, height)

    sus_nodes: set[str] = set()
    sus_edges: set[tuple] = set()

    if suspicious_paths:
        for p in suspicious_paths:
            if p.get('is_suspicious'):
                for node in p['nodes']:
                    sus_nodes.add(node)
                for e in p['edges']:
                    sus_edges.add((e['sender'], e['receiver']))

    all_nodes_set: set[str] = set()
    for tx in transactions:
        all_nodes_set.add(tx['sender'])
        all_nodes_set.add(tx['receiver'])

    all_nodes = sorted(all_nodes_set)

    receivers = {tx['receiver'] for tx in transactions}
    sources   = {tx['sender']   for tx in transactions} - receivers

    pos   = _circular_layout(all_nodes, sources, sus_nodes, width, height)
    radii = {node: _node_radius(node) for node in all_nodes}

    defs = (
        '<defs>'
        + _svg_marker('arr-sus',  COLOR_SUS_EDGE)
        + _svg_marker('arr-norm', COLOR_NORM_EDGE)
        + '</defs>'
    )

    # Считаем количество рёбер между каждой парой для правильного curvature
    pair_count: dict[tuple, int] = {}
    pair_index: dict[tuple, int] = {}
    for tx in transactions:
        key = (tx['sender'], tx['receiver'])
        pair_count[key] = pair_count.get(key, 0) + 1

    # Базовая кривизна зависит от расстояния между узлами
    # Чем ближе — тем сильнее кривая (иначе бейджик залезет на узел)
    CURVE_BASE = 40  # пикселей

    edges_svg = []
    nodes_svg = []

    for i, tx in enumerate(transactions):
        s, r = tx['sender'], tx['receiver']
        if s not in pos or r not in pos:
            continue
        x1, y1 = pos[s]
        x2, y2 = pos[r]

        is_sus    = (s, r) in sus_edges
        color     = COLOR_SUS_EDGE  if is_sus else COLOR_NORM_EDGE
        marker_id = 'arr-sus'       if is_sus else 'arr-norm'

        key = (s, r)
        idx = pair_index.get(key, 0)
        pair_index[key] = idx + 1
        total = pair_count[key]

        # Распределяем кривизну симметрично: [-curve, 0, +curve] и т.д.
        # Для одного ребра — небольшой изгиб чтобы не сливалось с обратным
        if total == 1:
            # Проверяем нет ли обратного ребра — тогда изгибаем
            has_reverse = (r, s) in pair_count
            curvature = CURVE_BASE * 0.6 if has_reverse else 0.0
        else:
            step = CURVE_BASE * 1.2
            curvature = (idx - (total - 1) / 2) * step

        edges_svg.append(
            _svg_edge_curve(
                x1, y1, x2, y2,
                radii[s], radii[r],
                i + 1,
                color, marker_id,
                curvature=curvature,
            )
        )

    for node in all_nodes:
        if node not in pos:
            continue
        x, y     = pos[node]
        r        = radii[node]
        is_start = node in sources
        is_sus   = node in sus_nodes

        if is_sus:
            fill, stroke, text_c = COLOR_SUS_FILL, COLOR_SUS_STROKE, COLOR_SUS_TEXT
        elif is_start:
            fill, stroke, text_c = COLOR_START_FILL, COLOR_START_FILL, COLOR_START_TEXT
        else:
            fill, stroke, text_c = COLOR_NORM_FILL, COLOR_NORM_STROKE, COLOR_NORM_TEXT

        nodes_svg.append(
            _svg_node(x, y, r, node, fill, stroke, text_c, is_start=is_start)
        )

    legend = _svg_legend(width, height)
    inner  = '\n'.join(edges_svg) + '\n' + '\n'.join(nodes_svg) + '\n' + legend

    svg = (
        f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'style="width:100%;height:100%;display:block;" overflow="visible">'
        f'{defs}'
        f'<rect width="{width}" height="{height}" fill="{COLOR_BG}" rx="14"/>'
        f'<g id="dfs-scene">'
        f'{inner}'
        f'</g>'
        f'</svg>'
    )
    return svg


# ---------------------------------------------------------------------------
# JS pan/zoom (без изменений)
# ---------------------------------------------------------------------------
_JS = """
<script>
(function() {
  var wrap  = document.getElementById('DFS_WRAP_ID');
  var scene = document.getElementById('dfs-scene');
  var lbl   = document.getElementById('DFS_LBL_ID');
  if (!wrap || !scene) return;

  var SVG_W = DFS_SVG_W, SVG_H = DFS_SVG_H;
  var MIN_SCALE = 0.2, MAX_SCALE = 5;
  var scale = 1, tx = 0, ty = 0;
  var dragging = false, startX = 0, startY = 0, startTx = 0, startTy = 0;

  function apply() {
    scene.setAttribute('transform',
      'translate(' + tx + ',' + ty + ') scale(' + scale + ')');
    if (lbl) lbl.textContent = Math.round(scale * 100) + '%';
  }
  function clamp() {
    var W = wrap.clientWidth  || SVG_W;
    var H = wrap.clientHeight || SVG_H;
    var gw = SVG_W * scale, gh = SVG_H * scale;
    var margin = 80;
    tx = Math.min(margin, Math.max(W - gw - margin, tx));
    ty = Math.min(margin, Math.max(H - gh - margin, ty));
  }
  wrap.addEventListener('mousedown', function(e) {
    if (e.button !== 0) return;
    dragging = true;
    startX = e.clientX; startY = e.clientY;
    startTx = tx; startTy = ty;
    e.preventDefault();
  });
  window.addEventListener('mousemove', function(e) {
    if (!dragging) return;
    tx = startTx + (e.clientX - startX);
    ty = startTy + (e.clientY - startY);
    clamp(); apply();
  });
  window.addEventListener('mouseup', function() { dragging = false; });
  wrap.addEventListener('wheel', function(e) {
    e.preventDefault();
    var rect  = wrap.getBoundingClientRect();
    var mx    = e.clientX - rect.left;
    var my    = e.clientY - rect.top;
    var delta = e.deltaY < 0 ? 1.12 : 1 / 1.12;
    var ns    = Math.min(MAX_SCALE, Math.max(MIN_SCALE, scale * delta));
    tx = mx - (mx - tx) * (ns / scale);
    ty = my - (my - ty) * (ns / scale);
    scale = ns; clamp(); apply();
  }, { passive: false });
  wrap.addEventListener('dblclick', function() {
    scale = 1; tx = 0; ty = 0; apply();
  });
  function zoomBtn(dir) {
    var W = wrap.clientWidth || SVG_W, H = wrap.clientHeight || SVG_H;
    var cx = W/2, cy = H/2;
    var d = dir > 0 ? 1.25 : 1/1.25;
    var ns = Math.min(MAX_SCALE, Math.max(MIN_SCALE, scale * d));
    tx = cx - (cx - tx) * (ns/scale);
    ty = cy - (cy - ty) * (ns/scale);
    scale = ns; clamp(); apply();
  }
  var btnIn  = document.getElementById('DFS_BTN_IN_ID');
  var btnOut = document.getElementById('DFS_BTN_OUT_ID');
  var btnRst = document.getElementById('DFS_BTN_RST_ID');
  if (btnIn)  btnIn.onclick  = function() { zoomBtn(1); };
  if (btnOut) btnOut.onclick = function() { zoomBtn(-1); };
  if (btnRst) btnRst.onclick = function() { scale=1; tx=0; ty=0; apply(); };
  var tStartX=0,tStartY=0,tStartTx=0,tStartTy=0;
  var pinchDist=0,pinchTx=0,pinchTy=0,pinchScale=1;
  wrap.addEventListener('touchstart', function(e) {
    e.preventDefault();
    if (e.touches.length===1) {
      dragging=true;
      tStartX=e.touches[0].clientX; tStartY=e.touches[0].clientY;
      tStartTx=tx; tStartTy=ty;
    } else if (e.touches.length===2) {
      dragging=false;
      pinchDist=Math.hypot(e.touches[0].clientX-e.touches[1].clientX,
                           e.touches[0].clientY-e.touches[1].clientY);
      pinchTx=tx; pinchTy=ty; pinchScale=scale;
    }
  }, {passive:false});
  wrap.addEventListener('touchmove', function(e) {
    e.preventDefault();
    if (e.touches.length===1 && dragging) {
      tx=tStartTx+(e.touches[0].clientX-tStartX);
      ty=tStartTy+(e.touches[0].clientY-tStartY);
      clamp(); apply();
    } else if (e.touches.length===2) {
      var dist=Math.hypot(e.touches[0].clientX-e.touches[1].clientX,
                          e.touches[0].clientY-e.touches[1].clientY);
      var ns=Math.min(MAX_SCALE,Math.max(MIN_SCALE,pinchScale*dist/pinchDist));
      var rect=wrap.getBoundingClientRect();
      var cx=(e.touches[0].clientX+e.touches[1].clientX)/2-rect.left;
      var cy=(e.touches[0].clientY+e.touches[1].clientY)/2-rect.top;
      tx=cx-(cx-pinchTx)*(ns/pinchScale);
      ty=cy-(cy-pinchTy)*(ns/pinchScale);
      scale=ns; clamp(); apply();
    }
  }, {passive:false});
  wrap.addEventListener('touchend', function() { dragging=false; });
  apply();
})();
</script>
"""


def render_graph_html(
    transactions: list[dict],
    suspicious_paths: list[dict] | None = None,
    width: int = 720,
    height: int = 520,
    container_height: int = 540,
) -> str:
    import hashlib, os
    uid = hashlib.md5(os.urandom(8)).hexdigest()[:6]

    wrap_id = f'dfs-wrap-{uid}'
    lbl_id  = f'dfs-lbl-{uid}'
    btn_in  = f'dfs-in-{uid}'
    btn_out = f'dfs-out-{uid}'
    btn_rst = f'dfs-rst-{uid}'

    svg = render_graph_svg(transactions, suspicious_paths, width, height)

    controls = (
        f'<div class="dfs-controls">'
        f'<button class="dfs-ctrl-btn" id="{btn_in}"  title="Увеличить">+</button>'
        f'<div    class="dfs-zoom-lbl" id="{lbl_id}">100%</div>'
        f'<button class="dfs-ctrl-btn" id="{btn_out}" title="Уменьшить">&#8722;</button>'
        f'<button class="dfs-ctrl-btn" id="{btn_rst}" title="Сбросить" style="font-size:13px">&#8962;</button>'
        f'</div>'
    )
    hint = '<span class="dfs-hint">Тащи · колёсико — зум · двойной клик — сброс</span>'

    js = (
        _JS
        .replace('DFS_WRAP_ID',    wrap_id)
        .replace('DFS_LBL_ID',     lbl_id)
        .replace('DFS_BTN_IN_ID',  btn_in)
        .replace('DFS_BTN_OUT_ID', btn_out)
        .replace('DFS_BTN_RST_ID', btn_rst)
        .replace('DFS_SVG_W',      str(width))
        .replace('DFS_SVG_H',      str(height))
    )

    return (
        f'<div class="dfs-graph-wrap" id="{wrap_id}" '
        f'style="height:{container_height}px;">'
        + svg + controls + hint + '</div>' + js
    )