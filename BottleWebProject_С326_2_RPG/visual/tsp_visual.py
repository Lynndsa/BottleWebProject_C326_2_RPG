import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx


def _build_fig(graph, best_path=None, full_path=None, hotel=None,
               unreachable=None, total_dist=None, impossible=False):

    # Инициализация графа NetworkX
    G = nx.Graph()
    for u, neighbors in graph.items():
        G.add_node(u)
        for v, w in neighbors.items():
            if not G.has_edge(u, v):
                G.add_edge(u, v, weight=w)

    if len(G.nodes) == 0:
        return None

    # Расположение вершин по кругу
    pos = nx.circular_layout(G)

    # Настройка холста
    fig, ax = plt.subplots(figsize=(10, 7))
    fig.patch.set_facecolor('#f8fafc')
    ax.set_facecolor('#f8fafc')

    # Определение рёбер, входящих в маршрут
    path_edge_set = set()
    draw_path = full_path if full_path else best_path
    if draw_path and len(draw_path) > 1:
        for i in range(len(draw_path) - 1):
            u, v = draw_path[i], draw_path[i + 1]
            path_edge_set.add((u, v))
            path_edge_set.add((v, u))

    # Разделение рёбер на обычные и маршрутные
    normal_edges = []
    route_edges  = []
    for u, v in G.edges():
        if (u, v) in path_edge_set or (v, u) in path_edge_set:
            route_edges.append((u, v))
        else:
            normal_edges.append((u, v))

    # Отрисовка рёбер графа
    nx.draw_networkx_edges(G, pos, ax=ax, edgelist=normal_edges,
                           edge_color='#cbd5e1', width=1.2)
    if route_edges:
        nx.draw_networkx_edges(G, pos, ax=ax, edgelist=route_edges,
                               edge_color='#0080cc', width=3.0)

    # Категоризация вершин по ролям
    full_path_nodes = set(full_path)  if full_path    else set()
    key_nodes       = set(best_path[:-1]) if best_path else set()
    unreachable_set = set(unreachable) if unreachable  else set()

    # Стилизация вершин (цвет и размер) в зависимости от роли
    node_colors = []
    node_sizes  = []
    for node in G.nodes():
        if node == hotel:
            node_colors.append('#0f172a')  # Отель
            node_sizes.append(700)
        elif node in unreachable_set:
            node_colors.append('#ef4444')  # Недостижимая точка
            node_sizes.append(500)
        elif node in key_nodes:
            node_colors.append('#0080cc')  # Достопримечательность
            node_sizes.append(500)
        elif node in full_path_nodes:
            node_colors.append('#38bdf8')  # Промежуточная точка маршрута
            node_sizes.append(350)
        else:
            node_colors.append('#94a3b8')  # Неиспользуемая вершина
            node_sizes.append(300)

    # Отрисовка вершин и их номеров
    nx.draw_networkx_nodes(G, pos, ax=ax, node_color=node_colors, node_size=node_sizes)
    nx.draw_networkx_labels(G, pos, ax=ax, font_color='white', font_size=9, font_weight='bold')

    # Отрисовка весов (расстояний) на рёбрах
    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels,
                                 ax=ax, font_size=8, font_color='#475569')

    # Формирование заголовка и вывод предупреждения о невозможности маршрута
    if impossible:
        ax.set_title('Маршрут построить невозможно:\nнедостижимые вершины отмечены красным',
                     fontsize=11, color='#ef4444', pad=15, fontweight='bold')
    elif draw_path:
        path_str   = ' → '.join(str(n) for n in draw_path)
        title_text = f'Полный путь: {path_str}'
        if total_dist is not None:
            title_text += f' \n Длина маршрута: {total_dist} ед.'
        ax.set_title(title_text, fontsize=10, color='#0f172a', pad=15,
                     fontweight='bold', wrap=True)

    # Формирование элементов легенды
    legend_items = []
    if hotel:
        legend_items.append(mpatches.Patch(color='#0f172a', label=f'Отель (вершина {hotel})'))
    if key_nodes:
        legend_items.append(mpatches.Patch(color='#0080cc', label='Достопримечательности'))
    if full_path_nodes - key_nodes - ({hotel} if hotel else set()):
        legend_items.append(mpatches.Patch(color='#38bdf8', label='Промежуточные вершины маршрута'))
    if unreachable_set:
        legend_items.append(mpatches.Patch(color='#ef4444', label='Недостижимые вершины'))
        
    all_special = key_nodes | full_path_nodes | unreachable_set | ({hotel} if hotel else set())
    if any(n not in all_special for n in G.nodes()):
        legend_items.append(mpatches.Patch(color='#94a3b8', label='Остальные вершины'))

    # Отрисовка легенды
    if legend_items:
        ax.legend(handles=legend_items, loc='lower left', fontsize=8,
                  framealpha=0.9, facecolor='white', edgecolor='#e2e8f0')

    ax.axis('off')
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    return fig


def build_svg(graph, best_path=None, full_path=None, hotel=None,
              unreachable=None, total_dist=None):

    # Проверка условий невозможности построения маршрута
    impossible = bool(unreachable) and not best_path

    fig = _build_fig(graph, best_path, full_path, hotel,
                     unreachable, total_dist, impossible)
    if fig is None:
        return ''

    # Экспорт графика в буфер формата SVG
    buf = io.StringIO()
    fig.savefig(buf, format='svg', bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)

    # Очистка и кастомизация SVG-строки для фронтенда
    svg_str = buf.getvalue()
    start = svg_str.find('<svg')
    if start == -1:
        return ''

    svg_str = svg_str[start:]
    svg_str = svg_str.replace(
        '<svg ',
        '<svg id="tsp-svg" style="cursor:grab;width:100%;height:100%;" ',
        1
    )
    return svg_str