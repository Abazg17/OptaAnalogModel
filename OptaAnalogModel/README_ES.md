# ✨ Modelo análogo a OPTA para predecir probabilidades en ligas de fútbol (ATraducción de AI)
Usamos el método de máxima verosimilitud y el método de Montecarlo para simular los resultados finales de las ligas europeas.

<br><br>

## 📌 Tabla de contenido
1. [Descripción](#descripcion)
2. [Instalación](#instalacion)
3. [Modelos](#modelos)
4. [Rendimiento](#rendimiento)
5. [Uso](#uso)
6. [Autores](#autores)

<br><br>
## <a name="descripcion">📖 Descripción
Algunos conceptos clave para la comprensión.

### Método de Máxima Verosimilitud
<img src="images/MMP_for_README.png" width="400" />
Disponemos de una muestra de valores de una distribución y queremos encontrar sus parámetros.
Buscamos el parámetro con el cual la probabilidad conjunta de la muestra es máxima.
Por ejemplo, en la imagen, la distribución verde describe la muestra (puntos en el eje inferior) peor que la roja.

### Método de Montecarlo
El modelo se calcula repetidamente y, con los datos obtenidos, se extraen características probabilísticas del proceso.

### Distribución de Poisson para modelar eventos raros
<img src="images/Poasson_dist.png" width="400" />

### Sobre los modelos
Se detallan en la sección de [Modelos](#modelos). En términos generales, usamos los resultados de los últimos campeonatos para estimar la fuerza de los equipos, que luego se convierte en probabilidades de victoria en cada partido. Con estas probabilidades, simulamos la temporada completa y usamos el método de Montecarlo para determinar la probabilidad final de cada posición para cada equipo.

<br><br>
## <a name="modelos">📊 Modelos
### El algoritmo solo usa los resultados de los partidos.
A cada equipo se le asigna una puntuación inicial. Para simular un partido, se calcula la fuerza relativa de los equipos considerando el factor de localía. Luego, con base en esas probabilidades, simulamos el resultado de manera aleatoria.

Para calcular las puntuaciones, la modelo optimiza iterativamente las probabilidades de los partidos pasados, minimizando el error entre las predicciones y los resultados reales. A los partidos más recientes se les da mayor peso.

### El segundo algoritmo considera el número de goles anotados
Usa la distribución de Poisson para modelar los goles. La metodología es similar, pero en lugar de predecir solo el resultado, se predice el marcador exacto. Esto permite diferenciar equipos con los mismos puntos por diferencia de goles.

### El tercer algoritmo modela la diferencia de goles en lugar del marcador exacto
El modelo considera que, por ejemplo, un 0:2 y un 6:8 son similares en términos futbolísticos. En lugar de ajustar las probabilidades a los goles anotados, las ajusta a la diferencia de goles. También usa la distribución de Poisson y el resultado del partido se simula de la misma forma que en el segundo modelo.

<br><br>
## <a name="rendimiento">📊 Rendimiento
Los modelos se comparan con OPTA utilizando el error absoluto medio (MAE) y el "MAE en eventos probables" (MAE para eventos con una probabilidad mayor al 1%). Los resultados completos están en la carpeta `models_metrics`.

<table>
  <tr>
    <th rowspan="2">Modelo</th>
    <th colspan="4">MAE</th>
    <th colspan="4">MAE >1%</th>
    <th rowspan="2">Tiempo de entrenamiento</th>
  </tr>
  <tr>
    <th>ITA</th> <th>ESP</th> <th>RUS</th> <th>Total</th>
    <th>ITA</th> <th>ESP</th> <th>RUS</th> <th>Total</th>
  </tr>
  <tr>
    <td>Modelo para resultado</td> <td><i>0.83%</i></td> <td><i>0.82%</i></td> <td><i>0.89%</i></td> <td><strong>0.84%</strong></td>
    <td><i>2.60%</i></td> <td><i>2.09%</i></td> <td><i>2.16%</i></td> <td><strong>2.28%</strong></td> <td>Muy rápido</td>
  </tr>
  <tr>
    <td>Modelo para marcador</td> <td><i>0.68%</i></td> <td><i>0.71%</i></td> <td><i>1.08%</i></td> <td><strong>0.82%</strong></td>
    <td><i>2.12%</i></td> <td><i>1.79%</i></td> <td><i>2.59%</i></td> <td><strong>2.16%</strong></td> <td>Rápido</td>
  </tr>
  <tr>
    <td>Modelo para diferencia de goles</td> <td><i>0.84%</i></td> <td><i>0.73%</i></td> <td><i>1.26%</i></td> <td><strong>0.94%</strong></td>
    <td><i>2.65%</i></td> <td><i>1.85%</i></td> <td><i>3.01%</i></td> <td><strong>2.5%</strong></td> <td>Despacio (4-5 min)</td>
  </tr>
</table>

<br><br>
## <a name="instalacion">🛠 Instalación
1. Clonar el repositorio.
2. Instalar las dependencias desde `requirements.txt` con:
```bash
pip install -r requirements.txt
```

<br><br>
## <a name="uso">💡 Uso
1. Elija uno de los modelos en la carpeta `models`:
   - `Result` – predice el resultado del partido.
   - `Score` – predice el marcador exacto.
   - `Score_diff` – predice la diferencia de goles.
2. Para ejecutar el modelo:
   - Ejecutar `main.py` (`python main.py` desde la carpeta del modelo).
   - Abrir el archivo `.exe`.
3. Seleccione un campeonato de la carpeta `for_data` y mueva **solo este archivo** a la carpeta del modelo.
   Asegúrese de que haya **un único archivo .xlsx** en la carpeta.
4. Si usa datos personalizados, deben cumplir con estas condiciones:
   - No debe haber partidos donde un equipo marque más de 9.5 goles.
   - Los nombres de los equipos deben ser consistentes entre temporadas.
   - El formato del archivo debe coincidir con los ejemplos (resultados de partidos por pares).
     Fuentes confiables incluyen las páginas de Wikipedia de las ligas.
5. Después de la ejecución, se generará un archivo `probabilities.xlsx` en la carpeta `results`.
   **Se sobrescribirá en la siguiente ejecución**.

---
## <a name="autores">✍️ Autores (con un toque de humor)
- Desarrollador: Mikhail Vataman
- Comentarista y traductor: ChatGPT
- Analista: "Lo importante es interpretar correctamente los resultados"
- Publicidad: PFC CSKA
- Mi futbolista favorito: Esmir Bajraktarevic
- Hotel: Trivago

