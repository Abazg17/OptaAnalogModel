# Импорт необходимых модулей и функций
from data_preprocess import process_all_seasons  # Функции для обработки данных
from simulate import simulateScore  # Функции для симуляции матчей
from model import loss_goals  # Функции для расчёта силы команд

import numpy as np  # Для работы с массивами
import pandas as pd  # Для создания таблицы с результатами
from scipy.optimize import minimize  # Для оптимизации параметров модели
import os
from tqdm import tqdm

#------------------------------------------------------------------------------------------


# Получаем список всех .xlsx файлов в текущей папкеimport os
script_dir = os.path.dirname(os.path.abspath(__file__))  # Директория текущего скрипта
xlsx_files = [f for f in os.listdir(script_dir) if f.endswith(".xlsx")]

# Проверяем, что найден ровно один файл
if len(xlsx_files) == 1:
    file_path = os.path.join(script_dir, xlsx_files[0])  # Создаём полный путь к файлу
else:
    raise ValueError("Ошибка: В папке должен быть ровно один .xlsx файл!")


# Обрабатываем данные из файла: 
# - all_games: все матчи всех сезонов
# - last_teams: список команд последнего сезона
# - last_data: матрица результатов матчей последнего сезона
all_games, last_teams, last_data = process_all_seasons(file_path)

# Отбираем только те матчи, где обе команды играли в последнем сезоне
need_games = np.array([
    row for row in np.array(all_games) if row[0] in last_teams and row[1] in last_teams
])

# Создаём словарь, сопоставляющий название команды с её индексом
team_to_index = {name: i for i, name in enumerate(last_teams)}

# Определяем количество команд в последнем сезоне
num_teams = len(last_teams)
print("Обработали данные")


#------------------------------------------------------------------------------------------


# Задаём начальные параметры для оптимизации: 
# - первые num_teams элементов — начальные значения силы команд (нулевые)
# - последний элемент — бонус домашнего поля (тоже ноль)
initial_params = np.zeros(num_teams + 1)

# Коэффициент затухания веса сезонов (старые сезоны менее значимы)
season_weight_factor = 0.45

def tqdm_callback(xk):
    pbar.update(1)

# Оптимизируем параметры модели, минимизируя функцию потерь loss_goals
# Оборачиваем tqdm для отслеживания прогресса
with tqdm(total=20, desc="Оптимизация", ncols=100) as pbar:
    # Функция callback для обновления прогресса
    def callback(xk):
        tqdm_callback(xk)  # Вызываем функцию с обновлением прогресса

    # Выполнение оптимизации с использованием callback для обновления прогресса
    res = minimize(
        loss_goals,  # Функция потерь
        initial_params,  # Начальные параметры
        args=(season_weight_factor, need_games, team_to_index, num_teams),  # Дополнительные аргументы
        method="L-BFGS-B",  # Метод оптимизации
        callback=callback
    )

# Получаем оптимизированные параметры:
# - team_strengths — рассчитанные силы команд
# - home_bonus — бонус домашнего поля
optimized_params = res.x
team_strengths = optimized_params[:num_teams]
home_bonus = optimized_params[num_teams]


print("Закончили обучение модели")
#------------------------------------------------------------------------------------------


# Количество симуляций
num_simulations = input("Введите количество симуляций (по умолчанию 100000): ")
num_simulations = int(num_simulations) if num_simulations.strip() else 100000


# Запускаем симуляцию оставшихся матчей сезона и получаем вероятности занятых мест
team_positions = simulateScore(
    last_data, last_teams, team_strengths, home_bonus, team_to_index, num_simulations
)

# Сортируем команды по наиболее вероятному итогу сезона (по вероятностям мест)
teams_for_print = sorted(
    last_teams, 
    key=lambda team: tuple(-p for p in team_positions[last_teams.index(team)])  # Сортируем по вероятностям
)

print("Закончили симуляцию")
#------------------------------------------------------------------------------------------


# Создаём список для хранения отформатированных результатов
formatted_results = []

# Формируем таблицу вероятностей для каждой команды
for team_name in teams_for_print:
    team_idx = last_teams.index(team_name)  # Получаем индекс команды
    probas = 100 * team_positions[team_idx] / num_simulations  # Рассчитываем вероятности в процентах
    formatted_probs = [f"{prob:.1f}%" for prob in probas]  # Округляем и форматируем
    formatted_results.append([team_name] + formatted_probs)  # Добавляем в список

# Создаём DataFrame (таблицу) для красивого представления результатов
df = pd.DataFrame(
    formatted_results, 
    columns=["Team"] + [f"Position {i+1}" for i in range(team_positions.shape[1])]
)

# Указываем путь для сохранения таблицы с результатами
folder = "results"
os.makedirs(folder, exist_ok=True)  # Создаст папку, если её нет

file_path = os.path.join(folder, "probabilities.xlsx")
df.to_excel(file_path, index=False)

# В итоге в файле "probabilities.xlsx" будет таблица с командами и вероятностями их мест в чемпионате