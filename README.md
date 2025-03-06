# Аналог модели OPTA для предсказаний вероятности итогов футбольного чемпионата
На основании метода максимального правдоподобия и метода Монте-Карло моделируем итоговые результаты европейских чемпионатов

<br><br>

## 📌 Оглавление
1. [Описание](#описание)
2. [Установка](#установка)
3. [Модели](#модели)
4. [Производительность](#производительность)
5. [Использование](#использование)
6. [Авторы](#авторы)

<br><br>
## <a name="описание">📖 Описание
Несколько основ для понимания.
   
### Метод максимального правдоподобия
<img src="README/images/MMP_for_README.png" width="400" />
У нас имеется выборка значений какого-либо распределения и мы хотим найти параметры этого распределения.
Тогда мы находим тот параметр, с которым суммарная вероятность получения нашей выборки максимальная.
Например, на картинке зеленое распределение описывает выборку (точки на нижнем оси) явно хуже, чем красное.

### Метод Монте-Карло. 
Модель, основанная на вероятностях событий, многократно обсчитывается и на основе полученных данных вычисляются вероятностные характеристики рассматриваемого процесса.

### Распределение Пуассона, используемое для моделирования редких событий
<img src="README/images/Poasson_dist.png" width="400" />


### О моделях. 
Более подробно разберем их на абзац ниже в [Модели](#модели). Глобальный (общий) смысл такой. Мы используем результаты игр в чемпионате за последние несколько сезонов. На основании этих результатов выводятся силы команд, которые затем конвертируются в вероятности победы в каждом отдельном матче. Затем по этим вероятность текущий чемпионат симулируется до конца и методом Монте-Карло получаются итоговые вероятности занять нужное место для нужной команды


<br><br>
## <a name="модели">📊 Модели
### Алгоритм использует только результаты матчей. 
Каждой команде сопоставляем значение рейтинга. Сначала допустим, что силы команд уже известны и мы хотим просимулировать определенный матч. Тогда из рейтингов двух команд и фактора домашней команды мы считаем силу обеих команд в этом, отдельновзятом, матче. Затем исходя из этих вероятностей мы случайным образом (выбирая число от 0 до 100) симулируем результат игры. 
Как мы считаем рейтинг команды? На каждой итерации для каждого матча модель на основе **текущих** сил команд считает вероятности результата игры и затем считает свою "ошибку", **вычитая** вероятность **верного** (случившегося) исхода. **Чем меньше эта вероятность, тем больше ошибка модели** -> минимизируя ошибку, мы подбираем такие силы, что вероятность случившихся результатов максимальная. Кроме этого, модель также учитывает, что влияние более давних матчей уменьшается, то есть ошибка модели на этих данных менее критична - модель старается лучше описать последние результаты.

### Второй алгоритм учитывает счет, с которым играют команды 
Для этого используется распределение Пуассона. Смысл абсолютно такой же - мы подбираем такие силы команд, чтобы они, являясь параметрами для распределения Пуассона, наилучшим образом соответствовали количеству забитых голов в каждом матче. Затем симулируем уже не результат, а счет игры. Здесь мы даже можем достоверно расположить команды с равным количеством очков, так как уже знаем разницу мячей.

### Третий алгоритм предполагает, что важен не счет, а разница забитых голов. 
Модель учится так, что 0:2 и 6:8 - одинаковые с точки зрения футбола исходы (что, конечно, не совсем так). Вместо того, чтобы приближать силами команд голы забитые в матче, модель учится приближать разность голов. То есть теперь у команд такие силы, которые лучше всего описывают попарные разности голов в матчах, а не количество этих голов. Для этого тоже используется распределение Пуассона. А моделируется результат также, как и во втором случае - мы моделируем количество голов, забитых каждой командой.


<br><br>
## <a name="производительность">📊 Производительность
Модели сравниваются с OPTA по среднему абсолютному отклонению (усредненный модуль разности с целевыми значениями), т.е. MAE, а также по "MAE на вероятных исходах", то есть на исходах с вероятностью более процента. Эти данные вместе со всеми результатами можно проверить в папке `models_metrics`.

<table>
  <tr>
    <th rowspan="2">Модель</th>
    <th colspan="4">MAE</th>
    <th colspan="4">MAE >1%</th>
    <th rowspan="2">Время обучения</th>
  </tr>
  <tr>
    <th>ITA</th> <th>ESP</th> <th>RUS</th> <th>Total</th>
    <th>ITA</th> <th>ESP</th> <th>RUS</th> <th>Total</th>
  </tr>
  <tr>
    <td>Result model</td> <td><i>0.83%</i></td> <td><i>0.82%</i></td> <td><i>0.89%</i></td> <td><strong>0.84%</strong></td>
    <td><i>2.60%</i></td> <td><i>2.09%</i></td> <td><i>2.16%</i></td> <td><strong>2.28%</strong></td> <td>Очень быстро</td>
  </tr>
  <tr>
    <td>Score</td> <td><i>0.68%</i></td> <td><i>0.71%</i></td> <td><i>1.08%</i></td> <td><strong>0.82%</strong></td>
    <td><i>2.12%</i></td> <td><i>1.79%</i></td> <td><i>2.59%</i></td> <td><strong>2.16%</strong></td> <td>Быстро</td>
  </tr>
  <tr>
    <td>Diff_score model</td> <td><i>0.84%</i></td> <td><i>0.73%</i></td> <td><i>1.26%</i></td> <td><strong>0.94%</strong></td>
    <td><i>2.65%</i></td> <td><i>1.85%</i></td> <td><i>3.01%</i></td> <td><strong>2.5%</strong></td> <td>Медленно (4-5 мин)</td>
  </tr>
</table>




<br><br>
## <a name="установка">🛠 Установка
1. Клонируйте репозиторий
2. Установите зависимости из `requirements.txt`
Вы можете установить их с помощью:
```bash
pip install -r requirements.txt
```

<br><br>
## <a name="использование"> 💡 Использование
1. Выберите одну из моделей. Они находятся в папке `models`:
   - `Result` — первая модель, предсказывающая исход.
   - `Score` — вторая модель, предсказывающая счёт.
   - `Score_diff` — третья модель, предсказывающая разницу мячей.
2. Основной способ варианта запуска:
   - `main.py` (выполнить команду `python main.py` в папке с моделью).
3. Выберите чемпионат (есть три варианта данных в `for_data`) и перенесите **только этот** файл в папку с выбранной моделью.  
   Рядом с запускаемым файлом должен находиться **единственный** файл `.xlsx`.
4. При использовании других данных должно выполняться обязательное условие:
   - Отсутствие матчей, в которых команда забила более 9.5 голов.
   - Названия команд в файле должны совпадать между сезонами.
   - Формат файла должен соответствовать уже имеющимся данным (результаты матчей попарно).  
     Данные легко находятся на страницах Википедии, например, для Серии А на итальянском языке.
5. После завершения работы модели в папке `results` появится файл `probabilities.xlsx`.  
   **При перезапуске он будет перезаписан**.



---
## <a name="авторы">✍️ Авторы (с долей юмора)
- Разработчик: Ватаман Михаил
- Комментатор и переводчик: ChatGPT
- Аналитик: сказал, что главное правильно интерпретировать результат
- Реклама: ПФК ЦСКА
- Мой любимый футболист: Эсмир Байрактаревич
- Отель: Триваго 
