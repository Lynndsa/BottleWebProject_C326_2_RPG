
import math

# Вычисление координат вершин

def _layout_nodes(
    nodes: list[str],
    suspicious_nodes: set[str],
    width: int,
    height: int,
    padding: int = 60,
) -> dict[str, tuple[float, float]]:
    n = len(nodes)
    pos: dict[str, tuple[float, float]] = {}
    if n == 0:
        return pos

    sus  = [v for v in nodes if v in suspicious_nodes]
    norm = [v for v in nodes if v not in suspicious_nodes]

    w = width  - 2 * padding
    h = height - 2 * padding

    if n <= 16:
        def row_x(items, y, row_w, row_padding):
            if not items:
                return
            step = row_w / max(len(items), 1)
            for i, node in enumerate(items):
                x = row_padding + step * i + step / 2
                pos[node] = (x, y)

        if sus and norm:
            row_x(sus,  padding + h * 0.25, width, padding)
            row_x(norm, padding + h * 0.72, width, padding)
        elif sus:
            row_x(sus, height / 2, width, padding)
        else:
            row_x(norm, height / 2, width, padding)
    else:
        cols = math.ceil(math.sqrt(n))
        rows = math.ceil(n / cols)
        for idx, node in enumerate(sus + norm):
            col = idx % cols
            row = idx // cols
            x = padding + col * (w / max(cols - 1, 1))
            y = padding + row * (h / max(rows - 1, 1))
            pos[node] = (x, y)

    return pos

# SVG-примитивы

def _svg_marker(marker_id: str, color: str) -> str:
    return (
        f'<marker id="{marker_id}" markerWidth="9" markerHeight="9" '
        f'refX="7" refY="3" orient="auto">'
        f'<path d="M0,0 L0,6 L9,3 z" fill="{color}"/>'
        f'</marker>'
    )


def _node_radius(label: str) -> int:
    return max(28, min(36, 10 + len(label) * 3))


def _svg_edge(
    x1: float, y1: float,
    x2: float, y2: float,
    r1: int, r2: int,
    label: str,
    color: str,
    marker_id: str,
) -> str:
    dx, dy = x2 - x1, y2 - y1
    dist = math.hypot(dx, dy) or 1
    ux, uy = dx / dist, dy / dist

    sx, sy = x1 + ux * r1, y1 + uy * r1
    ex, ey = x2 - ux * r2, y2 - uy * r2

    mx, my = (sx + ex) / 2, (sy + ey) / 2
    px, py = -uy * 12, ux * 12

    line = (
        f'<line x1="{sx:.1f}" y1="{sy:.1f}" x2="{ex:.1f}" y2="{ey:.1f}" '
        f'stroke="{color}" stroke-width="2.2" '
        f'marker-end="url(#{marker_id})"/>'
    )
    text = (
        f'<text x="{mx + px:.1f}" y="{my + py:.1f}" '
        f'text-anchor="middle" font-size="9" font-weight="700" fill="{color}" '
        f'font-family="Courier New, monospace">{_fmt_amount(label)}</text>'
    )
    return line + '\n' + text


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
        t1 = (
            f'<text x="{x:.1f}" y="{y - 5:.1f}" text-anchor="middle" '
            f'font-size="9" font-weight="800" fill="{text_color}" '
            f'font-family="inherit">{top}</text>'
        )
        t2 = (
            f'<text x="{x:.1f}" y="{y + 7:.1f}" text-anchor="middle" '
            f'font-size="9" font-weight="800" fill="{text_color}" '
            f'font-family="inherit">{bot}</text>'
        )
        texts = t1 + t2
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


def _fmt_amount(val) -> str:
    try:
        f = float(val)
        if f >= 1_000_000:
            return f'{f / 1_000_000:.1f}M'
        if f >= 1_000:
            return f'{f / 1_000:.1f}k'
        return f'{f:.0f}'
    except Exception:
        return str(val)

# Легенда и заглушка

def _svg_legend(width: int, height: int) -> str:
    lw, lh = 190, 60
    lx = width - lw - 12
    ly = height - lh - 12
    return (
        f'<rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" rx="8" '
        f'fill="white" stroke="{COLOR_GRID}" stroke-width="1.5" opacity="0.92"/>'
        f'<line x1="{lx+12}" y1="{ly+18}" x2="{lx+36}" y2="{ly+18}" '
        f'stroke="{COLOR_SUS_EDGE}" stroke-width="2.5"/>'
        f'<text x="{lx+42}" y="{ly+22}" font-size="9.5" fill="#475569" '
        f'font-weight="600" font-family="inherit">⚠ Подозрительная цепочка</text>'
        f'<line x1="{lx+12}" y1="{ly+40}" x2="{lx+36}" y2="{ly+40}" '
        f'stroke="{COLOR_NORM_EDGE}" stroke-width="2"/>'
        f'<text x="{lx+42}" y="{ly+44}" font-size="9.5" fill="#475569" '
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

# Основная функция: только SVG

def render_graph_svg(
    transactions: list[dict],
    suspicious_paths: list[dict] | None = None,
    width: int = 680,
    height: int = 460,
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

    receivers = {tx['receiver'] for tx in transactions}
    sources   = {tx['sender'] for tx in transactions} - receivers
    ordered   = sorted(sources) + sorted(all_nodes_set - sources)

    pos    = _layout_nodes(ordered, sus_nodes, width, height)
    radii  = {node: _node_radius(node) for node in ordered}

    defs = (
        '<defs>'
        + _svg_marker('arr-sus',  COLOR_SUS_EDGE)
        + _svg_marker('arr-norm', COLOR_NORM_EDGE)
        + '</defs>'
    )

    edges_svg = []
    nodes_svg = []

    for tx in transactions:
        s, r = tx['sender'], tx['receiver']
        if s not in pos or r not in pos:
            continue
        x1, y1 = pos[s]
        x2, y2 = pos[r]
        is_sus    = (s, r) in sus_edges
        color     = COLOR_SUS_EDGE  if is_sus else COLOR_NORM_EDGE
        marker_id = 'arr-sus'       if is_sus else 'arr-norm'
        edges_svg.append(
            _svg_edge(x1, y1, x2, y2, radii[s], radii[r],
                      str(tx['amount']), color, marker_id)
        )

    for node in ordered:
        if node not in pos:
            continue
        x, y   = pos[node]
        r      = radii[node]
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

    # Весь контент оборачиваем в <g id="scene"> — JS будет двигать именно его
    svg = (
        f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'style="width:100%;height:100%;display:block;">'
        f'{defs}'
        f'<rect width="{width}" height="{height}" fill="{COLOR_BG}" rx="14"/>'
        f'<g id="dfs-scene">'
        f'{inner}'
        f'</g>'
        f'</svg>'
    )
    return svg


# Обёртка: SVG + HTML-контейнер с pan/zoom
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

  /* ---- мышь ---- */
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

  /* ---- колёсико ---- */
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

  /* ---- двойной клик — сброс ---- */
  wrap.addEventListener('dblclick', function() {
    scale = 1; tx = 0; ty = 0; apply();
  });

  /* ---- кнопки ---- */
  function zoomBtn(dir) {
    var W  = wrap.clientWidth  || SVG_W;
    var H  = wrap.clientHeight || SVG_H;
    var cx = W / 2, cy = H / 2;
    var d  = dir > 0 ? 1.25 : 1 / 1.25;
    var ns = Math.min(MAX_SCALE, Math.max(MIN_SCALE, scale * d));
    tx = cx - (cx - tx) * (ns / scale);
    ty = cy - (cy - ty) * (ns / scale);
    scale = ns; clamp(); apply();
  }
  var btnIn    = document.getElementById('DFS_BTN_IN_ID');
  var btnOut   = document.getElementById('DFS_BTN_OUT_ID');
  var btnReset = document.getElementById('DFS_BTN_RST_ID');
  if (btnIn)    btnIn.onclick    = function() { zoomBtn(1); };
  if (btnOut)   btnOut.onclick   = function() { zoomBtn(-1); };
  if (btnReset) btnReset.onclick = function() { scale=1; tx=0; ty=0; apply(); };

  /* ---- пинч-зум (touch) ---- */
  var tStartX=0, tStartY=0, tStartTx=0, tStartTy=0;
  var pinchDist=0, pinchTx=0, pinchTy=0, pinchScale=1;

  wrap.addEventListener('touchstart', function(e) {
    e.preventDefault();
    if (e.touches.length === 1) {
      dragging = true;
      tStartX = e.touches[0].clientX; tStartY = e.touches[0].clientY;
      tStartTx = tx; tStartTy = ty;
    } else if (e.touches.length === 2) {
      dragging = false;
      pinchDist   = Math.hypot(
        e.touches[0].clientX - e.touches[1].clientX,
        e.touches[0].clientY - e.touches[1].clientY);
      pinchTx = tx; pinchTy = ty; pinchScale = scale;
    }
  }, { passive: false });

  wrap.addEventListener('touchmove', function(e) {
    e.preventDefault();
    if (e.touches.length === 1 && dragging) {
      tx = tStartTx + (e.touches[0].clientX - tStartX);
      ty = tStartTy + (e.touches[0].clientY - tStartY);
      clamp(); apply();
    } else if (e.touches.length === 2) {
      var dist = Math.hypot(
        e.touches[0].clientX - e.touches[1].clientX,
        e.touches[0].clientY - e.touches[1].clientY);
      var ns = Math.min(MAX_SCALE, Math.max(MIN_SCALE,
        pinchScale * dist / pinchDist));
      var rect = wrap.getBoundingClientRect();
      var cx = (e.touches[0].clientX + e.touches[1].clientX) / 2 - rect.left;
      var cy = (e.touches[0].clientY + e.touches[1].clientY) / 2 - rect.top;
      tx = cx - (cx - pinchTx) * (ns / pinchScale);
      ty = cy - (cy - pinchTy) * (ns / pinchScale);
      scale = ns; clamp(); apply();
    }
  }, { passive: false });

  wrap.addEventListener('touchend', function() { dragging = false; });

  apply();
})();
</script>
"""


def render_graph_html(
    transactions: list[dict],
    suspicious_paths: list[dict] | None = None,
    width: int = 680,
    height: int = 460,
    container_height: int = 480,
) -> str:
    # Уникальные ID, чтобы несколько графов на одной странице не конфликтовали
    import hashlib, os
    uid = hashlib.md5(os.urandom(8)).hexdigest()[:6]

    wrap_id   = f'dfs-wrap-{uid}'
    lbl_id    = f'dfs-lbl-{uid}'
    btn_in    = f'dfs-in-{uid}'
    btn_out   = f'dfs-out-{uid}'
    btn_rst   = f'dfs-rst-{uid}'

    svg = render_graph_svg(transactions, suspicious_paths, width, height)

    controls = (
        f'<div class="dfs-controls">'
        f'<button class="dfs-ctrl-btn" id="{btn_in}"  title="Увеличить">+</button>'
        f'<div    class="dfs-zoom-lbl" id="{lbl_id}">100%</div>'
        f'<button class="dfs-ctrl-btn" id="{btn_out}" title="Уменьшить">&#8722;</button>'
        f'<button class="dfs-ctrl-btn" id="{btn_rst}" title="Сбросить"  style="font-size:13px">&#8962;</button>'
        f'</div>'
    )

    hint = '<span class="dfs-hint">Тащи · колёсико — зум · двойной клик — сброс</span>'

    js = (
        _JS
        .replace('DFS_WRAP_ID',   wrap_id)
        .replace('DFS_LBL_ID',    lbl_id)
        .replace('DFS_BTN_IN_ID', btn_in)
        .replace('DFS_BTN_OUT_ID',btn_out)
        .replace('DFS_BTN_RST_ID',btn_rst)
        .replace('DFS_SVG_W',     str(width))
        .replace('DFS_SVG_H',     str(height))
    )

    html = (
        f'<div class="dfs-graph-wrap" id="{wrap_id}" '
        f'style="height:{container_height}px;">'
        + svg
        + controls
        + hint
        + f'</div>'
        + js
    )
    return html

# Цветовая палитра

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