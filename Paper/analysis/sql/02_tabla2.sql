-- =====================================================================
-- 02_tabla2.sql — Tabla 2 del paper (tab:corpus)
--   "Overview of the interaction data. Per-session values are mean ± SD."
-- Requiere: build_sqlite.py + sql/00_scope.sql
--
-- Cada consulta devuelve una fila por cohorte:
--   A_todos      → 28 niños/as (todos los que usaron a Bit)
--   B_edad_10_13 → 19 niños/as con edad registrada entre 10 y 13
-- =====================================================================

-- ---------------------------------------------------------------------
-- Q2.1  Bloque «Data totals»
--   Children / Sessions / Messages / Child msg. / Bit msg. / Exercises
--
--   Bit msg. incluye el mensaje de apertura sembrado por el sistema en
--   cada conversación (`instruccion_nino`); `msg_bit_llm` da el subconjunto
--   realmente generado por el LLM. Así Child + Bit = Messages.
--   Exercises cuenta los `juego_id` distintos trabajados (proyecto_libre
--   se reporta aparte porque no es un ejercicio del catálogo).
-- ---------------------------------------------------------------------
-- @name totales
SELECT
    k.cohorte,
    COUNT(DISTINCT ms.estudiante_id)                       AS children,
    COUNT(*)                                               AS sessions,
    SUM(ms.mensajes)                                       AS messages,
    SUM(ms.msg_nino)                                       AS child_msg,
    SUM(ms.msg_bit)                                        AS bit_msg,
    SUM(ms.msg_bit_llm)                                    AS bit_msg_llm,
    SUM(ms.msg_bit) - SUM(ms.msg_bit_llm)                  AS bit_msg_apertura,
    COUNT(DISTINCT ms.juego_id)                            AS exercises_incl_libre,
    COUNT(DISTINCT CASE WHEN ms.juego_id <> 'proyecto_libre'
                        THEN ms.juego_id END)              AS exercises,
    SUM(ms.turnos)                                         AS turns,
    SUM(ms.preguntas)                                      AS questions,
    SUM(ms.bloques_sugeridos)                              AS blocks_sugg
FROM v_metricas_sesion ms
JOIN v_cohorte k ON k.estudiante_id = ms.estudiante_id
GROUP BY k.cohorte
ORDER BY k.cohorte;

-- ---------------------------------------------------------------------
-- Q2.2  Bloque «Per session» — media ± SD (SD muestral, n-1)
--   Turns / Messages / Questions / Duration (min) / Blocks sugg.
-- ---------------------------------------------------------------------
-- @name por_sesion
WITH d AS (
    SELECT k.cohorte, ms.turnos, ms.mensajes, ms.preguntas,
           ms.duracion_min, ms.bloques_sugeridos
    FROM v_metricas_sesion ms
    JOIN v_cohorte k ON k.estudiante_id = ms.estudiante_id
)
SELECT
    cohorte,
    COUNT(*)                                               AS n_sesiones,
    ROUND(AVG(turnos), 2)            AS turns_mean,
    ROUND(SQRT((SUM(turnos*turnos) - COUNT(*)*AVG(turnos)*AVG(turnos))
               / (COUNT(*) - 1.0)), 2)                     AS turns_sd,
    ROUND(AVG(mensajes), 2)          AS messages_mean,
    ROUND(SQRT((SUM(mensajes*mensajes) - COUNT(*)*AVG(mensajes)*AVG(mensajes))
               / (COUNT(*) - 1.0)), 2)                     AS messages_sd,
    ROUND(AVG(preguntas), 2)         AS questions_mean,
    ROUND(SQRT((SUM(preguntas*preguntas) - COUNT(*)*AVG(preguntas)*AVG(preguntas))
               / (COUNT(*) - 1.0)), 2)                     AS questions_sd,
    ROUND(AVG(duracion_min), 2)      AS duration_mean,
    ROUND(SQRT((SUM(duracion_min*duracion_min)
                - COUNT(*)*AVG(duracion_min)*AVG(duracion_min))
               / (COUNT(*) - 1.0)), 2)                     AS duration_sd,
    ROUND(AVG(bloques_sugeridos), 2) AS blocks_mean,
    ROUND(SQRT((SUM(bloques_sugeridos*bloques_sugeridos)
                - COUNT(*)*AVG(bloques_sugeridos)*AVG(bloques_sugeridos))
               / (COUNT(*) - 1.0)), 2)                     AS blocks_sd
FROM d
GROUP BY cohorte
ORDER BY cohorte;

-- ---------------------------------------------------------------------
-- Q2.3  Bloque «Outcomes» — desenlace de las sesiones
--   `cerrada`    → el/la docente verificó la solución en Scratch y cerró
--   `abandonada` → el navegador disparó el beacon de abandono o el niño
--                  cambió de ejercicio sin terminar
--   `activa`     → nunca se cerró (quedó abierta al final de la jornada)
-- ---------------------------------------------------------------------
-- @name outcomes
SELECT
    k.cohorte,
    COUNT(*)                                               AS n_sesiones,
    SUM(ms.estado = 'cerrada')                             AS closed_n,
    ROUND(100.0 * SUM(ms.estado = 'cerrada')    / COUNT(*), 1) AS closed_pct,
    SUM(ms.estado = 'abandonada')                          AS abandoned_n,
    ROUND(100.0 * SUM(ms.estado = 'abandonada') / COUNT(*), 1) AS abandoned_pct,
    SUM(ms.estado = 'activa')                              AS active_n,
    ROUND(100.0 * SUM(ms.estado = 'activa')     / COUNT(*), 1) AS active_pct
FROM v_metricas_sesion ms
JOIN v_cohorte k ON k.estudiante_id = ms.estudiante_id
GROUP BY k.cohorte
ORDER BY k.cohorte;

-- ---------------------------------------------------------------------
-- Q2.4  Bloque «Outcomes» — satisfacción (escala emoji 1–5)
--   Solo sobre las sesiones que registraron feedback.
-- ---------------------------------------------------------------------
-- @name satisfaccion
WITH d AS (
    SELECT k.cohorte, ms.nivel_satisfaccion AS s
    FROM v_metricas_sesion ms
    JOIN v_cohorte k ON k.estudiante_id = ms.estudiante_id
    WHERE ms.nivel_satisfaccion IS NOT NULL
)
SELECT
    cohorte,
    COUNT(*)                                               AS n_feedback,
    ROUND(AVG(s), 2)                                       AS satisf_mean,
    ROUND(SQRT((SUM(s*s) - COUNT(*)*AVG(s)*AVG(s)) / (COUNT(*) - 1.0)), 2) AS satisf_sd,
    MIN(s) AS min, MAX(s) AS max
FROM d
GROUP BY cohorte
ORDER BY cohorte;

-- ---------------------------------------------------------------------
-- Q2.5  Cobertura del feedback (cuántas sesiones lo registraron)
-- ---------------------------------------------------------------------
-- @name cobertura_feedback
SELECT
    k.cohorte,
    COUNT(*)                                               AS sesiones,
    SUM(ms.nivel_satisfaccion IS NOT NULL)                 AS con_feedback,
    ROUND(100.0 * SUM(ms.nivel_satisfaccion IS NOT NULL) / COUNT(*), 1) AS pct
FROM v_metricas_sesion ms
JOIN v_cohorte k ON k.estudiante_id = ms.estudiante_id
GROUP BY k.cohorte;

-- ---------------------------------------------------------------------
-- Q2.6  Distribución de la escala de satisfacción
-- ---------------------------------------------------------------------
-- @name satisfaccion_dist
SELECT
    k.cohorte, ms.nivel_satisfaccion AS nivel, COUNT(*) AS n
FROM v_metricas_sesion ms
JOIN v_cohorte k ON k.estudiante_id = ms.estudiante_id
WHERE ms.nivel_satisfaccion IS NOT NULL
GROUP BY k.cohorte, ms.nivel_satisfaccion
ORDER BY k.cohorte, nivel;

-- ---------------------------------------------------------------------
-- Q2.7  TABLA 2 ENSAMBLADA — cohorte B (edad 10–13), lista para LaTeX
--   Devuelve las 15 celdas de la tabla en el mismo orden en que aparecen.
-- ---------------------------------------------------------------------
-- @name tabla2_armada
WITH ms AS (
    SELECT ms.* FROM v_metricas_sesion ms
    JOIN v_cohorte k ON k.estudiante_id = ms.estudiante_id
    WHERE k.cohorte = 'B_edad_10_13'
),
n AS (SELECT COUNT(*) AS ns FROM ms)
SELECT 1 AS ord, 'Data totals' AS bloque, 'Children'  AS metrica,
       CAST(COUNT(DISTINCT estudiante_id) AS TEXT) AS valor FROM ms
UNION ALL SELECT 2, 'Data totals', 'Sessions',   CAST(COUNT(*) AS TEXT) FROM ms
UNION ALL SELECT 3, 'Data totals', 'Messages',   CAST(SUM(mensajes) AS TEXT) FROM ms
UNION ALL SELECT 4, 'Data totals', 'Child msg.', CAST(SUM(msg_nino) AS TEXT) FROM ms
UNION ALL SELECT 5, 'Data totals', 'Bit msg.',   CAST(SUM(msg_bit) AS TEXT) FROM ms
UNION ALL SELECT 6, 'Data totals', 'Exercises',
       CAST(COUNT(DISTINCT CASE WHEN juego_id <> 'proyecto_libre'
                                THEN juego_id END) AS TEXT) FROM ms
UNION ALL SELECT 7, 'Per session', 'Turns',
       ROUND(AVG(turnos),1) || ' ± ' ||
       ROUND(SQRT((SUM(turnos*turnos)-COUNT(*)*AVG(turnos)*AVG(turnos))/(COUNT(*)-1.0)),1) FROM ms
UNION ALL SELECT 8, 'Per session', 'Messages',
       ROUND(AVG(mensajes),1) || ' ± ' ||
       ROUND(SQRT((SUM(mensajes*mensajes)-COUNT(*)*AVG(mensajes)*AVG(mensajes))/(COUNT(*)-1.0)),1) FROM ms
UNION ALL SELECT 9, 'Per session', 'Questions',
       ROUND(AVG(preguntas),1) || ' ± ' ||
       ROUND(SQRT((SUM(preguntas*preguntas)-COUNT(*)*AVG(preguntas)*AVG(preguntas))/(COUNT(*)-1.0)),1) FROM ms
UNION ALL SELECT 10, 'Per session', 'Duration (min)',
       ROUND(AVG(duracion_min),1) || ' ± ' ||
       ROUND(SQRT((SUM(duracion_min*duracion_min)-COUNT(*)*AVG(duracion_min)*AVG(duracion_min))/(COUNT(*)-1.0)),1) FROM ms
UNION ALL SELECT 11, 'Per session', 'Blocks sugg.',
       ROUND(AVG(bloques_sugeridos),1) || ' ± ' ||
       ROUND(SQRT((SUM(bloques_sugeridos*bloques_sugeridos)-COUNT(*)*AVG(bloques_sugeridos)*AVG(bloques_sugeridos))/(COUNT(*)-1.0)),1) FROM ms
UNION ALL SELECT 12, 'Outcomes', 'Closed %',
       ROUND(100.0*SUM(estado='cerrada')/(SELECT ns FROM n),1) || ' %' FROM ms
UNION ALL SELECT 13, 'Outcomes', 'Abandoned %',
       ROUND(100.0*SUM(estado='abandonada')/(SELECT ns FROM n),1) || ' %' FROM ms
UNION ALL SELECT 14, 'Outcomes', 'Active %',
       ROUND(100.0*SUM(estado='activa')/(SELECT ns FROM n),1) || ' %' FROM ms
UNION ALL SELECT 15, 'Outcomes', 'Satisf. (1-5)',
       ROUND(AVG(nivel_satisfaccion),1) || ' ± ' ||
       ROUND(SQRT((SUM(nivel_satisfaccion*nivel_satisfaccion)
                   - SUM(nivel_satisfaccion IS NOT NULL)*AVG(nivel_satisfaccion)*AVG(nivel_satisfaccion))
                  / (SUM(nivel_satisfaccion IS NOT NULL)-1.0)),1) FROM ms
ORDER BY ord;
