import pandas as pd
import numpy as np

def diff_score(result):
    """
    Сравнивает результат матча между двумя командами.

    Аргументы:
    result : str
        Строка с результатом матча в формате "X-Y", где X — количество голов первой команды, Y — количество голов второй команды.
        Обязательно меньше 9.5 голов!!
        
    Возвращает:
    int : 
        Разница мячей
    """
    score1, score2 = int(result[0]), int(result[-1])
    return score1 - score2

def process_season_data(data, teams, season_label):
    """
    Обрабатывает данные сезона и возвращает DataFrame с результатами матчей для указанного сезона.

    Аргументы:
    data : list of list
        Двумерный список, представляющий матрицу результатов матчей для сезона.
    teams : list
        Список команд, участвующих в сезоне.
    season_label : int
        Месячная метка сезона, чтобы различать данные разных сезонов.

    Возвращает:
    DataFrame, list, list
        - DataFrame с результатами матчей между командами,
        - Список команд для сезона,
        - Оригинальные данные сезона.
    """
    df = pd.DataFrame(data, columns=teams, index=teams)
    comparison_data = []
    
    for i in range(len(df)):
        for j in range(len(df.columns)):
            if i != j and len(df.iloc[i, j]) == 3:  # Исключаем матчи с самим собой
                comparison_data.append([
                    teams[i],       # Команда из строки
                    teams[j],       # Команда из столбца
                    diff_score(df.iloc[i, j]),  # Результат сравнения
                    season_label    # Сезон (метка)
                ])
                
    return pd.DataFrame(comparison_data, columns=["Домашняя команда", "Гостевая команда", "Результат", "Сезон"]), teams, data

def process_all_seasons(file):
    """
    Обрабатывает все сезоны из Excel файла, объединяя данные всех сезонов в один DataFrame.

    Аргументы:
    file : str
        Путь к Excel файлу с данными сезонов.

    Возвращает:
    DataFrame, list, list
        - Объединенный DataFrame с данными всех сезонов,
        - Список команд последнего сезона,
        - Данные последнего сезона.
    """
    all_seasons_data = []
    last_season_teams = None
    last_season_data = None

    # Открытие Excel файла для обработки
    with pd.ExcelFile(file) as xls:
        for idx, sheet_name in enumerate(xls.sheet_names):
            # Чтение данных из каждого сезона
            season_data = pd.read_excel(xls, sheet_name=sheet_name, header=None)
            teams = season_data.iloc[0, 1:].dropna().tolist()  # Извлечение названий команд
            data = season_data.iloc[1:, 1:].fillna("").values.tolist()  # Получение матрицы результатов
            season_label = -len(xls.sheet_names) + idx + 1  # Присваиваем метку сезона (для сортировки)
            
            # Обработка данных для текущего сезона
            season_df, current_teams, current_data = process_season_data(data, teams, season_label)
            all_seasons_data.append(season_df)

            # Сохраняем данные последнего сезона
            if idx == len(xls.sheet_names) - 1:
                last_season_teams = current_teams
                last_season_data = current_data

    # Объединяем данные всех сезонов в один DataFrame
    combined_df = pd.concat(all_seasons_data, ignore_index=True)
    return combined_df, last_season_teams, last_season_data
