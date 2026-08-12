# Informe: cómo se completan las Tablas 1 y 2

Cada número del paper con la consulta exacta que lo produce.

**Cohorte publicada: 25 niños/as de 10 a 13 años, 98 sesiones, 2 738 mensajes.**
Todo en este documento sale de esa población — no hay ninguna cifra calculada
sobre otra.

| | |
|---|---|
| Base | `creabits_paper.db`, reconstruida del backup `db_cluster-09-08-2026@21-16-40.backup` |
| Reproducir | `python build_sqlite.py && python run_queries.py` |
| Consultas por celda | [`sql/04_celdas.sql`](sql/04_celdas.sql) — una por número publicado |
| Detalle metodológico | [`ANALISIS.md`](ANALISIS.md) |

---

## 1. Los 25 estudiantes

`j1` = 11/07, `j2` = 18/07, `j3` = 01/08 (sesiones abiertas ese día).

| # | Código | Nombre | Edad | G | j1 | j2 | j3 | Ses. | Msgs | Turnos | Preg. | Cerr. |
|---:|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | leon-azul-13 | Andrés David Escalante Merchan | 10 | M | 2 | 2 | 1 | 5 | 89 | 42 | 23 | 0 |
| 2 | leon-azul-14 | Alex Sean Freire Lirio | 10 | M | 2 | 2 | 1 | 5 | 379 | 187 | 6 | 1 |
| 3 | leon-azul-17 | Billy Navas | 10 | M | 0 | 0 | 1 | 1 | 47 | 23 | 8 | 0 |
| 4 | leon-azul-25 | Keiler Antonio Ordoñez Mero | 10 | M | 2 | 2 | 1 | 5 | 107 | 51 | 13 | 3 |
| 5 | leon-azul-28 | Angel Josue Quito Moreira | 10 | M | 2 | 0 | 0 | 2 | 90 | 44 | 4 | 1 |
| 6 | tigre-rosado-1 | Yesli Acosta Delgado | 10 | F | 2 | 2 | 1 | 5 | 53 | 24 | 9 | 2 |
| 7 | leon-azul-1 | Ariel Estupiñan | 11 | M | 2 | 1 | 1 | 4 | 124 | 60 | 16 | 2 |
| 8 | leon-azul-11 | Jesús Delgado Medina | 11 | M | 2 | 2 | 2 | 6 | 86 | 40 | 9 | 3 |
| 9 | leon-azul-15 | Jose Daniel Guananga Usca | 11 | M | 3 | 2 | 1 | 6 | 74 | 34 | 8 | 3 |
| 10 | leon-azul-6 | Snayder Victor Arroyo Castro | 11 | M | 1 | 2 | 0 | 3 | 51 | 24 | 2 | 2 |
| 11 | leon-azul-7 | Yeyder Sneyder Ayoví Angulo | 11 | M | 2 | 1 | 1 | 4 | 200 | 98 | 12 | 3 |
| 12 | leon-azul-8 | Neymar Mateo Burbano Cuero | 11 | M | 3 | 2 | 0 | 5 | 85 | 40 | 0 | 1 |
| 13 | leon-azul-9 | Fausto Cisneros | 11 | M | 3 | 2 | 1 | 6 | 64 | 29 | 6 | 5 |
| 14 | tigre-rosado-12 | Brittany Noelia Guerrero Quiñonez | 11 | F | 2 | 0 | 1 | 3 | 119 | 58 | 1 | 0 |
| 15 | tigre-rosado-23 | Yahnia Valeska Quiñonez Rodriguez | 11 | F | 3 | 1 | 0 | 4 | 54 | 25 | 5 | 2 |
| 16 | tigre-rosado-3 | Hillary Masacón | 11 | F | 2 | 3 | 0 | 5 | 203 | 99 | 14 | 3 |
| 17 | tigre-rosado-8 | Scarlett Catalina Canga Vasconez | 11 | F | 3 | 0 | 0 | 3 | 77 | 37 | 5 | 1 |
| 18 | leon-azul-3 | Edgar Eliazar Escalante Merchán | 12 | M | 1 | 2 | 3 | 6 | 100 | 47 | 2 | 1 |
| 19 | leon-azul-33 | Isaac Zambrano Figueroa | 12 | M | 3 | 2 | 1 | 6 | 262 | 128 | 20 | 2 |
| 20 | tigre-rosado-25 | Michelle Elisabe Quito Moreira | 12 | F | 2 | 0 | 0 | 2 | 86 | 42 | 0 | 2 |
| 21 | tigre-rosado-7 | Emely Nazareno | 12 | F | 0 | 0 | 1 | 1 | 95 | 47 | 8 | 0 |
| 22 | tigre-rosado-8b | Valentina Jimenez | 12 | F | 0 | 1 | 0 | 1 | 45 | 22 | 2 | 0 |
| 23 | tigre-rosado-9 | Johana Mina | 12 | F | 0 | 0 | 1 | 1 | 31 | 15 | 3 | 0 |
| 24 | leon-azul-16 | Juan Ángel Guerrero Quiñonez | 13 | M | 2 | 0 | 1 | 3 | 73 | 35 | 16 | 0 |
| 25 | tigre-rosado-19 | Madison Elisa Ordoñez Mero | 13 | F | 2 | 3 | 1 | 6 | 144 | 69 | 21 | 4 |
| | | **Total** | | **15 M / 10 F** | | | | **98** | **2 738** | **1 320** | **213** | **41** |

<details><summary><b>Consulta</b> (<code>Q1.1 padron</code>)</summary>

```sql
SELECT
    p.codigo_publico                                AS codigo,
    COALESCE(p.nombre_completo, '(no recuperado)')  AS nombre,
    p.edad,
    p.genero_opcion                                 AS genero,
    SUM(s.jornada = 1)                              AS j1,   -- 11/07
    SUM(s.jornada = 2)                              AS j2,   -- 18/07
    SUM(s.jornada = 3)                              AS j3,   -- 01/08
    p.n_sesiones                                    AS sesiones,
    SUM(ms.mensajes)                                AS mensajes,
    SUM(ms.turnos)                                  AS turnos,
    SUM(ms.preguntas)                               AS preguntas,
    SUM(ms.estado = 'cerrada')                      AS cerradas
FROM v_participantes p
JOIN v_sesiones_estudio s  ON s.estudiante_id = p.id
JOIN v_metricas_sesion  ms ON ms.sesion_id    = s.id
WHERE p.clase_edad = 'en_rango_10_13'
GROUP BY p.id
ORDER BY p.edad, p.codigo_publico;
```
</details>

### Quiénes quedan fuera (y por qué)

28 niños/as usaron a Bit. Estos 3 no entran en la cohorte publicada; aportan
4 sesiones y 64 mensajes (**2.3 % del corpus**):

| Código | Nombre | Edad | G | Ses. | Motivo |
|---|---|---|---|---:|---|
| leon-azul-2 | Dustin Zapata | 16 | M | 1 | fuera del rango 10–13 que declara el paper |
| tigre-rosado-25b | Danna Almeida | 16 | F | 2 | fuera del rango 10–13 |
| tigre-rosado-11 | (no recuperado) | — | F | 1 | no aparece en la hoja de asistencia; edad no verificable |

También se excluyen del alcance, antes de llegar aquí: el grupo *CreaBits
Demo* (`tigre-azul-7`, `demo-ia-1`, `leon-rojo-3` — 28 sesiones de prueba del
equipo) y las cuentas `voluntario-1…10` (10 sesiones del piloto).

### De dónde salen las edades

La base tenía 7 de 28 edades vacías. La hoja de asistencia en papel cerró 6:
`tigre-rosado-1` (Yesli, 10), `tigre-rosado-19` (Madison, 13),
`tigre-rosado-25` (Michelle, 12), `leon-azul-17` (Billy, 10),
`tigre-rosado-7` (Emely, 12) y `tigre-rosado-9` (Johana, 12). Se aplican en
[`sql/00a_hoja_asistencia.sql`](sql/00a_hoja_asistencia.sql).

La hoja es fiable: **23 puntos de control, cero contradicciones** — las 21
edades que ya estaban coinciden una a una, y las dos reasignaciones anotadas
por el equipo (`tigre-rosado-8b` Valentina 12, `tigre-rosado-25b` Danna 16)
aparecen con el mismo nombre y edad.

---

## 2. Cómo se completa la TABLA 1 (demografía)

| Attribute | Item | Freq | Attribute | Item | Freq |
|---|---|---:|---|---|---:|
| Age | 10 | 6 | Gender | Male | 15 |
| | 11 | 11 | | Female | 10 |
| | 12 | 6 | | Non-specified | 0 |
| | 13 | 2 | | | |
| **Total students** | | **25** | | | |

Es un conteo directo sobre `v_participantes` filtrando `clase_edad`. Nada
más: no hay ponderaciones ni imputaciones.

| Celda | Valor | Consulta |
|---|---|---|
| Age × Freq | 6 / 11 / 6 / 2 | `SELECT edad AS item, COUNT(*) AS freq FROM v_participantes WHERE clase_edad='en_rango_10_13' GROUP BY edad ORDER BY edad;` |
| Gender × Freq | 15 / 10 / 0 | `SELECT SUM(genero_opcion='masculino') AS male, SUM(genero_opcion='femenino') AS female, SUM(genero_opcion IS NULL OR genero_opcion NOT IN ('masculino','femenino')) AS non_specified FROM v_participantes WHERE clase_edad='en_rango_10_13';` |
| Total students | 25 | `SELECT COUNT(*) FROM v_participantes WHERE clase_edad='en_rango_10_13';` |

> Esta tabla es **idéntica** a la que ya tenía el borrador. Se construyó a
> partir de la misma hoja de asistencia, restringida a 10–13 años. Lo único
> que había que ajustar era el texto que la introduce: 28 niños usaron el
> tutor, de los cuales estos 25 forman la cohorte de análisis.

---

## 3. Cómo se completa la TABLA 2 (corpus de interacción)

| Data totals | | Per session | | Outcomes | |
|---|---:|---|---:|---|---:|
| Children | 25 | Turns | 13.5 ± 13.5 | Closed % | 41.8 |
| Sessions | 98 | Messages | 27.9 ± 27.1 | Abandoned % | 42.9 |
| Messages | 2 738 | Questions | 2.2 ± 2.7 | Active % | 15.3 |
| Child msg. | 1 320 | Duration (min) | 13.8 ± 13.9 | Satisf. (1–5) | 3.9 ± 1.2 |
| Bit msg. | 1 418 | Blocks sugg. | 6.8 ± 7.6 | | |
| Exercises | 6 | | | | |

Los valores por sesión son media ± SD muestral (denominador n−1), sobre las
98 sesiones.

### 3.1 Data totals

| Celda | Valor | Consulta |
|---|---:|---|
| **Children** | 25 | `SELECT COUNT(DISTINCT estudiante_id) FROM v_ms_pub;` |
| **Sessions** | 98 | `SELECT COUNT(*) FROM v_ms_pub;` |
| **Messages** | 2 738 | `SELECT COUNT(*) FROM v_msg_pub;` |
| **Child msg.** | 1 320 | `SELECT COUNT(*) FROM v_msg_pub WHERE rol='nino';` |
| **Bit msg.** | 1 418 | `SELECT COUNT(*) FROM v_msg_pub WHERE rol='tutor';` |
| **Exercises** | 6 | `SELECT COUNT(DISTINCT juego_id) FROM v_ms_pub WHERE juego_id <> 'proyecto_libre';` |

Dos aclaraciones que hay que declarar en el paper:

- **`Bit msg.` = 1 320 respuestas del LLM + 98 mensajes de apertura.** El
  sistema siembra un mensaje `instruccion_nino` al abrir cada conversación
  (`proveedor_llm='system'`). Se cuenta porque el niño lo ve como un mensaje
  de Bit, y así `Child msg. + Bit msg. = Messages` cuadra exactamente.
  El desglose:
  ```sql
  SELECT COUNT(*) AS bit_msg, SUM(es_apertura=0) AS generados_por_llm,
         SUM(es_apertura=1) AS apertura_del_sistema
  FROM v_msg_pub WHERE rol='tutor';   -- 1418 | 1320 | 98
  ```
- **`Exercises` = 6**, los del catálogo (`ej_001`…`ej_006`). Dos sesiones más
  usaron *Proyecto libre*, que no es un ejercicio y no se cuenta. El borrador
  decía "4 exercises".

### 3.2 Per session

Las cinco consultas, cada una devuelve su celda. `n = 98` en todas.

```sql
-- Turns → 13.5 ± 13.5
SELECT ROUND(AVG(turnos), 1) AS media,
       ROUND(SQRT((SUM(turnos*turnos) - COUNT(*)*AVG(turnos)*AVG(turnos))
                  / (COUNT(*) - 1.0)), 1) AS sd
FROM v_ms_pub;

-- Messages → 27.9 ± 27.1
SELECT ROUND(AVG(mensajes), 1) AS media,
       ROUND(SQRT((SUM(mensajes*mensajes) - COUNT(*)*AVG(mensajes)*AVG(mensajes))
                  / (COUNT(*) - 1.0)), 1) AS sd
FROM v_ms_pub;

-- Questions → 2.2 ± 2.7
SELECT ROUND(AVG(preguntas), 1) AS media,
       ROUND(SQRT((SUM(preguntas*preguntas) - COUNT(*)*AVG(preguntas)*AVG(preguntas))
                  / (COUNT(*) - 1.0)), 1) AS sd
FROM v_ms_pub;

-- Duration (min) → 13.8 ± 13.9
SELECT ROUND(AVG(duracion_min), 1) AS media,
       ROUND(SQRT((SUM(duracion_min*duracion_min)
                   - COUNT(*)*AVG(duracion_min)*AVG(duracion_min))
                  / (COUNT(*) - 1.0)), 1) AS sd
FROM v_ms_pub;

-- Blocks sugg. → 6.8 ± 7.6
SELECT ROUND(AVG(bloques_sugeridos), 1) AS media,
       ROUND(SQRT((SUM(bloques_sugeridos*bloques_sugeridos)
                   - COUNT(*)*AVG(bloques_sugeridos)*AVG(bloques_sugeridos))
                  / (COUNT(*) - 1.0)), 1) AS sd
FROM v_ms_pub;
```

O las cinco de una vez, ya formateadas como aparecen en la tabla
(`t2_per_session_todas` en [`sql/04_celdas.sql`](sql/04_celdas.sql)):

```sql
SELECT 1 AS ord, 'Turns' AS celda,
       ROUND(AVG(turnos),1) || ' ± ' ||
       ROUND(SQRT((SUM(turnos*turnos) - COUNT(*)*AVG(turnos)*AVG(turnos))
                  / (COUNT(*)-1.0)),1) AS valor, COUNT(*) AS n
FROM v_ms_pub
UNION ALL SELECT 2, 'Messages',
       ROUND(AVG(mensajes),1) || ' ± ' ||
       ROUND(SQRT((SUM(mensajes*mensajes) - COUNT(*)*AVG(mensajes)*AVG(mensajes))
                  / (COUNT(*)-1.0)),1), COUNT(*) FROM v_ms_pub
UNION ALL SELECT 3, 'Questions',
       ROUND(AVG(preguntas),1) || ' ± ' ||
       ROUND(SQRT((SUM(preguntas*preguntas) - COUNT(*)*AVG(preguntas)*AVG(preguntas))
                  / (COUNT(*)-1.0)),1), COUNT(*) FROM v_ms_pub
UNION ALL SELECT 4, 'Duration (min)',
       ROUND(AVG(duracion_min),1) || ' ± ' ||
       ROUND(SQRT((SUM(duracion_min*duracion_min)
                   - COUNT(*)*AVG(duracion_min)*AVG(duracion_min))
                  / (COUNT(*)-1.0)),1), COUNT(*) FROM v_ms_pub
UNION ALL SELECT 5, 'Blocks sugg.',
       ROUND(AVG(bloques_sugeridos),1) || ' ± ' ||
       ROUND(SQRT((SUM(bloques_sugeridos*bloques_sugeridos)
                   - COUNT(*)*AVG(bloques_sugeridos)*AVG(bloques_sugeridos))
                  / (COUNT(*)-1.0)),1), COUNT(*) FROM v_ms_pub
ORDER BY ord;
```

```
 ord   celda              valor          n
   1   Turns              13.5 ± 13.5    98
   2   Messages           27.9 ± 27.1    98
   3   Questions          2.2 ± 2.7      98
   4   Duration (min)     13.8 ± 13.9    98
   5   Blocks sugg.       6.8 ± 7.6      98
```

### De dónde sale el `±`

Es la **desviación estándar muestral entre las 98 sesiones**: cada sesión es
una observación, y se calculan media y SD sobre esas 98 cifras. SQLite no
trae `STDDEV()`, así que se usa la identidad algebraica de la varianza:

$$s=\\sqrt{\\frac{\\sum x_i^2-n\\bar{x}^2}{n-1}}\\quad\\longrightarrow\\quad
\\texttt{SQRT((SUM(x*x)-COUNT(*)*AVG(x)*AVG(x))/(COUNT(*)-1.0))}$$

El `-1.0` cumple dos funciones: fuerza división en coma flotante y es el
denominador *n−1* (corrección de Bessel), es decir SD **muestral**, no
poblacional. Verificado contra `numpy.std(ddof=1)`: las cinco columnas
coinciden hasta el último decimal.

| Columna | media | SD (fórmula SQL) | SD (numpy) |
|---|---:|---:|---:|
| `turnos` | 13.469 | 13.546 | 13.546 |
| `mensajes` | 27.939 | 27.092 | 27.092 |
| `preguntas` | 2.173 | 2.675 | 2.675 |
| `duracion_min` | 13.754 | 13.870 | 13.870 |
| `bloques_sugeridos` | 6.776 | 7.581 | 7.581 |

**La SD sale casi igual a la media porque la distribución está muy sesgada a
la derecha** (asimetría 1.4–2.2). Los 98 valores de `turnos` van de 0 a 64,
con 13 sesiones en 0 (se abrió el ejercicio y nunca se habló con Bit) y una
cola larga. La mediana es 9 frente a una media de 13.5. Alternativa por si se
prefiere reportar mediana e IQR (habría que cambiar el caption):

| Celda | media ± SD | mediana [IQR] |
|---|---:|---:|
| Turns | 13.5 ± 13.5 | 9.0 [3.0–21.0] |
| Messages | 27.9 ± 27.1 | 19.0 [7.0–43.0] |
| Questions | 2.2 ± 2.7 | 1.0 [0.0–3.0] |
| Duration (min) | 13.8 ± 13.9 | 10.8 [2.5–22.1] |
| Blocks sugg. | 6.8 ± 7.6 | 4.0 [1.2–10.0] |

Las cuatro decisiones metodológicas que hay detrás de esas columnas:

**`turnos` — un turno es un intercambio niño→Bit.** Cada mensaje del niño
recibe exactamente una respuesta del LLM (verificado: 1 320 = 1 320), así que
`turnos = mensajes del niño = respuestas del LLM`, y `Messages ≈ 2×turnos + 1`.

**`duracion_min` — NO es `fin_en − inicio_en`.** Una sesión queda abierta
hasta que el docente la cierra o el navegador dispara el beacon de abandono,
lo que da duraciones de hasta 46 155 min (32 días). Se mide como la suma, por
jornada, del lapso entre el primer y el último mensaje de esa sesión ese día
(4 sesiones continuaron en un sábado posterior tras ser reanudadas):

```sql
WITH span AS (
  SELECT sesion_id, fecha_local,
         (julianday(MAX(creado_utc)) - julianday(MIN(creado_utc))) * 1440.0 AS min_dia
  FROM v_msg_estudio GROUP BY sesion_id, fecha_local)
SELECT sesion_id, SUM(min_dia) AS duracion_min FROM span GROUP BY sesion_id;
```

**`preguntas` — no se pueden contar por signos de interrogación.** Los niños
solo usaron `?` o `¿` en 44 de 1 320 mensajes, y el **74.7 %** de lo que
escriben son toques en un chip de respuesta rápida, no texto propio. La
clasificación:

| Clase | n | % |
|---|---:|---:|
| Chip (coincide exacto con una `opciones_respuesta` del mensaje anterior de Bit) | 986 | 74.7 |
| Texto libre | 334 | 25.3 |
| └ **Petición de ayuda** → `Questions` | **213** | **16.1** |

`es_ayuda` marca un mensaje libre con: signo `?`/`¿`; interrogativo (`como`,
`que`, `cual`, `cuanto`, `donde`, `quien`, `por que`, con abreviaturas y
faltas típicas — `q`, `k`, `komo`, `xq`); petición explícita (`ayuda`,
`pista`, `dime`, `dame`, `muestrame`); señal de bloqueo (`no entiendo`,
`no se`, `no encuentro`, `no me sale`, `sigo sin`); objetivo dirigido a Bit
(`quiero que…`, `necesito…`); o petición del siguiente paso (`y ahora`,
`que mas`, `como empiezo`). Las 334 clasificaciones se revisaron a mano;
error residual estimado ~2 %. La definición completa está en
[`sql/00_scope.sql`](sql/00_scope.sql) (vista `v_msg_estudio`), y `Q3.5`
publica las variantes alternativas por si el revisor quiere recalcular.

**`bloques_sugeridos`** cuenta los bloques de Scratch que Bit propuso, ya
validados contra el catálogo oficial (los IDs desconocidos se descartan antes
de persistirse).

### 3.3 Outcomes

| Celda | Valor | Consulta |
|---|---:|---|
| **Closed %** | 41.8 (41 ses.) | `SELECT estado, COUNT(*) n, ROUND(100.0*COUNT(*)/(SELECT COUNT(*) FROM v_ms_pub),1) pct FROM v_ms_pub GROUP BY estado;` |
| **Abandoned %** | 42.9 (42 ses.) | ↑ misma consulta |
| **Active %** | 15.3 (15 ses.) | ↑ misma consulta |
| **Satisf. (1–5)** | 3.9 ± 1.2 | `SELECT COUNT(*), ROUND(AVG(nivel_satisfaccion),1), ROUND(SQRT((SUM(nivel_satisfaccion*nivel_satisfaccion)-COUNT(*)*AVG(nivel_satisfaccion)*AVG(nivel_satisfaccion))/(COUNT(*)-1.0)),1) FROM v_ms_pub WHERE nivel_satisfaccion IS NOT NULL;` |

- `cerrada` = un voluntario verificó la solución en Scratch y cerró la sesión.
- `abandonada` = el navegador reportó abandono o el niño cambió de ejercicio.
- `activa` = **no es "en curso"**: son sesiones que quedaron abiertas al
  terminar el taller. Conviene decirlo en la nota de la tabla.
- **Satisfacción sobre 60 de 98 sesiones (61.2 % de cobertura).** Distribución:
  1★ 3, 2★ 3, 3★ 17, 4★ 10, 5★ 27. Como las sesiones abandonadas en silencio
  no dejan feedback, el 3.9 es probablemente un techo optimista — vale la pena
  reconocerlo en Limitations.

---

## 4. Comprobaciones que conviene citar

**Sensibilidad a la exclusión de los 3** (`Q3.11`) — ningún valor se mueve
más de 1 punto porcentual:

| | Publicada (25) | Todos (28) |
|---|---:|---:|
| Sesiones | 98 | 102 |
| Mensajes | 2 738 | 2 802 |
| Closed % | 41.8 | 42.2 |
| Abandoned % | 42.9 | 42.2 |

**Sensibilidad a las sesiones vacías** (`Q3.9`) — 13 de las 98 sesiones se
abrieron sin llegar a ningún intercambio, y son la causa de las SD altas.
Excluyéndolas (n = 85): turnos 15.5 ± 13.4, duración 15.9 ± 13.7,
cerradas 42.4 %.

**Cifras que el borrador dejaba pendientes:**

| §Data Collection decía | Real |
|---|---|
| "[81, revisar!!!!] sessions" | **98** |
| "approximately [2,000, revisar!!!] messages" | **2 738** |
| "across 4 exercises" | **6 ejercicios** + proyecto libre |
| "three **consecutive** Saturday sessions" | 11/07, 18/07 y **01/08** — no son consecutivos, el 25/07 no hubo jornada |

---

## 5. LaTeX listo para pegar

Ya insertado en [`../sample.tex`](../sample.tex); copia de respaldo en
[`tablas_paper.tex`](tablas_paper.tex), que además trae comentada la variante
con los 28 niños/as por si se decide no excluir a nadie.

```latex
% ---------- TABLA 1 ----------
\begin{table}[t]
\centering
\caption{Demographic breakdown of the 25 children aged 10--13 who participated in the data collection phase.}
\label{tab:demographics}
\begin{tabular}{llr@{\hspace{2.5em}}llr}
\toprule
Attribute & Item & Freq & Attribute & Item & Freq \\
\midrule
Age & 10 & 6  & Gender & Male          & 15 \\
    & 11 & 11 &        & Female        & 10 \\
    & 12 & 6  &        & Non-specified & 0  \\
    & 13 & 2  &        &               &    \\
\midrule
\textbf{Total students} & & \textbf{25} & & & \\
\bottomrule
\end{tabular}
\end{table}

% ---------- TABLA 2 ----------
\begin{table}[ht]
\centering
\caption{Overview of the interaction data. Per-session values are mean\,$\pm$\,SD.}
\label{tab:corpus}
\footnotesize
\setlength{\tabcolsep}{4pt}
\begin{tabular}{lr@{\hskip 1.5em}lr@{\hskip 1.5em}lr}
\toprule
\multicolumn{2}{l}{\textit{Data totals}} &
\multicolumn{2}{l}{\textit{Per session}} &
\multicolumn{2}{l}{\textit{Outcomes}} \\
\cmidrule(r){1-2}\cmidrule(r){3-4}\cmidrule(r){5-6}
Children    & 25      & Turns          & 13.5 $\pm$ 13.5 & Closed \%      & 41.8 \\
Sessions    & 98      & Messages       & 27.9 $\pm$ 27.1 & Abandoned \%   & 42.9 \\
Messages    & 2{,}738 & Questions      & 2.2 $\pm$ 2.7   & Active \%      & 15.3 \\
Child msg.  & 1{,}320 & Duration (min) & 13.8 $\pm$ 13.9 & Satisf. (1--5) & 3.9 $\pm$ 1.2 \\
Bit msg.    & 1{,}418 & Blocks sugg.   & 6.8 $\pm$ 7.6   &                &    \\
Exercises   & 6       &                &                 &                &    \\
\bottomrule
\end{tabular}
\end{table}
```
