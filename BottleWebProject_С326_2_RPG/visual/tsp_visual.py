import io
import matplotlib
# Переключение Matplotlib в фоновый режим 'Agg' (без графического интерфейса), 
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import networkx as nx

def _build_fig(graph, best_path=None, full_path=None, hotel=None, unreachable=None):

    # Создаём пустой объект неориентированного графа в NetworkX
    G = nx.Graph()
    
    # Заполняем граф вершинами и рёбрами с весами из нашей структуры данных
    for u, neighbors in graph.items():
        G.add_node(u)
        for v, w in neighbors.items():
            if not G.has_edge(u, v):
                G.add_edge(u, v, weight=w)
                
    # Если граф пустой, рисовать нечего
    if len(G.nodes) == 0:
        return None
        
    # Задаём шаблон генерации координат: circular_layout расставляет все вершины по кругу
    pos = nx.circular_layout(G)
    
    # Создаём холст 
    fig, ax = plt.subplots(figsize=(8, 6))
    fig.patch.set_facecolor('#f8fafc')
    ax.set_facecolor('#f8fafc')
    
    # Собираем все рёбра, которые входят в итоговый маршрут
    path_edge_set = set()
    draw_path = full_path if full_path else best_path
    if draw_path and len(draw_path) > 1:
        for i in range(len(draw_path) - 1):
            u, v = draw_path[i], draw_path[i + 1]
            path_edge_set.add((u, v))
            path_edge_set.add((v, u))
            
    # Разделяем рёбра графа на две группы: обычные дороги и дороги из маршрута
    normal_edges = []
    route_edges  = []
    for u, v in G.edges():
        if (u, v) in path_edge_set or (v, u) in path_edge_set:
            # если оптимальный
            route_edges.append((u, v))
        else:
            #если не оптимальный
            normal_edges.append((u, v))
            
    # Рисуем обычные рёбра ( нейтрального серого цвета)
    nx.draw_networkx_edges(G, pos, ax=ax,
                           edgelist=normal_edges,
                           edge_color='#cbd5e1', width=1.2)
                           
    # Рисуем рёбра маршрута 
    if route_edges:
        nx.draw_networkx_edges(G, pos, ax=ax,
                               edgelist=route_edges,
                               edge_color='#0080cc', width=3.0)
                               
    # Подготавливаем множества вершин для удобной проверки их статуса при раскраске
    # если ничего нет, то вернем пустоем множество
    full_path_nodes = set(full_path) if full_path else set()
    key_nodes       = set(best_path[:-1]) if best_path else set()
    unreachable_set = set(unreachable) if unreachable else set()
    
    node_colors = []
    node_sizes  = []
    
    # Логика цветовой схемы для вершин графа
    for node in G.nodes():
        if node == hotel:
            node_colors.append('#0f172a')  # Отель — тёмно-синий
            node_sizes.append(700)         # Большой круг
        elif node in unreachable_set:
            node_colors.append('#ef4444')  # Недостижимые вершины — ярко-красный 
            node_sizes.append(500)
        elif node in key_nodes:
            node_colors.append('#0080cc')  # Ключевые точки — насыщенный синий
            node_sizes.append(500)
        elif node in full_path_nodes:
            node_colors.append('#38bdf8')  # Промежуточные вершины маршрута — нежно-голубой
            node_sizes.append(350)
        else:
            node_colors.append('#94a3b8')  # Обычные, не задействованные вершины — нейтральный серый
            node_sizes.append(300)
            
    # Рисуем кружки вершин с подготовленными цветами и размерами
    nx.draw_networkx_nodes(G, pos, ax=ax,
                           node_color=node_colors,
                           node_size=node_sizes)
                           
    # Рисуем номера вершин 
    nx.draw_networkx_labels(G, pos, ax=ax,
                            font_color='white',
                            font_size=9, font_weight='bold')
                            
    # Считываем веса рёбер и рисуем их (цену дорог) 
    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels,
                                 ax=ax, font_size=8, font_color='#475569')
                                 
    # Если путь существует, генерируем для графика заголовок с цепочкой обхода
    if draw_path:
        path_str = ' → '.join(str(n) for n in draw_path)
        if len(path_str) > 60:
            path_str = path_str[:57] + '...'
        ax.set_title('Полный путь: ' + path_str, fontsize=10, color='#0f172a', pad=15)
        
    # Прячем оси координат 
    ax.axis('off')
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    return fig

# Принимает данные графа, генерирует картинку и конвертирует её в чистую SVG-строку
def build_svg(graph, best_path=None, full_path=None, hotel=None, unreachable=None):

    # Строим фигуру 
    fig = _build_fig(graph, best_path, full_path, hotel, unreachable)
    if fig is None:
        return ''
        
    # Создаём строковый буфер в памяти, куда Matplotlib запишет векторные данные
    buf = io.StringIO()
    fig.savefig(buf, format='svg', bbox_inches='tight',
                facecolor=fig.get_facecolor())
    plt.close(fig)  
    
    svg_str = buf.getvalue()
    
    # Находим картинку среди мусора
    start = svg_str.find('<svg')
    if start == -1:
        return ''
    # Обрезаем мусор
    svg_str = svg_str[start:]
    # Добавляем стили
    svg_str = svg_str.replace('<svg ', '<svg id="tsp-svg" style="cursor:grab;width:100%;height:100%;" ', 1)
    
    return svg_str