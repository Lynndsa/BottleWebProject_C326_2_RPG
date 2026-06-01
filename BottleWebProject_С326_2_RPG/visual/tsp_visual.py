import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import networkx as nx

def _build_fig(graph, best_path=None, full_path=None, hotel=None, unreachable=None):
    G = nx.Graph()
    for u, neighbors in graph.items():
        G.add_node(u)
        for v, w in neighbors.items():
            if not G.has_edge(u, v):
                G.add_edge(u, v, weight=w)
    if len(G.nodes) == 0:
        return None
    pos = nx.circular_layout(G)
    fig, ax = plt.subplots(figsize=(8, 6))
    fig.patch.set_facecolor('#f8fafc')
    ax.set_facecolor('#f8fafc')
    path_edge_set = set()
    draw_path = full_path if full_path else best_path
    if draw_path and len(draw_path) > 1:
        for i in range(len(draw_path) - 1):
            u, v = draw_path[i], draw_path[i + 1]
            path_edge_set.add((u, v))
            path_edge_set.add((v, u))
    normal_edges = []
    route_edges  = []
    for u, v in G.edges():
        if (u, v) in path_edge_set or (v, u) in path_edge_set:
            route_edges.append((u, v))
        else:
            normal_edges.append((u, v))
    nx.draw_networkx_edges(G, pos, ax=ax,
                           edgelist=normal_edges,
                           edge_color='#cbd5e1', width=1.2)
    if route_edges:
        nx.draw_networkx_edges(G, pos, ax=ax,
                               edgelist=route_edges,
                               edge_color='#0080cc', width=3.0)
    full_path_nodes = set(full_path) if full_path else set()
    key_nodes       = set(best_path[:-1]) if best_path else set()
    unreachable_set = set(unreachable) if unreachable else set()
    node_colors = []
    node_sizes  = []
    for node in G.nodes():
        if node == hotel:
            node_colors.append('#0f172a')
            node_sizes.append(700)
        elif node in unreachable_set:
            node_colors.append('#ef4444')
            node_sizes.append(500)
        elif node in key_nodes:
            node_colors.append('#0080cc')
            node_sizes.append(500)
        elif node in full_path_nodes:
            node_colors.append('#38bdf8')
            node_sizes.append(350)
        else:
            node_colors.append('#94a3b8')
            node_sizes.append(300)
    nx.draw_networkx_nodes(G, pos, ax=ax,
                           node_color=node_colors,
                           node_size=node_sizes)
    nx.draw_networkx_labels(G, pos, ax=ax,
                            font_color='white',
                            font_size=9, font_weight='bold')
    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels,
                                 ax=ax, font_size=8, font_color='#475569')
    if draw_path:
        path_str = ' → '.join(str(n) for n in draw_path)
        if len(path_str) > 60:
            path_str = path_str[:57] + '...'
        ax.set_title('Полный путь: ' + path_str, fontsize=10, color='#0f172a', pad=15)
    ax.axis('off')
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    return fig


def build_svg(graph, best_path=None, full_path=None, hotel=None, unreachable=None):
    fig = _build_fig(graph, best_path, full_path, hotel, unreachable)
    if fig is None:
        return ''
    buf = io.StringIO()
    fig.savefig(buf, format='svg', bbox_inches='tight',
                facecolor=fig.get_facecolor())
    plt.close(fig)
    svg_str = buf.getvalue()
    start = svg_str.find('<svg')
    return svg_str[start:] if start != -1 else svg_str