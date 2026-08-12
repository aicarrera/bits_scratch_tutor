# Resultados — `01_demografia.sql`

## padron

```sql
SELECT
    p.codigo_publico                                       AS codigo,
    COALESCE(p.nombre_completo, '(no recuperado)')         AS nombre,
    p.edad,
    p.genero_opcion                                        AS genero,
    SUM(s.jornada = 1)                                     AS j1,
    SUM(s.jornada = 2)                                     AS j2,
    SUM(s.jornada = 3)                                     AS j3,
    p.n_sesiones                                           AS sesiones,
    SUM(ms.mensajes)                                       AS mensajes,
    SUM(ms.turnos)                                         AS turnos,
    SUM(ms.preguntas)                                      AS preguntas,
    SUM(ms.estado = 'cerrada')                             AS cerradas,
    p.clase_edad,
    CASE WHEN p.clase_edad = 'en_rango_10_13'
         THEN 'cohorte publicada' ELSE 'excluido' END      AS uso
FROM v_participantes p
JOIN v_sesiones_estudio  s  ON s.estudiante_id = p.id
JOIN v_metricas_sesion   ms ON ms.sesion_id    = s.id
GROUP BY p.id
ORDER BY (p.clase_edad <> 'en_rango_10_13'), p.edad, p.codigo_publico;

-- ---------------------------------------------------------------------
-- Q1.2  Cobertura del dato "edad": cuántos participantes tienen edad
--       registrada y cuánta interacción aportan los que no la tienen.
--       (Justifica la decisión de filtrar o no por edad.)
-- ---------------------------------------------------------------------
```

| codigo           | nombre                            |   edad | genero    |   j1 |   j2 |   j3 |   sesiones |   mensajes |   turnos |   preguntas |   cerradas | clase_edad     | uso               |
|:-----------------|:----------------------------------|-------:|:----------|-----:|-----:|-----:|-----------:|-----------:|---------:|------------:|-----------:|:---------------|:------------------|
| leon-azul-13     | Andrés David Escalante Merchan    |     10 | masculino |    2 |    2 |    1 |          5 |         89 |       42 |          23 |          0 | en_rango_10_13 | cohorte publicada |
| leon-azul-14     | Alex Sean Freire Lirio            |     10 | masculino |    2 |    2 |    1 |          5 |        379 |      187 |           6 |          1 | en_rango_10_13 | cohorte publicada |
| leon-azul-17     | Billy Navas                       |     10 | masculino |    0 |    0 |    1 |          1 |         47 |       23 |           8 |          0 | en_rango_10_13 | cohorte publicada |
| leon-azul-25     | Keiler Antonio Ordoñez Mero       |     10 | masculino |    2 |    2 |    1 |          5 |        107 |       51 |          13 |          3 | en_rango_10_13 | cohorte publicada |
| leon-azul-28     | Angel Josue Quito Moreira         |     10 | masculino |    2 |    0 |    0 |          2 |         90 |       44 |           4 |          1 | en_rango_10_13 | cohorte publicada |
| tigre-rosado-1   | Yesli Acosta Delgado              |     10 | femenino  |    2 |    2 |    1 |          5 |         53 |       24 |           9 |          2 | en_rango_10_13 | cohorte publicada |
| leon-azul-1      | Ariel Estupiñan                   |     11 | masculino |    2 |    1 |    1 |          4 |        124 |       60 |          16 |          2 | en_rango_10_13 | cohorte publicada |
| leon-azul-11     | Jesús Delgado Medina              |     11 | masculino |    2 |    2 |    2 |          6 |         86 |       40 |           9 |          3 | en_rango_10_13 | cohorte publicada |
| leon-azul-15     | Jose Daniel Guananga Usca         |     11 | masculino |    3 |    2 |    1 |          6 |         74 |       34 |           8 |          3 | en_rango_10_13 | cohorte publicada |
| leon-azul-6      | Snayder Victor Arroyo Castro      |     11 | masculino |    1 |    2 |    0 |          3 |         51 |       24 |           2 |          2 | en_rango_10_13 | cohorte publicada |
| leon-azul-7      | Yeyder Sneyder Ayoví Angulo       |     11 | masculino |    2 |    1 |    1 |          4 |        200 |       98 |          12 |          3 | en_rango_10_13 | cohorte publicada |
| leon-azul-8      | Neymar Mateo Burbano Cuero        |     11 | masculino |    3 |    2 |    0 |          5 |         85 |       40 |           0 |          1 | en_rango_10_13 | cohorte publicada |
| leon-azul-9      | Fausto Cisneros                   |     11 | masculino |    3 |    2 |    1 |          6 |         64 |       29 |           6 |          5 | en_rango_10_13 | cohorte publicada |
| tigre-rosado-12  | Brittany Noelia Guerrero Quiñonez |     11 | femenino  |    2 |    0 |    1 |          3 |        119 |       58 |           1 |          0 | en_rango_10_13 | cohorte publicada |
| tigre-rosado-23  | Yahnia Valeska Quiñonez Rodriguez |     11 | femenino  |    3 |    1 |    0 |          4 |         54 |       25 |           5 |          2 | en_rango_10_13 | cohorte publicada |
| tigre-rosado-3   | Hillary Masacón                   |     11 | femenino  |    2 |    3 |    0 |          5 |        203 |       99 |          14 |          3 | en_rango_10_13 | cohorte publicada |
| tigre-rosado-8   | Scarlett Catalina Canga Vasconez  |     11 | femenino  |    3 |    0 |    0 |          3 |         77 |       37 |           5 |          1 | en_rango_10_13 | cohorte publicada |
| leon-azul-3      | Edgar Eliazar Escalante Merchán   |     12 | masculino |    1 |    2 |    3 |          6 |        100 |       47 |           2 |          1 | en_rango_10_13 | cohorte publicada |
| leon-azul-33     | Isaac Zambrano Figueroa           |     12 | masculino |    3 |    2 |    1 |          6 |        262 |      128 |          20 |          2 | en_rango_10_13 | cohorte publicada |
| tigre-rosado-25  | Michelle Elisabe Quito Moreira    |     12 | femenino  |    2 |    0 |    0 |          2 |         86 |       42 |           0 |          2 | en_rango_10_13 | cohorte publicada |
| tigre-rosado-7   | Emely Nazareno                    |     12 | femenino  |    0 |    0 |    1 |          1 |         95 |       47 |           8 |          0 | en_rango_10_13 | cohorte publicada |
| tigre-rosado-8b  | Valentina Jimenez                 |     12 | femenino  |    0 |    1 |    0 |          1 |         45 |       22 |           2 |          0 | en_rango_10_13 | cohorte publicada |
| tigre-rosado-9   | Johana Mina                       |     12 | femenino  |    0 |    0 |    1 |          1 |         31 |       15 |           3 |          0 | en_rango_10_13 | cohorte publicada |
| leon-azul-16     | Juan Ángel Guerrero Quiñonez      |     13 | masculino |    2 |    0 |    1 |          3 |         73 |       35 |          16 |          0 | en_rango_10_13 | cohorte publicada |
| tigre-rosado-19  | Madison Elisa Ordoñez Mero        |     13 | femenino  |    2 |    3 |    1 |          6 |        144 |       69 |          21 |          4 | en_rango_10_13 | cohorte publicada |
| tigre-rosado-11  | (no recuperado)                   |    nan | femenino  |    0 |    0 |    1 |          1 |         25 |       12 |           4 |          1 | no_registrada  | excluido          |
| leon-azul-2      | Dustin Zapata                     |     16 | masculino |    1 |    0 |    0 |          1 |         19 |        9 |           5 |          1 | fuera_de_rango | excluido          |
| tigre-rosado-25b | Danna Almeida                     |     16 | femenino  |    0 |    2 |    0 |          2 |         20 |        9 |           2 |          0 | fuera_de_rango | excluido          |

## cobertura_edad

```sql
SELECT
    p.clase_edad,
    COUNT(*)                                             AS ninos,
    SUM(p.n_sesiones)                                    AS sesiones,
    (SELECT COUNT(*) FROM v_msg_estudio m
      WHERE m.estudiante_id IN (SELECT id FROM v_participantes p2
                                 WHERE p2.clase_edad = p.clase_edad)) AS mensajes
FROM v_participantes p
GROUP BY p.clase_edad
ORDER BY ninos DESC;

-- ---------------------------------------------------------------------
-- Q1.3  TABLA 1 — distribución de edad (todos los participantes)
-- ---------------------------------------------------------------------
```

| clase_edad     |   ninos |   sesiones |   mensajes |
|:---------------|--------:|-----------:|-----------:|
| en_rango_10_13 |      25 |         98 |       2738 |
| fuera_de_rango |       2 |          3 |         39 |
| no_registrada  |       1 |          1 |         25 |

## tabla1_edad

```sql
SELECT
    COALESCE(CAST(p.edad AS TEXT), 'No registrada')      AS item,
    COUNT(*)                                             AS freq,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM v_participantes), 1) AS pct
FROM v_participantes p
GROUP BY p.edad
ORDER BY (p.edad IS NULL), p.edad;

-- ---------------------------------------------------------------------
-- Q1.4  TABLA 1 — distribución de género (todos los participantes)
-- ---------------------------------------------------------------------
```

| item          |   freq |   pct |
|:--------------|-------:|------:|
| 10            |      6 |  21.4 |
| 11            |     11 |  39.3 |
| 12            |      6 |  21.4 |
| 13            |      2 |   7.1 |
| 16            |      2 |   7.1 |
| No registrada |      1 |   3.6 |

## tabla1_genero

```sql
SELECT
    CASE p.genero_opcion
        WHEN 'masculino'         THEN 'Male'
        WHEN 'femenino'          THEN 'Female'
        WHEN 'otro'              THEN 'Other'
        WHEN 'prefiero_no_decir' THEN 'Non-specified'
        ELSE 'Non-specified'
    END                                                  AS item,
    COUNT(*)                                             AS freq,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM v_participantes), 1) AS pct
FROM v_participantes p
GROUP BY 1
ORDER BY freq DESC;

-- ---------------------------------------------------------------------
-- Q1.5  TABLA 1 — edad × género cruzados (versión que se publica)
-- ---------------------------------------------------------------------
```

| item   |   freq |   pct |
|:-------|-------:|------:|
| Male   |     16 |  57.1 |
| Female |     12 |  42.9 |

## tabla1_cruce

```sql
SELECT
    COALESCE(CAST(p.edad AS TEXT), 'No registrada')      AS edad,
    SUM(p.genero_opcion = 'masculino')                   AS masculino,
    SUM(p.genero_opcion = 'femenino')                    AS femenino,
    SUM(p.genero_opcion NOT IN ('masculino','femenino')
        OR p.genero_opcion IS NULL)                      AS otro_ns,
    COUNT(*)                                             AS total
FROM v_participantes p
GROUP BY p.edad
ORDER BY (p.edad IS NULL), p.edad;

-- ---------------------------------------------------------------------
-- Q1.6  Estadísticos de edad (solo con edad registrada)
-- ---------------------------------------------------------------------
```

| edad          |   masculino |   femenino |   otro_ns |   total |
|:--------------|------------:|-----------:|----------:|--------:|
| 10            |           5 |          1 |         0 |       6 |
| 11            |           7 |          4 |         0 |      11 |
| 12            |           2 |          4 |         0 |       6 |
| 13            |           1 |          1 |         0 |       2 |
| 16            |           1 |          1 |         0 |       2 |
| No registrada |           0 |          1 |         0 |       1 |

## edad_stats

```sql
SELECT
    COUNT(*)                                             AS n_con_edad,
    MIN(edad)                                            AS edad_min,
    MAX(edad)                                            AS edad_max,
    ROUND(AVG(edad), 2)                                  AS media,
    ROUND(
        SQRT( (SUM(edad * edad) - COUNT(*) * AVG(edad) * AVG(edad))
              / (COUNT(*) - 1.0) ), 2)                   AS sd,
    SUM(edad BETWEEN 10 AND 13)                          AS en_rango_10_13,
    SUM(edad NOT BETWEEN 10 AND 13)                      AS fuera_de_rango
FROM v_participantes
WHERE edad IS NOT NULL;

-- ---------------------------------------------------------------------
-- Q1.7  Mediana de edad (SQLite no trae percentile())
-- ---------------------------------------------------------------------
```

|   n_con_edad |   edad_min |   edad_max |   media |   sd |   en_rango_10_13 |   fuera_de_rango |
|-------------:|-----------:|-----------:|--------:|-----:|-----------------:|-----------------:|
|           27 |         10 |         16 |   11.52 | 1.55 |               25 |                2 |

## edad_mediana

```sql
SELECT AVG(edad) AS mediana
FROM (SELECT edad FROM v_participantes WHERE edad IS NOT NULL
      ORDER BY edad
      LIMIT 2 - (SELECT COUNT(*) FROM v_participantes WHERE edad IS NOT NULL) % 2
      OFFSET (SELECT (COUNT(*) - 1) / 2
              FROM v_participantes WHERE edad IS NOT NULL));

-- ---------------------------------------------------------------------
-- Q1.8  Asistencia por jornada (cuántos niños distintos cada sábado)
-- ---------------------------------------------------------------------
```

|   mediana |
|----------:|
|        11 |

## asistencia

```sql
SELECT
    s.jornada,
    s.fecha_local                                        AS fecha,
    COUNT(DISTINCT s.estudiante_id)                      AS ninos,
    COUNT(*)                                             AS sesiones,
    MIN(s.inicio_local)                                  AS primera_sesion,
    MAX(s.inicio_local)                                  AS ultima_sesion
FROM v_sesiones_estudio s
GROUP BY s.jornada, s.fecha_local
ORDER BY s.jornada;

-- ---------------------------------------------------------------------
-- Q1.9  ¿Cuántos niños asistieron a 1, 2 o 3 jornadas?
-- ---------------------------------------------------------------------
```

|   jornada | fecha      |   ninos |   sesiones | primera_sesion      | ultima_sesion       |
|----------:|:-----------|--------:|-----------:|:--------------------|:--------------------|
|         1 | 2026-07-11 |      22 |         47 | 2026-07-11 09:52:37 | 2026-07-11 11:48:29 |
|         2 | 2026-07-18 |      18 |         34 | 2026-07-18 09:33:53 | 2026-07-18 11:42:49 |
|         3 | 2026-08-01 |      18 |         21 | 2026-08-01 11:17:54 | 2026-08-01 11:39:12 |

## jornadas_por_nino

```sql
SELECT n_jornadas, COUNT(*) AS ninos
FROM v_participantes
GROUP BY n_jornadas
ORDER BY n_jornadas;
```

|   n_jornadas |   ninos |
|-------------:|--------:|
|            1 |      10 |
|            2 |       6 |
|            3 |      12 |
