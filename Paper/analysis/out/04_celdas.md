# Resultados — `04_celdas.sql`

## t1_edad

```sql
SELECT edad AS item, COUNT(*) AS freq
FROM v_participantes
WHERE clase_edad = 'en_rango_10_13'
GROUP BY edad ORDER BY edad;

-- T1.b  Gender × Freq  → Male 15, Female 10, Non-specified 0
```

|   item |   freq |
|-------:|-------:|
|     10 |      6 |
|     11 |     11 |
|     12 |      6 |
|     13 |      2 |

## t1_genero

```sql
SELECT
    SUM(genero_opcion = 'masculino')                       AS male,
    SUM(genero_opcion = 'femenino')                        AS female,
    SUM(genero_opcion IS NULL
        OR genero_opcion NOT IN ('masculino','femenino'))  AS non_specified
FROM v_participantes
WHERE clase_edad = 'en_rango_10_13';

-- T1.c  Total students → 25
```

|   male |   female |   non_specified |
|-------:|---------:|----------------:|
|     15 |       10 |               0 |

## t1_total

```sql
SELECT COUNT(*) AS total_students
FROM v_participantes WHERE clase_edad = 'en_rango_10_13';


-- ================== TABLA 2 — Data totals ============================

-- T2.1  Children → 25
```

|   total_students |
|-----------------:|
|               25 |

## t2_children

```sql
SELECT COUNT(DISTINCT estudiante_id) AS children FROM v_ms_pub;

-- T2.2  Sessions → 98
```

|   children |
|-----------:|
|         25 |

## t2_sessions

```sql
SELECT COUNT(*) AS sessions FROM v_ms_pub;

-- T2.3  Messages → 2738
```

|   sessions |
|-----------:|
|         98 |

## t2_messages

```sql
SELECT COUNT(*) AS messages FROM v_msg_pub;

-- T2.4  Child msg. → 1320
```

|   messages |
|-----------:|
|       2738 |

## t2_child_msg

```sql
SELECT COUNT(*) AS child_msg FROM v_msg_pub WHERE rol = 'nino';

-- T2.5  Bit msg. → 1418  (1320 del LLM + 98 mensajes de apertura)
```

|   child_msg |
|------------:|
|        1320 |

## t2_bit_msg

```sql
SELECT COUNT(*)                    AS bit_msg,
       SUM(es_apertura = 0)        AS generados_por_llm,
       SUM(es_apertura = 1)        AS apertura_del_sistema
FROM v_msg_pub WHERE rol = 'tutor';

-- T2.6  Exercises → 6  (proyecto_libre no es un ejercicio del catálogo)
```

|   bit_msg |   generados_por_llm |   apertura_del_sistema |
|----------:|--------------------:|-----------------------:|
|      1418 |                1320 |                     98 |

## t2_exercises

```sql
SELECT COUNT(DISTINCT juego_id) AS exercises
FROM v_ms_pub WHERE juego_id <> 'proyecto_libre';


-- ================== TABLA 2 — Per session (media ± SD) ===============

-- T2.7  Turns → 13.5 ± 13.5
```

|   exercises |
|------------:|
|           6 |

## t2_turns

```sql
SELECT ROUND(AVG(turnos), 1) AS media,
       ROUND(SQRT((SUM(turnos*turnos) - COUNT(*)*AVG(turnos)*AVG(turnos))
                  / (COUNT(*) - 1.0)), 1) AS sd
FROM v_ms_pub;

-- T2.8  Messages → 27.9 ± 27.1
```

|   media |   sd |
|--------:|-----:|
|    13.5 | 13.5 |

## t2_messages_ses

```sql
SELECT ROUND(AVG(mensajes), 1) AS media,
       ROUND(SQRT((SUM(mensajes*mensajes) - COUNT(*)*AVG(mensajes)*AVG(mensajes))
                  / (COUNT(*) - 1.0)), 1) AS sd
FROM v_ms_pub;

-- T2.9  Questions → 2.2 ± 2.7
```

|   media |   sd |
|--------:|-----:|
|    27.9 | 27.1 |

## t2_questions

```sql
SELECT ROUND(AVG(preguntas), 1) AS media,
       ROUND(SQRT((SUM(preguntas*preguntas) - COUNT(*)*AVG(preguntas)*AVG(preguntas))
                  / (COUNT(*) - 1.0)), 1) AS sd
FROM v_ms_pub;

-- T2.10 Duration (min) → 13.8 ± 13.9
```

|   media |   sd |
|--------:|-----:|
|     2.2 |  2.7 |

## t2_duration

```sql
SELECT ROUND(AVG(duracion_min), 1) AS media,
       ROUND(SQRT((SUM(duracion_min*duracion_min)
                   - COUNT(*)*AVG(duracion_min)*AVG(duracion_min))
                  / (COUNT(*) - 1.0)), 1) AS sd
FROM v_ms_pub;

-- T2.11 Blocks sugg. → 6.8 ± 7.6
```

|   media |   sd |
|--------:|-----:|
|    13.8 | 13.9 |

## t2_blocks

```sql
SELECT ROUND(AVG(bloques_sugeridos), 1) AS media,
       ROUND(SQRT((SUM(bloques_sugeridos*bloques_sugeridos)
                   - COUNT(*)*AVG(bloques_sugeridos)*AVG(bloques_sugeridos))
                  / (COUNT(*) - 1.0)), 1) AS sd
FROM v_ms_pub;


-- ================== TABLA 2 — Outcomes ===============================

-- T2.12-14  Closed / Abandoned / Active %  → 41.8 / 42.9 / 15.3
```

|   media |   sd |
|--------:|-----:|
|     6.8 |  7.6 |

## t2_outcomes

```sql
SELECT estado,
       COUNT(*)                                          AS n,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM v_ms_pub), 1) AS pct
FROM v_ms_pub
GROUP BY estado ORDER BY n DESC;

-- T2.15 Satisf. (1-5) → 3.9 ± 1.2  (sobre las 60 sesiones con feedback)
```

| estado     |   n |   pct |
|:-----------|----:|------:|
| abandonada |  42 |  42.9 |
| cerrada    |  41 |  41.8 |
| activa     |  15 |  15.3 |

## t2_satisf

```sql
SELECT COUNT(*) AS n_con_feedback,
       ROUND(AVG(nivel_satisfaccion), 1) AS media,
       ROUND(SQRT((SUM(nivel_satisfaccion*nivel_satisfaccion)
                   - COUNT(*)*AVG(nivel_satisfaccion)*AVG(nivel_satisfaccion))
                  / (COUNT(*) - 1.0)), 1) AS sd
FROM v_ms_pub WHERE nivel_satisfaccion IS NOT NULL;


-- ================== TABLA 2 — bloque «Per session» completo ==========
-- Devuelve las 5 filas ya formateadas como "media ± SD", en el mismo
-- orden en que aparecen en la tabla del paper.
```

|   n_con_feedback |   media |   sd |
|-----------------:|--------:|-----:|
|               60 |     3.9 |  1.2 |

## t2_per_session_todas

```sql
SELECT 1 AS ord, 'Turns' AS celda,
       ROUND(AVG(turnos),1) || ' ± ' ||
       ROUND(SQRT((SUM(turnos*turnos) - COUNT(*)*AVG(turnos)*AVG(turnos))
                  / (COUNT(*)-1.0)),1)                       AS valor,
       COUNT(*) AS n
FROM v_ms_pub
UNION ALL
SELECT 2, 'Messages',
       ROUND(AVG(mensajes),1) || ' ± ' ||
       ROUND(SQRT((SUM(mensajes*mensajes) - COUNT(*)*AVG(mensajes)*AVG(mensajes))
                  / (COUNT(*)-1.0)),1),
       COUNT(*)
FROM v_ms_pub
UNION ALL
SELECT 3, 'Questions',
       ROUND(AVG(preguntas),1) || ' ± ' ||
       ROUND(SQRT((SUM(preguntas*preguntas) - COUNT(*)*AVG(preguntas)*AVG(preguntas))
                  / (COUNT(*)-1.0)),1),
       COUNT(*)
FROM v_ms_pub
UNION ALL
SELECT 4, 'Duration (min)',
       ROUND(AVG(duracion_min),1) || ' ± ' ||
       ROUND(SQRT((SUM(duracion_min*duracion_min)
                   - COUNT(*)*AVG(duracion_min)*AVG(duracion_min))
                  / (COUNT(*)-1.0)),1),
       COUNT(*)
FROM v_ms_pub
UNION ALL
SELECT 5, 'Blocks sugg.',
       ROUND(AVG(bloques_sugeridos),1) || ' ± ' ||
       ROUND(SQRT((SUM(bloques_sugeridos*bloques_sugeridos)
                   - COUNT(*)*AVG(bloques_sugeridos)*AVG(bloques_sugeridos))
                  / (COUNT(*)-1.0)),1),
       COUNT(*)
FROM v_ms_pub
ORDER BY ord;
```

|   ord | celda          | valor       |   n |
|------:|:---------------|:------------|----:|
|     1 | Turns          | 13.5 ± 13.5 |  98 |
|     2 | Messages       | 27.9 ± 27.1 |  98 |
|     3 | Questions      | 2.2 ± 2.7   |  98 |
|     4 | Duration (min) | 13.8 ± 13.9 |  98 |
|     5 | Blocks sugg.   | 6.8 ± 7.6   |  98 |
