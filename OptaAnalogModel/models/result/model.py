from scipy.stats import poisson  # Распределение Пуассона
import numpy as np  # Numpy для математических операций

# Функция расчёта вероятностей исходов матча
def count_teams_probs(s, h, d, home, away, team_to_index):
    """
    Рассчитывает вероятности исходов (П1, Х, П2) на основе рейтингов силы команд.
    
    Параметры:
    - s: массив рейтингов силы команд.
    - h: бонус домашнего поля.
    - d: фактор ничьей.
    - home: название команды-хозяина.
    - away: название команды-гостя.
    - team_to_index: словарь {команда: индекс}.

    Возвращает:
    - prob_home: вероятность победы хозяев.
    - prob_away: вероятность победы гостей.
    - prob_draw: вероятность ничьей.
    """
    home_strength = np.exp(s[team_to_index[home]] - s[team_to_index[away]] + h)
    away_strength = np.exp(s[team_to_index[away]] - s[team_to_index[home]] - h)
    draw = np.exp(d)
    
    all_prob = home_strength + away_strength + draw
    prob_home, prob_away, prob_draw = home_strength / all_prob, away_strength / all_prob, draw / all_prob

    return prob_home, prob_away, prob_draw

# Функция потерь для оптимизации предсказания исходов матчей
def loss_goals(params, season_weight_factor, result_n, team_to_index, num_teams):
    """
    Функция потерь для предсказания исходов матчей (П1, X, П2).
    
    Параметры:
    - params: массив параметров модели (силы команд + бонус хозяев + фактор ничьей).
    - season_weight_factor: коэффициент уменьшения веса старых сезонов.
    - result_n: список матчей (хозяева, гости, исход (1=П1, 0=X, -1=П2), сезон).
    - team_to_index: словарь {команда: индекс}.
    - num_teams: количество команд.

    Возвращает:
    - total_loss: сумму -log(вероятность исхода), которую мы минимизируем.
    """
    s = params[:num_teams]  # Силы команд
    h = params[num_teams]   # Бонус домашних матчей
    d = params[num_teams + 1]  # Фактор ничьей

    total_loss = 0  # Ошибка предсказания исходов матчей
    
    for home, away, result, season in result_n:
        p_win_home, p_win_away, p_draw = count_teams_probs(s, h, d, home, away, team_to_index)
        # Вычисление потерь на основе результата матча
        season_weight = np.power(season_weight_factor, -season)

        if result == 1:
            total_loss -= np.log(p_win_home) * season_weight
            # if (p_win_away > 1e-8):
            #   total_loss += np.log(p_win_away) * season_weight
        elif result == 0:
            total_loss -= np.log(p_draw) * season_weight
        elif result == -1:
            total_loss -= np.log(p_win_away) * season_weight
            # if (p_win_home > 1e-8):
            #   total_loss += np.log(p_win_home) * season_weight

    return total_loss
