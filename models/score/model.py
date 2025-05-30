from scipy.stats import poisson  # Импортируем распределение Пуассона из scipy.stats
import numpy as np  # Импортируем библиотеку numpy для работы с массивами и математическими операциями

# Функция для расчёта вероятности ожидаемого количества голов для хозяев и гостей с помощью модели Пуассона
def count_teams_rating(s, h, home, away, team_to_index):
    """
    Рассчитывает силу в определенном матче хозяев и гостей на основе рейтингов силы команд.
    
    Параметры:
    - s: массив, содержащий рейтинги силы каждой команды.
    - h: бонус для домашнего поля (число, добавляемое к силе хозяев).
    - home: название команды-хозяина.
    - away: название команды-гостя.
    - team_to_index: словарь, сопоставляющий название команды с её индексом в массиве s.
    
    Возвращает:
    - home_strength: ожидаемое количество голов команды-хозяина.
    - away_strength: ожидаемое количество голов команды-гостя.
    """
    # Рассчитываем силу в матче для хозяев (экспонента разницы рейтингов плюс бонус за домашний стадион)
    home_strength = np.exp(s[team_to_index[home]] - s[team_to_index[away]] + h)
    
    # Рассчитываем силу в матче для гостей (экспонента разницы рейтингов, без бонуса)
    away_strength = np.exp(s[team_to_index[away]] - s[team_to_index[home]])
    
    return home_strength, away_strength  # Возвращаем рассчитанные вероятности голов

# Функция потерь для оптимизации разницы голов в матчах
def loss_goals(params, season_weight_factor, result_n, team_to_index, num_teams):
    """
    Функция потерь для модели предсказания разницы голов. Будем ее минимизировать.
    
    Параметры:
    - params: массив параметров модели (силы команд + бонус для хозяев поля).
    - season_weight_factor: коэффициент, уменьшающий вес старых сезонов в расчётах.
    - result_n: список матчей с информацией (хозяева, гости, разница мячей, сезон).
    - team_to_index: словарь соответствия названия команды её индексу.
    - num_teams: количество команд в лиге.
    
    Возвращает:
    - total_loss: общее значение функции потерь (чем меньше, тем лучше модель).
    """
    # Разбираем параметры: первые num_teams элементов — это силы команд, последний элемент — бонус хозяев
    s = params[:num_teams]  # Вытаскиваем силы команд
    h = params[num_teams]   # Вытаскиваем бонус для домашних матчей

    total_loss = 0  # Инициализируем суммарную ошибку
    
    # Перебираем все матчи из набора данных
    for home, away, goal_home, goal_away, season in result_n:
        # Получаем силу хозяев и гостей в очном матче с учетом домашнего преимущества
        lambda_home, lambda_away = count_teams_rating(s, h, home, away, team_to_index)

        # Вероятность именно получившегося исхода
        prob = poisson.pmf(goal_home, lambda_home) * poisson.pmf(goal_away, lambda_away)

        prob = max(prob, 1e-8)  # Защита от log(0), так как log(0) не определён

        # Учитываем сезонный вес, уменьшая влияние старых данных
        season_weight = np.power(season_weight_factor, -season)
        
        # Уменьшаем функцию потерь (используем логарифм вероятности для лучшей числовой стабильности)
        total_loss -= np.log(prob) * season_weight

    return total_loss  # Возвращаем общее значение функции потерь
