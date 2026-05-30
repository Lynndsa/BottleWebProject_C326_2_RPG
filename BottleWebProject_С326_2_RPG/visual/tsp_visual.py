
import io
import base64
import matplotlib
matplotlib.use('Agg')  # без GUI
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx


def build_svg(graph, best_path=None, hotel=None):
    """
    Строит SVG визуализацию графа.

    Параметры:
        graph     — словарь смежности {вершина: {сосед: вес}}
        best_path — список вершин оптимального маршрута ['1','3','2','1']
                    (если None — рисуем просто граф без маршрута)
        hotel     — строка-ключ вершины-отеля

    Возвращает:
        строку SVG для вставки в шаблон через {{!svg_html}}
    """
    G = nx.Graph()

    # Добавляем вершины и рёбра
    for u, neighbors in graph.items():
        G.add_node(u)
        for v, w in neighbors.items():
            if not G.has_edge(u, v):
                G.add_edge(u, v, weight=w)

    if len(G.nodes) == 0:
        return ''

    # Определяем рёбра маршрута
    path_edges = set()
    if best_path and len(best_path) > 1:
        for i in range(len(best_path) - 1):
            u, v = best_path[i], best_path[i + 1]
            path_edges.add((min(u, v), max(u, v)))

    # Layout
    pos = nx.spring_layout(G, seed=42, k=2.5)

    fig, ax = plt.subplots(figsize=(8, 6))
    fig.patch.set_facecolor('#f8fafc')
    ax.set_facecolor('#f8fafc')

    # Цвета рёбер
    edge_colors = []
    edge_widths = []
    for u, v in G.edges():
        key = (min(u, v), max(u, v))
        if key in path_edges:
            edge_colors.append('#0080cc')
            edge_widths.append(3.0)
        else:
            edge_colors.append('#cbd5e1')
            edge_widths.append(1.2)

    nx.draw_networkx_edges(G, pos, ax=ax,
                           edge_color=edge_colors,
                           width=edge_widths)

    # Веса рёбер
    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels,
                                 ax=ax, font_size=8, font_color='#475569')

    # Цвета вершин
    node_colors = []
    node_sizes  = []
    for node in G.nodes():
        if node == hotel:
            node_colors.append('#0f172a')  # отель — тёмный
            node_sizes.append(600)
        elif best_path and node in best_path:
            node_colors.append('#0080cc')  # в маршруте — синий
            node_sizes.append(500)
        else:
            node_colors.append('#94a3b8')  # остальные — серый
            node_sizes.append(400)

    nx.draw_networkx_nodes(G, pos, ax=ax,
                           node_color=node_colors,
                           node_size=node_sizes)

    nx.draw_networkx_labels(G, pos, ax=ax,
                            font_color='white',
                            font_size=9,
                            font_weight='bold')

    # Легенда
    legend = []
    if hotel:
        legend.append(mpatches.Patch(color='#0f172a', label=f'Отель ({hotel})'))
    if best_path:
        legend.append(mpatches.Patch(color='#0080cc', label='Маршрут'))
    legend.append(mpatches.Patch(color='#94a3b8', label='Остальные вершины'))
    if legend:
        ax.legend(handles=legend, loc='upper left', fontsize=8,
                  framealpha=0.8, facecolor='white')

    # Заголовок
    if best_path:
        ax.set_title(' → '.join(best_path), fontsize=10,
                     color='#0f172a', pad=10)

    ax.axis('off')
    plt.tight_layout()

    # Сохраняем в SVG строку
    buf = io.StringIO()
    fig.savefig(buf, format='svg', bbox_inches='tight',
                facecolor=fig.get_facecolor())
    plt.close(fig)

    svg_str = buf.getvalue()
    # Вырезаем только тег <svg>...</svg>
    start = svg_str.find('<svg')
    if start != -1:
        svg_str = svg_str[start:]

    return svg_str