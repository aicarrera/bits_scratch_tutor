# Resultados — `03_contexto.sql`

## por_ejercicio

```sql
SELECT
    ms.juego_id,
    j.titulo,
    COUNT(*)                                              AS sesiones,
    COUNT(DISTINCT ms.estudiante_id)                      AS ninos,
    SUM(ms.estado = 'cerrada')                            AS cerradas,
    ROUND(100.0 * SUM(ms.estado = 'cerrada') / COUNT(*), 1) AS pct_cerradas,
    SUM(ms.estado = 'abandonada')                         AS abandonadas,
    ROUND(100.0 * SUM(ms.estado = 'abandonada') / COUNT(*), 1) AS pct_abandonadas,
    ROUND(AVG(ms.turnos), 1)                              AS turnos_media,
    ROUND(AVG(ms.duracion_min), 1)                        AS dur_media,
    ROUND(AVG(ms.preguntas), 1)                           AS preguntas_media
FROM v_ms_pub ms
JOIN juegos j ON j.id = ms.juego_id
GROUP BY ms.juego_id, j.titulo
ORDER BY sesiones DESC;

-- ---------------------------------------------------------------------
-- Q3.2  Por jornada (sábado)
-- ---------------------------------------------------------------------
```

| juego_id       | titulo                     |   sesiones |   ninos |   cerradas |   pct_cerradas |   abandonadas |   pct_abandonadas |   turnos_media |   dur_media |   preguntas_media |
|:---------------|:---------------------------|-----------:|--------:|-----------:|---------------:|--------------:|------------------:|---------------:|------------:|------------------:|
| ej_001         | Haz bailar al gato         |         24 |      21 |          8 |           33.3 |            14 |              58.3 |           19.2 |        21.6 |               2.6 |
| ej_002         | Mariposa cambia de disfraz |         20 |      19 |         12 |           60   |             5 |              25   |            6.5 |         6.1 |               1.1 |
| ej_003         | Atrapa la estrella         |         19 |      18 |          6 |           31.6 |             9 |              47.4 |           19.8 |        22.9 |               4.7 |
| ej_006         | Historia con escenarios    |         18 |      18 |         13 |           72.2 |             2 |              11.1 |           14.3 |         9.6 |               1.2 |
| ej_005         | Diálogo entre personajes   |         14 |      14 |          2 |           14.3 |            11 |              78.6 |            5.4 |         6.6 |               1   |
| proyecto_libre | Proyecto libre             |          2 |       2 |          0 |            0   |             0 |               0   |            5.5 |         1.4 |               1   |
| ej_004         | Salta obstáculos           |          1 |       1 |          0 |            0   |             1 |             100   |            7   |         5.6 |               2   |

## por_jornada

```sql
SELECT
    ms.jornada, ms.fecha_local,
    COUNT(DISTINCT ms.estudiante_id)                      AS ninos,
    COUNT(*)                                              AS sesiones,
    SUM(ms.mensajes)                                      AS mensajes,
    SUM(ms.turnos)                                        AS turnos,
    SUM(ms.preguntas)                                     AS preguntas,
    ROUND(AVG(ms.duracion_min), 1)                        AS dur_media,
    ROUND(100.0 * SUM(ms.estado = 'cerrada') / COUNT(*), 1) AS pct_cerradas
FROM v_ms_pub ms
GROUP BY ms.jornada, ms.fecha_local
ORDER BY ms.jornada;

-- ---------------------------------------------------------------------
-- Q3.3  Fase pedagógica de las respuestas de Bit
--       (predecir → pista → confirmar → responder; alimenta RQ4)
-- ---------------------------------------------------------------------
```

|   jornada | fecha_local   |   ninos |   sesiones |   mensajes |   turnos |   preguntas |   dur_media |   pct_cerradas |
|----------:|:--------------|--------:|-----------:|-----------:|---------:|------------:|------------:|---------------:|
|         1 | 2026-07-11    |      21 |         46 |       1248 |      601 |          85 |        13.9 |           43.5 |
|         2 | 2026-07-18    |      17 |         32 |        744 |      356 |          44 |         9.2 |           50   |
|         3 | 2026-08-01    |      17 |         20 |        746 |      363 |          84 |        20.6 |           25   |

## fases

```sql
SELECT
    COALESCE(fase, '(apertura del sistema)')              AS fase,
    COUNT(*)                                              AS n,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1)    AS pct,
    ROUND(AVG(n_bloques), 2)                              AS bloques_media,
    ROUND(AVG(n_opciones), 2)                             AS opciones_media
FROM v_msg_pub
WHERE rol = 'tutor'
GROUP BY fase
ORDER BY n DESC;

-- ---------------------------------------------------------------------
-- Q3.4  Cómo responde el niño: chip vs texto libre vs petición de ayuda
--       (alimenta el principio "Child-friendly interaction" y RQ1)
-- ---------------------------------------------------------------------
```

| fase                   |   n |   pct |   bloques_media |   opciones_media |
|:-----------------------|----:|------:|----------------:|-----------------:|
| pista                  | 664 |  46.8 |            0.21 |             2.97 |
| predecir               | 406 |  28.6 |            0.94 |             3    |
| confirmar              | 148 |  10.4 |            0.95 |             2.45 |
| (apertura del sistema) |  98 |   6.9 |            0    |             0    |
| responder              |  98 |   6.9 |            0.03 |             2.26 |
| necesita_aclaracion    |   4 |   0.3 |            0    |             3    |

## modo_respuesta_nino

```sql
SELECT
    COUNT(*)                                              AS msg_nino,
    SUM(es_chip)                                          AS con_chip,
    ROUND(100.0 * SUM(es_chip) / COUNT(*), 1)             AS pct_chip,
    SUM(es_libre)                                         AS texto_libre,
    ROUND(100.0 * SUM(es_libre) / COUNT(*), 1)            AS pct_libre,
    SUM(es_ayuda)                                         AS peticiones_ayuda,
    ROUND(100.0 * SUM(es_ayuda) / COUNT(*), 1)            AS pct_ayuda,
    ROUND(AVG(n_palabras), 2)                             AS palabras_media
FROM v_msg_pub
WHERE rol = 'nino';

-- ---------------------------------------------------------------------
-- Q3.5  Definiciones alternativas de "Questions" (transparencia)
--   marca_signo  = contiene '?' o '¿'
--   libre        = escrito a mano (no chip)
--   ayuda        = libre + léxico de pregunta/ayuda  ← la que se publica
-- ---------------------------------------------------------------------
```

|   msg_nino |   con_chip |   pct_chip |   texto_libre |   pct_libre |   peticiones_ayuda |   pct_ayuda |   palabras_media |
|-----------:|-----------:|-----------:|--------------:|------------:|-------------------:|------------:|-----------------:|
|       1320 |        986 |       74.7 |           334 |        25.3 |                213 |        16.1 |              3.7 |

## variantes_questions

```sql
SELECT
    SUM(instr(contenido,'?') > 0 OR instr(contenido, char(191)) > 0) AS marca_signo,
    SUM(es_libre)                                         AS libre,
    SUM(es_ayuda)                                         AS ayuda_publicada,
    ROUND(1.0 * SUM(es_ayuda) / (SELECT COUNT(*) FROM v_ms_pub), 2) AS ayuda_por_sesion
FROM v_msg_pub
WHERE rol = 'nino';

-- ---------------------------------------------------------------------
-- Q3.6  Bloques de Scratch sugeridos por Bit (validados contra el catálogo)
-- ---------------------------------------------------------------------
```

|   marca_signo |   libre |   ayuda_publicada |   ayuda_por_sesion |
|--------------:|--------:|------------------:|-------------------:|
|            44 |     334 |               213 |               2.17 |

## bloques_top

```sql
SELECT
    json_extract(j.value, '$.id')                         AS bloque_id,
    json_extract(j.value, '$.nombre')                     AS nombre,
    COUNT(*)                                              AS veces_sugerido,
    COUNT(DISTINCT m.sesion_id)                           AS sesiones,
    COUNT(DISTINCT m.estudiante_id)                       AS ninos
FROM v_msg_pub m,
     json_each(COALESCE(json_extract(m.metadata,'$.bloques_sugeridos'),'[]')) j
WHERE m.rol = 'tutor'
GROUP BY bloque_id, nombre
ORDER BY veces_sugerido DESC;

-- ---------------------------------------------------------------------
-- Q3.7  Modelo LLM y consumo de tokens
-- ---------------------------------------------------------------------
```

| bloque_id                             | nombre                         |   veces_sugerido |   sesiones |   ninos |
|:--------------------------------------|:-------------------------------|-----------------:|-----------:|--------:|
| movimiento_mover_pasos                | Mover pasos                    |               95 |         30 |      22 |
| eventos_bandera_verde                 | Al presionar bandera verde     |               80 |         38 |      23 |
| apariencia_decir_segundos             | Decir durante segundos         |               56 |         18 |      13 |
| apariencia_siguiente_disfraz          | Siguiente disfraz              |               54 |         21 |      14 |
| movimiento_cambiar_x                  | Cambiar x                      |               52 |         16 |      14 |
| eventos_tecla_presionada              | Al presionar tecla             |               46 |         14 |      14 |
| control_repetir_veces                 | Repetir veces                  |               44 |         19 |      17 |
| apariencia_cambiar_fondo              | Cambiar fondo                  |               43 |         16 |      16 |
| movimiento_girar_derecha_grados       | Girar a la derecha             |               39 |         18 |      17 |
| movimiento_cambiar_y                  | Cambiar y                      |               35 |          7 |       6 |
| control_esperar_segundos              | Esperar segundos               |               17 |          8 |       7 |
| control_por_siempre                   | Por siempre                    |               16 |          8 |       6 |
| movimiento_girar_izquierda_grados     | Girar a la izquierda           |               13 |          7 |       6 |
| sensores_tocando                      | Tocando objeto                 |               13 |          4 |       4 |
| eventos_al_recibir_mensaje            | Al recibir mensaje             |                8 |          3 |       3 |
| variables_cambiar                     | Cambiar variable               |                7 |          4 |       4 |
| apariencia_cambiar_disfraz            | Cambiar disfraz                |                6 |          4 |       3 |
| eventos_enviar_mensaje                | Enviar mensaje                 |                6 |          3 |       3 |
| sonido_iniciar_sonido                 | Iniciar sonido                 |                6 |          4 |       4 |
| sonido_tocar_sonido_hasta_que_termine | Tocar sonido hasta que termine |                6 |          2 |       2 |
| sensores_tecla_presionada             | Tecla presionada (sensor)      |                5 |          3 |       3 |
| control_si_entonces                   | Si entonces                    |                4 |          3 |       3 |
| movimiento_apuntar_direccion          | Apuntar en dirección           |                3 |          2 |       2 |
| apariencia_esconder                   | Esconder                       |                2 |          2 |       2 |
| movimiento_fijar_x                    | Fijar x                        |                2 |          1 |       1 |
| operadores_numero_aleatorio           | Número aleatorio               |                2 |          1 |       1 |
| variables_boton_crear                 | Crear una variable             |                2 |          2 |       2 |
| apariencia_mostrar                    | Mostrar                        |                1 |          1 |       1 |
| movimiento_fijar_y                    | Fijar y                        |                1 |          1 |       1 |

## uso_llm

```sql
SELECT
    COALESCE(modelo_llm, '(apertura del sistema)')        AS modelo,
    COUNT(*)                                              AS respuestas,
    SUM(COALESCE(input_tokens, 0))                        AS input_tokens,
    SUM(COALESCE(output_tokens, 0))                       AS output_tokens,
    ROUND(AVG(COALESCE(input_tokens, 0)), 0)              AS input_medio,
    ROUND(AVG(COALESCE(output_tokens, 0)), 0)             AS output_medio
FROM v_msg_pub
WHERE rol = 'tutor'
GROUP BY modelo_llm
ORDER BY respuestas DESC;

-- ---------------------------------------------------------------------
-- Q3.8  Reanudaciones: sesiones que continuaron en un sábado posterior
-- ---------------------------------------------------------------------
```

| modelo                  |   respuestas |   input_tokens |   output_tokens |   input_medio |   output_medio |
|:------------------------|-------------:|---------------:|----------------:|--------------:|---------------:|
| google/gemini-2.5-flash |         1320 |        4872104 |          266988 |          3691 |            202 |
| (apertura del sistema)  |           98 |              0 |               0 |             0 |              0 |

## reanudaciones

```sql
SELECT n_dias, COUNT(*) AS sesiones, ROUND(AVG(duracion_min),1) AS dur_media
FROM v_ms_pub
GROUP BY n_dias
ORDER BY n_dias;

-- ---------------------------------------------------------------------
-- Q3.9  Métricas por sesión EXCLUYENDO sesiones sin ningún intercambio
--       (13 sesiones de la cohorte B se abrieron y nunca se habló con Bit;
--        esta variante sirve como análisis de sensibilidad de la Tabla 2)
-- ---------------------------------------------------------------------
```

|   n_dias |   sesiones |   dur_media |
|---------:|-----------:|------------:|
|        1 |         94 |        12.9 |
|        2 |          4 |        33.7 |

## tabla2_sin_sesiones_vacias

```sql
SELECT
    k.cohorte,
    COUNT(*)                                              AS sesiones,
    COUNT(DISTINCT ms.estudiante_id)                      AS ninos,
    SUM(ms.mensajes)                                      AS mensajes,
    ROUND(AVG(ms.turnos), 1)                              AS turnos_media,
    ROUND(SQRT((SUM(ms.turnos*ms.turnos)-COUNT(*)*AVG(ms.turnos)*AVG(ms.turnos))/(COUNT(*)-1.0)),1) AS turnos_sd,
    ROUND(AVG(ms.preguntas), 1)                           AS preguntas_media,
    ROUND(AVG(ms.duracion_min), 1)                        AS dur_media,
    ROUND(SQRT((SUM(ms.duracion_min*ms.duracion_min)-COUNT(*)*AVG(ms.duracion_min)*AVG(ms.duracion_min))/(COUNT(*)-1.0)),1) AS dur_sd,
    ROUND(AVG(ms.bloques_sugeridos), 1)                   AS bloques_media,
    ROUND(100.0 * SUM(ms.estado='cerrada')    / COUNT(*), 1) AS closed_pct,
    ROUND(100.0 * SUM(ms.estado='abandonada') / COUNT(*), 1) AS abandoned_pct,
    ROUND(100.0 * SUM(ms.estado='activa')     / COUNT(*), 1) AS active_pct
FROM v_metricas_sesion ms
JOIN v_cohorte k ON k.estudiante_id = ms.estudiante_id
WHERE ms.turnos > 0
GROUP BY k.cohorte;

-- ---------------------------------------------------------------------
-- Q3.10 Sesiones cerradas vs abandonadas: qué las distingue (RQ3)
-- ---------------------------------------------------------------------
```

| cohorte      |   sesiones |   ninos |   mensajes |   turnos_media |   turnos_sd |   preguntas_media |   dur_media |   dur_sd |   bloques_media |   closed_pct |   abandoned_pct |   active_pct |
|:-------------|-----------:|--------:|-----------:|---------------:|------------:|------------------:|------------:|---------:|----------------:|-------------:|----------------:|-------------:|
| A_todos      |         89 |      28 |       2789 |           15.2 |        13.2 |               2.5 |        15.9 |     13.7 |             7.6 |         42.7 |            43.8 |         13.5 |
| B_edad_10_13 |         85 |      25 |       2725 |           15.5 |        13.4 |               2.5 |        15.9 |     13.7 |             7.8 |         42.4 |            44.7 |         12.9 |

## cerradas_vs_abandonadas

```sql
SELECT
    ms.estado,
    COUNT(*)                                              AS sesiones,
    ROUND(AVG(ms.turnos), 1)                              AS turnos,
    ROUND(AVG(ms.preguntas), 1)                           AS preguntas,
    ROUND(AVG(ms.duracion_min), 1)                        AS duracion,
    ROUND(AVG(ms.bloques_sugeridos), 1)                   AS bloques,
    ROUND(AVG(1.0*ms.chips_usados / NULLIF(ms.msg_nino,0)) * 100, 1) AS pct_chips,
    ROUND(AVG(ms.nivel_satisfaccion), 2)                  AS satisfaccion
FROM v_ms_pub ms
WHERE ms.turnos > 0
GROUP BY ms.estado
ORDER BY sesiones DESC;

-- ---------------------------------------------------------------------
-- Q3.11 Impacto de excluir a los 3 que no son 10-13.
--       Verifica además las cifras que el borrador dejó pendientes
--       ("[81] sessions … [2,000] messages across 4 exercises").
-- ---------------------------------------------------------------------
```

| estado     |   sesiones |   turnos |   preguntas |   duracion |   bloques |   pct_chips |   satisfaccion |
|:-----------|-----------:|---------:|------------:|-----------:|----------:|------------:|---------------:|
| abandonada |         38 |     15.7 |         2.8 |       17.2 |       7.6 |        57.5 |           4.15 |
| cerrada    |         36 |     14.6 |         2.1 |       14.1 |       7.4 |        67.8 |           4.08 |
| activa     |         11 |     18.1 |         2.8 |       17.1 |      10   |        64.3 |           3    |

## verificacion_borrador

```sql
SELECT
    'B — publicada (25 niños, 10-13)'                        AS cohorte,
    COUNT(*)                                                 AS sesiones,
    SUM(mensajes)                                            AS mensajes,
    SUM(msg_nino)                                            AS msg_nino,
    COUNT(DISTINCT CASE WHEN juego_id <> 'proyecto_libre'
                        THEN juego_id END)                   AS ejercicios,
    ROUND(100.0 * SUM(estado='cerrada')    / COUNT(*), 1)    AS closed_pct,
    ROUND(100.0 * SUM(estado='abandonada') / COUNT(*), 1)    AS abandoned_pct
FROM v_ms_pub
UNION ALL
SELECT
    'A — todos los que usaron Bit (28)',
    COUNT(*), SUM(mensajes), SUM(msg_nino),
    COUNT(DISTINCT CASE WHEN juego_id <> 'proyecto_libre' THEN juego_id END),
    ROUND(100.0 * SUM(estado='cerrada')    / COUNT(*), 1),
    ROUND(100.0 * SUM(estado='abandonada') / COUNT(*), 1)
FROM v_metricas_sesion
UNION ALL
SELECT
    'Diferencia (los 3 excluidos)',
    (SELECT COUNT(*)      FROM v_metricas_sesion) - (SELECT COUNT(*)      FROM v_ms_pub),
    (SELECT SUM(mensajes) FROM v_metricas_sesion) - (SELECT SUM(mensajes) FROM v_ms_pub),
    (SELECT SUM(msg_nino) FROM v_metricas_sesion) - (SELECT SUM(msg_nino) FROM v_ms_pub),
    NULL, NULL, NULL;
```

| cohorte                           |   sesiones |   mensajes |   msg_nino |   ejercicios |   closed_pct |   abandoned_pct |
|:----------------------------------|-----------:|-----------:|-----------:|-------------:|-------------:|----------------:|
| B — publicada (25 niños, 10-13)   |         98 |       2738 |       1320 |            6 |         41.8 |            42.9 |
| A — todos los que usaron Bit (28) |        102 |       2802 |       1350 |            6 |         42.2 |            42.2 |
| Diferencia (los 3 excluidos)      |          4 |         64 |         30 |          nan |        nan   |           nan   |
