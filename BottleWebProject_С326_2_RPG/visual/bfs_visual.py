import networkx as nx
import matplotlib
matplotlib.use('Agg')  # Важно для работы без GUI
import matplotlib.pyplot as plt
import io
import base64

def create_graph_from_edges(n_nodes, edges):
    """Создает граф из списка ребер"""
    G = nx.Graph()
    
    # Добавляем все узлы
    for i in range(1, n_nodes + 1):
        G.add_node(i)
    
    # Добавляем рёбра
    for u, v in edges:
        if u != v:
            G.add_edge(u, v)
    
    return G

def generate_graph_svg(graph, initial_infected=None, infection_frequency=None):
    """Генерирует SVG графа"""
    if graph.number_of_nodes() == 0:
        return '<svg width="400" height="300"><text x="200" y="150" text-anchor="middle">Нет данных для отображения</text></svg>'
    
    plt.figure(figsize=(12, 8))
    
    # Позиционирование узлов
    try:
        pos = nx.spring_layout(graph, k=2, iterations=50, seed=42)
    except:
        pos = nx.circular_layout(graph)
    
    # Цвета узлов
    node_colors = []
    initial_set = set(initial_infected) if initial_infected else set()
    
    for node in graph.nodes():
        if node in initial_set:
            node_colors.append('#dc2626')  # Красный - очаг
        elif infection_frequency and node in infection_frequency:
            freq = infection_frequency[node]
            if freq > 0.7:
                node_colors.append('#dc2626')  # Тёмно-красный
            elif freq > 0.4:
                node_colors.append('#f97316')  # Оранжевый
            elif freq > 0.1:
                node_colors.append('#fbbf24')  # Жёлтый
            else:
                node_colors.append('#e5e7eb')  # Серый
        else:
            node_colors.append('#e5e7eb')
    
    # Рисуем граф
    nx.draw_networkx_nodes(graph, pos, node_color=node_colors, node_size=400, alpha=0.9, edgecolors='#4b5563', linewidths=1.5)
    nx.draw_networkx_edges(graph, pos, width=1.5, alpha=0.5, edge_color='#9ca3af')
    nx.draw_networkx_labels(graph, pos, font_size=10, font_weight='bold', font_color='#1f2937')
    
    plt.title("Структура сети. Красный — начальный очаг, Жёлтый→Оранжевый — частота заражения", fontsize=12, pad=15)
    plt.axis('off')
    plt.tight_layout()
    
    # Сохраняем в SVG
    buf = io.BytesIO()
    plt.savefig(buf, format='svg', bbox_inches='tight', facecolor='white')
    buf.seek(0)
    svg_string = buf.getvalue().decode('utf-8')
    plt.close()
    
    return svg_string

def generate_infection_chart(progression_data):
    """Генерирует график динамики заражения"""
    if not progression_data:
        return None
    
    plt.figure(figsize=(10, 5))
    
    steps = list(range(len(progression_data)))
    plt.plot(steps, progression_data, marker='o', linewidth=2, markersize=4, color='#dc2626', label='Заражённые узлы')
    
    plt.xlabel('Шаг распространения (уровень BFS)', fontsize=11)
    plt.ylabel('Количество заражённых узлов', fontsize=11)
    plt.title('Динамика распространения инфекции (усреднённая)', fontsize=12, fontweight='bold')
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.legend(loc='lower right')
    
    if progression_data:
        final_value = progression_data[-1]
        plt.annotate(f'Итог: {final_value:.1f}', 
                    xy=(steps[-1], final_value),
                    xytext=(-40, -15),
                    textcoords='offset points',
                    fontsize=9,
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='#fef08a', alpha=0.8))
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()
    
    return img_base64