import numpy as np
from model import count_teams_probs 
from tqdm import tqdm

def calculate_head_to_head_stats(results_matrix, teams, tied_teams):
    """
    Рассчитывает статистику личных встреч между командами из списка tied_teams:
    - Очки, набранные в матчах друг с другом.
    - Количество побед в личных встречах.
    """
    num_teams = len(teams)

    # Статистика для личных встреч
    head_to_head_points = {team: 0 for team in tied_teams}
    wins = {team: 0 for team in teams}

    for i in range(num_teams):
        for j in range(num_teams):
            if i == j:
                continue  # Пропускаем матчи против самих себя
            
            home_team = teams[i]
            away_team = teams[j]
            home_goals, away_goals = int(results_matrix[i][j][0]), int(results_matrix[i][j][-1])
            if home_goals > away_goals:
                wins[home_team] += 1
            elif home_goals < away_goals:
                wins[away_team] += 1

            # Если обе команды в списке tied_teams, учитываем личные встречи
            if home_team in tied_teams and away_team in tied_teams:
                # Очки в личных встречах
                if home_goals > away_goals:
                    head_to_head_points[home_team] += 3
                elif home_goals < away_goals:
                    head_to_head_points[away_team] += 3
                else:
                    head_to_head_points[home_team] += 1
                    head_to_head_points[away_team] += 1

    return head_to_head_points, wins



def simulateScore(data, teams, team_strengths, home_bonus, draw_factor, team_to_index, num_simulations=3500):
    """
    Симулирует оставшиеся матчи сезона и определяет распределение вероятностей финишных позиций команд.

    Параметры:
    - data: матрица текущих результатов матчей (частично заполнена).
    - teams: список всех команд.
    - team_strengths: рейтинг силы каждой команды.
    - home_bonus: дополнительный бонус для домашних матчей.
    - team_to_index: словарь соответствия команд их индексам.
    - num_simulations: количество симуляций.

    Возвращает:
    - team_positions: матрица, где (i, j) показывает, сколько раз команда i заняла место j.
    """
    results = np.copy(data)  # Копируем матрицу матчей, чтобы не изменять оригинал
    team_positions = np.zeros((len(teams), len(teams)))  # Матрица финишных позиций команд
    
    for _ in tqdm(range(num_simulations), desc="Прогресс", unit="шаг", ncols=100):
        sim_results = np.copy(results)  # Копируем текущие результаты

        # Симулируем каждый незаконченный матч
        for i, home_team in enumerate(teams):
            for j, away_team in enumerate(teams):
                if i != j and len(sim_results[i][j]) < 3:
                    # Рассчитываем ожидаемые голы для обеих команд
                    home_pr, away_pr, draw_pr = count_teams_probs(team_strengths, home_bonus, draw_factor, home_team, away_team, team_to_index)
                    outcomes = [1, -1, 0]
                    probabilities = [home_pr, away_pr, draw_pr]
                    
                    match_result = np.random.choice(outcomes, p=probabilities)
                    if match_result==1:
                        home_goals = 1
                        away_goals = 0
                    elif match_result==0:
                        home_goals = 0
                        away_goals = 0
                    else:
                        home_goals = 0
                        away_goals = 1

                    # Записываем результат матча
                    sim_results[i][j] = f"{home_goals}:{away_goals}"
                
        # Подсчёт очков для каждой команды
        team_points = np.zeros(len(teams))
        for i, team in enumerate(teams):
            team_points[i] += np.sum([3 if sim_results[i][j][0] > sim_results[i][j][-1] else 0 for j in range(len(teams))])
            team_points[i] += np.sum([1 if sim_results[i][j][0] == sim_results[i][j][-1] else 0 for j in range(len(teams))])
            team_points[i] += np.sum([3 if sim_results[j][i][0] < sim_results[j][i][-1] else 0 for j in range(len(teams))])
            team_points[i] += np.sum([1 if sim_results[j][i][0] == sim_results[j][i][-1] else 0 for j in range(len(teams))])

        # Получаем уникальные значения очков и сортируем их по убыванию
        unique_points = np.unique(team_points)[::-1]
        sorted_teams = []

        # Разрешаем ситуации, когда несколько команд набрали одинаковое количество очков
        for points in unique_points:
            tied_teams = [teams[i] for i in range(len(teams)) if team_points[i] == points]

            if len(tied_teams) > 1:
                # Подсчитываем дополнительные параметры для сортировки
                head_to_head_points, total_wins = calculate_head_to_head_stats(sim_results, teams, tied_teams)

                # Сортируем команды по дополнительным критериям
                tied_teams.sort(
                    key=lambda team: (
                        -head_to_head_points[team],  # Очки в личных встречах
                        -total_wins[team],
                        -team_strengths[team_to_index[team]] 
                    )
                )

            sorted_teams.extend(tied_teams)

        # Обновляем матрицу финишных позиций
        for idx, team in enumerate(sorted_teams):
            team_idx = teams.index(team)
            team_positions[team_idx][idx] += 1  # Засчитываем место, которое команда заняла в симуляции
    
    return team_positions
