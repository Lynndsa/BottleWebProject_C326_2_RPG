import networkx as nx
import matplotlib.pyplot as plt
import io
import base64

def create_graph_from_edges(edges, n_nodes):
    """Создает граф из списка ребер с гарантированным добавлением всех узлов"""
    G = nx.Graph()
    
    # Добавляем все узлы от 1 до n_nodes
    for i in range(1, n_nodes + 1):
        G.add_node(i)
    
    # Добавляем ребра с валидацией данных
    for u, v in edges:
        if u is not None and v is not None:
            G.add_edge(int(u), int(v))
    
    return G

def generate_graph_svg(graph, infection_frequency=None, initial_infected=None):
    """Генерирует SVG представление графа с правильной цветовой палитрой"""
    # Фиксируем размер полотна
    plt.figure(figsize=(12, 8))
    
    # Использование семени (random_state) гарантирует одинаковое расположение узлов при перезапусках
    pos = nx.spring_layout(graph, k=1.0, iterations=50, seed=42)
    
    node_colors = []
    initial_set = set(initial_infected) if initial_infected else set()
    
    for node in graph.nodes():
        if node in initial_set:
            node_colors.append('#dc2626')  # Ярко-красный для нулевого пациента
        elif infection_frequency and node in infection_frequency:
            freq = infection_frequency[node]
            if freq > 0:
                # Масштабируем от 0.2 до 0.9 для лучшей читаемости градиента YlOrRd
                intensity = 0.2 + freq * 0.7
                node_colors.append(plt.cm.YlOrRd(intensity))
            else:
                node_colors.append('#e5e7eb')  # Серый для незараженных
        else:
            node_colors.append('#e5e7eb')
    
    # Отрисовка базовых элементов графа
    nx.draw_networkx_nodes(graph, pos, node_color=node_colors, node_size=500, alpha=0.95, edgecolors='#4b5563')
    nx.draw_networkx_edges(graph, pos, width=1.2, alpha=0.4, edge_color='#9ca3af')
    nx.draw_networkx_labels(graph, pos, font_size=10, font_weight='bold', font_color='#1f2937')
    
    plt.title("Структура сети. Красный — очаг, Желтый->Оранжевый — частота заражения", fontsize=14, pad=15)
    plt.axis('off')
    
    # Экспорт в SVG строку
    buf = io.BytesIO()
    plt.savefig(buf, format='svg', bbox_inches='tight')
    buf.seek(0)
    svg_string = buf.getvalue().decode('utf-8')
    plt.close()
    
    return svg_string

def generate_infection_chart(progression_data):
    """Генерирует график динамики заражения (возвращает base64 PNG)"""
    if not progression_data:
        return None
    
    plt.figure(figsize=(10, 5))
    
    steps = list(range(len(progression_data)))
    plt.plot(steps, progression_data, marker='o', linewidth=2.5, markersize=5, 
             color='#dc2626', label='Среднее кол-во зараженных')
    
    plt.xlabel('Шаг времени (итерация BFS)')
    plt.ylabel('Количество зараженных узлов')
    plt.title('Эпидемиологическая динамика (Модель SI)')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend(loc='upper left')
    
    # Корректное отображение финальной метки
    final_value = progression_data[-1]
    plt.annotate(f'Итог: {final_value:.2f}', 
                xy=(steps[-1], final_value),
                xytext=(-50, -20),  # Смещаем вниз-влево, чтобы текст не вылезал за границы
                textcoords='offset points',
                fontsize=10,
                fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.4', facecolor='#fef08a', edgecolor='#eab308', alpha=0.9))
    
    # Экспорт в Base64 PNG
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=120)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()
    
    return img_base64
