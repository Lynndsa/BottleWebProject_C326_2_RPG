import random
import networkx as nx
from collections import deque

class ProbabilisticBFS:
    def __init__(self, graph, p=0.5):
        """
        Инициализация стохастической модели распространения инфекции.
        :param graph: Сетвой граф популяции (NetworkX Graph)
        :param p: Вероятность успешной передачи вируса по ребру (0.0 - 1.0)
        """
        self.graph = graph
        self.p = p
        self.n_nodes = graph.number_of_nodes()
        
    def get_connected_component_size(self, start_nodes):
        """
        Классический BFS для поиска размера связной компоненты.
        Определяет теоретический максимум охвата, если бы вероятность p была равна 1.
        """
        visited = set(start_nodes)
        queue = deque(start_nodes)
                    
        while queue:
            node = queue.popleft()
            for neighbor in self.graph.neighbors(node):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
                    
        return len(visited)
    
    def run_single_simulation(self, initial_infected):
        """
        Запуск одного изолированного сценария (итерации) заражения.
        Реализует послойный вероятностный обход графа в ширину.
        """
        # Статусы: 0 — здоров, 1 — заражен. Шаги: -1 — не заражался, >=0 — такт заражения
        status = {node: 0 for node in self.graph.nodes()}
        infection_steps = {node: -1 for node in self.graph.nodes()}
        
        queue = deque()
        current_infected_count = 0
        
        # Первичная инициализация нулевого слоя (очагов инфекции)
        for node in initial_infected:
            if node in status:
                status[node] = 1
                infection_steps[node] = 0
                queue.append(node)
                current_infected_count += 1
            
        step = 0
        infected_count_per_step = [current_infected_count] # Фиксация кумулятивной динамики
        
        # Послойный обход графа (один цикл while = одна волна/шаг времени)
        while queue:
            step += 1
            current_level_size = len(queue) # Фиксируем размер текущего фронта инфекции
            newly_infected = []
            
            for _ in range(current_level_size):
                current_node = queue.popleft()
                
                for neighbor in self.graph.neighbors(current_node):
                    if status[neighbor] == 0:  # Проверка только не болевших соседей
                        # Розыгрыш вероятности заражения (Бернуллиевское испытание)
                        if random.random() < self.p:
                            status[neighbor] = 1
                            infection_steps[neighbor] = step
                            newly_infected.append(neighbor)
                            current_infected_count += 1
            
            # Переносим свежезараженных на следующий шаг симуляции
            for node in newly_infected:
                queue.append(node)
                
            infected_count_per_step.append(current_infected_count)
            
        return {
            'total_infected': current_infected_count, # Итоговое число заболевших
            'duration': step,                         # Время затухания вспышки
            'infection_steps': infection_steps,       # Лог "кто на каком шаге заболел"
            'infection_progression': infected_count_per_step # Временной ряд кумулятивного прироста
        }
    
    def monte_carlo_simulation(self, initial_infected, num_iterations=100):
        """
        Монте-Карло агрегация: запуск ансамбля независимых симуляций 
        для получения устойчивых статистических оценок процесса.
        """
        results = []
        for _ in range(num_iterations):
            results.append(self.run_single_simulation(initial_infected))
        
        # Расчет базовых статистических метрик
        avg_infected = sum(r['total_infected'] for r in results) / num_iterations
        avg_duration = sum(r['duration'] for r in results) / num_iterations
        max_infected = max(r['total_infected'] for r in results)
        min_infected = min(r['total_infected'] for r in results)
        
        # Расчет индивидуальной частоты (риска) заражения для каждого узла графа
        infection_frequency = {node: 0 for node in self.graph.nodes()}
        for result in results:
            for node, step in result['infection_steps'].items():
                if step >= 0:
                    infection_frequency[node] += 1
        
        for node in infection_frequency:
            infection_frequency[node] /= num_iterations
        
        # Вычисление жесткого предела достижимости (изолированные подграфы вирус не пройдут)
        theoretical_max = self.get_connected_component_size(initial_infected)
        
        # Поиск моды распределения — наиболее часто повторяющегося паттерна (состава) заражения
        infection_counts = {}
        for result in results:
            infected_tuple = tuple(sorted([n for n, step in result['infection_steps'].items() if step >= 0]))
            infection_counts[infected_tuple] = infection_counts.get(infected_tuple, 0) + 1
        
        most_common_infection = max(infection_counts.items(), key=lambda x: x[1]) if infection_counts else ((), 0)
        
        # Синхронизация и усреднение временных рядов (кривых инфекции) разной длины
        max_steps = max(len(r['infection_progression']) for r in results)
        avg_progression = []
        for step in range(max_steps):
            step_sum = 0
            for r in results:
                progression = r['infection_progression']
                # Если симуляция завершилась раньше max_steps, удерживаем её финальное плато
                if step < len(progression):
                    step_sum += progression[step]
                else:
                    step_sum += progression[-1]
            avg_progression.append(step_sum / num_iterations)
        
        return {
            'avg_infected_count': avg_infected,                    # Среднее число зараженных узлов
            'avg_infected_percentage': (avg_infected / self.n_nodes) * 100, # Средний процент поражения популяции
            'avg_duration': avg_duration,                          # Среднее время жизни эпидемии
            'infection_frequencies': infection_frequency,          # Словарь рисков для визуализации (тепловая карта)
            'max_possible_reach': theoretical_max,                 # Предел компоненты связности
            'max_infected': max_infected,                          # Худший сценарий охвата
            'min_infected': min_infected,                          # Лучший сценарий охвата
            'iterations': num_iterations,                          # Объем выборки
            'most_common_pattern': list(most_common_infection[0]), # Состав типичной группы зараженных
            'pattern_probability': (most_common_infection[1] / num_iterations) * 100, # Вероятность этого паттерна
            'timeline': avg_progression                            # Данные для отрисовки 2D-графика
        }