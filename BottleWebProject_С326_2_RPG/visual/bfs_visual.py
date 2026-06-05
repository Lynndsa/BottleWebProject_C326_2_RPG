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

import matplotlib.patches as mpatches

def generate_graph_svg(graph, initial_infected=None, infection_frequency=None):
    """Генерирует SVG графа с легендой в правом нижнем углу"""
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
            node_colors.append('#dc2626') 
        elif infection_frequency and node in infection_frequency:
            freq = infection_frequency[node]
            if freq > 0.7:
                node_colors.append('#FC0176')  
            elif freq > 0.4:
                node_colors.append('#f97316')  
            elif freq > 0.05:
                node_colors.append('#FFFF00')  
            else:
                node_colors.append('#e5e7eb')  
        else:
            node_colors.append('#e5e7eb')
    
    # Рисуем граф
    nx.draw_networkx_nodes(graph, pos, node_color=node_colors, node_size=600, alpha=0.9, edgecolors='#4b5563', linewidths=1.5)
    nx.draw_networkx_edges(graph, pos, width=1.5, alpha=0.5, edge_color='#9ca3af')
    nx.draw_networkx_labels(graph, pos, font_size=10, font_weight='bold', font_color='#1f2937')
    
    plt.title("Структура сети и частота заражения узлов", fontsize=12, pad=15)
    plt.axis('off')
    
    legend_labels = [
        mpatches.Patch(color='#dc2626', label='Начальный очаг'),
        mpatches.Patch(color='#FC0176', label='Частота > 70%'),
        mpatches.Patch(color='#f97316', label='Частота 40% – 70%'),
        mpatches.Patch(color='#FFFF00', label='Частота 5% – 40%'),
        mpatches.Patch(color='#e5e7eb', label='Безопасный / Здоровый (< 5%)')
    ]
    
    plt.legend(
        handles=legend_labels, 
        loc='lower left',             # Точка привязки самой панели легенды
        bbox_to_anchor=(1.02, 0.0),    # Смещение: x=1.02 (снаружи графа), y=0.0 (снизу)
        title='Условные обозначения', 
        frameon=True, 
        facecolor='white', 
        edgecolor='#e5e7eb', 
        fontsize=10, 
        title_fontsize=11
    )
    
    plt.tight_layout()
    
    # Сохраняем в SVG
    buf = io.BytesIO()
    plt.savefig(buf, format='svg', bbox_inches='tight', facecolor='white')
    buf.seek(0)
    svg_string = buf.getvalue().decode('utf-8')
    plt.close()
    
    return svg_string

def generate_infection_chart(progression_data, n_nodes):
    """Генерирует график динамики заражения в процентах от населения"""
    if not progression_data or n_nodes == 0:
        return None
    
    plt.figure(figsize=(10, 5))
    
    # Переводим абсолютное количество узлов в проценты
    progression_percentage = [(val / n_nodes) * 100 for val in progression_data]
    steps = list(range(len(progression_data)))
    
    # Строим график по процентным значениям
    plt.plot(steps, progression_percentage, marker='o', linewidth=2, markersize=4, color='#dc2626', label='Заражённое население (%)')
    
    plt.xlabel('Шаг распространения (уровень BFS)', fontsize=11)
    plt.ylabel('Процент заражённого населения (%)', fontsize=11)
    plt.title('Динамика распространения инфекции (усреднённая)', fontsize=12, fontweight='bold')
    
    # Настраиваем отображение сетки и лимитов для наглядности (от 0% до 100%)
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.ylim(-5, 105) 
    plt.legend(loc='lower right')
    
    # Аннотация финального результата в процентах
    if progression_percentage:
        final_percentage = progression_percentage[-1]
        plt.annotate(f'Итог: {final_percentage:.1f}%', 
                    xy=(steps[-1], final_percentage),
                    xytext=(-50, -15),
                    textcoords='offset points',
                    fontsize=9,
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='#fef08a', alpha=0.8))
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()
    
    return img_base64