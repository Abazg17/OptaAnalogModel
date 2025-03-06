import numpy as np
from model import count_teams_rating 
from tqdm import tqdm

def calculate_head_to_head_points(results_matrix, teams, tied_teams):
    """
    Рассчитывает статистику личных встреч между командами из списка tied_teams:
    - Очки, набранные в матчах друг с другом.
    - Разницу голов в этих матчах.
    - Количество забитых мячей.
    
    Также рассчитывает общую разницу голов и общее количество забитых мячей во всех матчах.
    """
    num_teams = len(teams)
    
    # Статистика для личных встреч
    head_to_head_points = {team: 0 for team in tied_teams}
    goal_difference = {team: 0 for team in tied_teams}
    goals_scored = {team: 0 for team in tied_teams}

    # Статистика для всех матчей
    total_goal_difference = {team: 0 for team in teams}
    total_goals_scored = {team: 0 for team in teams}

    for i in range(num_teams):
        for j in range(num_teams):
            if i == j:
                continue  # Пропускаем матчи против самих себя
            
            home_team = teams[i]
            away_team = teams[j]
            home_goals, away_goals = int(results_matrix[i][j][0]), int(results_matrix[i][j][-1])

            # Подсчёт общей разницы голов
            total_goal_difference[home_team] += (home_goals - away_goals)
            total_goal_difference[away_team] += (away_goals - home_goals)

            # Подсчёт общего количества забитых голов
            total_goals_scored[home_team] += home_goals
            total_goals_scored[away_team] += away_goals

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

                # Разница голов в личных встречах
                goal_difference[home_team] += (home_goals - away_goals)
                goal_difference[away_team] += (away_goals - home_goals)

                # Забитые голы в личных встречах
                goals_scored[home_team] += home_goals
                goals_scored[away_team] += away_goals

    return head_to_head_points, goal_difference, goals_scored, total_goal_difference, total_goals_scored


def simulateScore(data, teams, team_strengths, home_bonus, team_to_index, num_simulations=3500):
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
                    lambda_home, lambda_away = count_teams_rating(team_strengths, home_bonus, home_team, away_team, team_to_index)

                    # Генерируем количество голов по распределению Пуассона
                    home_goals = np.random.poisson(lambda_home)
                    away_goals = np.random.poisson(lambda_away)

                    # Ограничиваем максимальное число голов
                    home_goals = min(9, home_goals)
                    away_goals = min(9, away_goals)

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
                head_to_head_points, head_to_head_goal_diff, head_to_head_goals, total_goal_difference, total_goals_scored = calculate_head_to_head_points(sim_results, teams, tied_teams)

                # Сортируем команды по дополнительным критериям
                tied_teams.sort(
                    key=lambda team: (
                        -head_to_head_points[team],  # Очки в личных встречах
                        -head_to_head_goal_diff[team],  # Разница голов в личных встречах
                        -head_to_head_goals[team],  # Забитые голы в личных встречах
                        -total_goal_difference[team],  # Общая разница голов
                        -total_goals_scored[team]  # Общее количество забитых голов
                    )
                )

            sorted_teams.extend(tied_teams)

        # Обновляем матрицу финишных позиций
        for idx, team in enumerate(sorted_teams):
            team_idx = teams.index(team)
            team_positions[team_idx][idx] += 1  # Засчитываем место, которое команда заняла в симуляции
    
    return team_positions
