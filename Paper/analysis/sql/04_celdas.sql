-- =====================================================================
-- 04_celdas.sql — Una consulta mínima por CADA celda de las Tablas 1 y 2.
--
-- Sirve para auditar: cada número publicado se puede reproducir con la
-- consulta de al lado, sin depender del resto del archivo. Todas leen de
-- `v_ms_pub` / `v_msg_pub` / `v_participantes` (cohorte publicada: los 25
-- niños/as de 10 a 13 años).
--
-- Requiere: build_sqlite.py + sql/00a_hoja_asistencia.sql + sql/00_scope.sql
-- =====================================================================


-- ================== TABLA 1 — Demografía =============================

-- T1.a  Age × Freq  → 10:6  11:11  12:6  13:2
-- @name t1_edad
SELECT edad AS item, COUNT(*) AS freq
FROM v_participantes
WHERE clase_edad = 'en_rango_10_13'
GROUP BY edad ORDER BY edad;

-- T1.b  Gender × Freq  → Male 15, Female 10, Non-specified 0
-- @name t1_genero
SELECT
    SUM(genero_opcion = 'masculino')                       AS male,
    SUM(genero_opcion = 'femenino')                        AS female,
    SUM(genero_opcion IS NULL
        OR genero_opcion NOT IN ('masculino','femenino'))  AS non_specified
FROM v_participantes
WHERE clase_edad = 'en_rango_10_13';

-- T1.c  Total students → 25
-- @name t1_total
SELECT COUNT(*) AS total_students
FROM v_participantes WHERE clase_edad = 'en_rango_10_13';


-- ================== TABLA 2 — Data totals ============================

-- T2.1  Children → 25
-- @name t2_children
SELECT COUNT(DISTINCT estudiante_id) AS children FROM v_ms_pub;

-- T2.2  Sessions → 98
-- @name t2_sessions
SELECT COUNT(*) AS sessions FROM v_ms_pub;

-- T2.3  Messages → 2738
-- @name t2_messages
SELECT COUNT(*) AS messages FROM v_msg_pub;

-- T2.4  Child msg. → 1320
-- @name t2_child_msg
SELECT COUNT(*) AS child_msg FROM v_msg_pub WHERE rol = 'nino';

-- T2.5  Bit msg. → 1418  (1320 del LLM + 98 mensajes de apertura)
-- @name t2_bit_msg
SELECT COUNT(*)                    AS bit_msg,
       SUM(es_apertura = 0)        AS generados_por_llm,
       SUM(es_apertura = 1)        AS apertura_del_sistema
FROM v_msg_pub WHERE rol = 'tutor';

-- T2.6  Exercises → 6  (proyecto_libre no es un ejercicio del catálogo)
-- @name t2_exercises
SELECT COUNT(DISTINCT juego_id) AS exercises
FROM v_ms_pub WHERE juego_id <> 'proyecto_libre';


-- ================== TABLA 2 — Per session (media ± SD) ===============

-- T2.7  Turns → 13.5 ± 13.5
-- @name t2_turns
SELECT ROUND(AVG(turnos), 1) AS media,
       ROUND(SQRT((SUM(turnos*turnos) - COUNT(*)*AVG(turnos)*AVG(turnos))
                  / (COUNT(*) - 1.0)), 1) AS sd
FROM v_ms_pub;

-- T2.8  Messages → 27.9 ± 27.1
-- @name t2_messages_ses
SELECT ROUND(AVG(mensajes), 1) AS media,
       ROUND(SQRT((SUM(mensajes*mensajes) - COUNT(*)*AVG(mensajes)*AVG(mensajes))
                  / (COUNT(*) - 1.0)), 1) AS sd
FROM v_ms_pub;

-- T2.9  Questions → 2.2 ± 2.7
-- @name t2_questions
SELECT ROUND(AVG(preguntas), 1) AS media,
       ROUND(SQRT((SUM(preguntas*preguntas) - COUNT(*)*AVG(preguntas)*AVG(preguntas))
                  / (COUNT(*) - 1.0)), 1) AS sd
FROM v_ms_pub;

-- T2.10 Duration (min) → 13.8 ± 13.9
-- @name t2_duration
SELECT ROUND(AVG(duracion_min), 1) AS media,
       ROUND(SQRT((SUM(duracion_min*duracion_min)
                   - COUNT(*)*AVG(duracion_min)*AVG(duracion_min))
                  / (COUNT(*) - 1.0)), 1) AS sd
FROM v_ms_pub;

-- T2.11 Blocks sugg. → 6.8 ± 7.6
-- @name t2_blocks
SELECT ROUND(AVG(bloques_sugeridos), 1) AS media,
       ROUND(SQRT((SUM(bloques_sugeridos*bloques_sugeridos)
                   - COUNT(*)*AVG(bloques_sugeridos)*AVG(bloques_sugeridos))
                  / (COUNT(*) - 1.0)), 1) AS sd
FROM v_ms_pub;


-- ================== TABLA 2 — Outcomes ===============================

-- T2.12-14  Closed / Abandoned / Active %  → 41.8 / 42.9 / 15.3
-- @name t2_outcomes
SELECT estado,
       COUNT(*)                                          AS n,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM v_ms_pub), 1) AS pct
FROM v_ms_pub
GROUP BY estado ORDER BY n DESC;

-- T2.15 Satisf. (1-5) → 3.9 ± 1.2  (sobre las 60 sesiones con feedback)
-- @name t2_satisf
SELECT COUNT(*) AS n_con_feedback,
       ROUND(AVG(nivel_satisfaccion), 1) AS media,
       ROUND(SQRT((SUM(nivel_satisfaccion*nivel_satisfaccion)
                   - COUNT(*)*AVG(nivel_satisfaccion)*AVG(nivel_satisfaccion))
                  / (COUNT(*) - 1.0)), 1) AS sd
FROM v_ms_pub WHERE nivel_satisfaccion IS NOT NULL;


-- ================== TABLA 2 — bloque «Per session» completo ==========
-- Devuelve las 5 filas ya formateadas como "media ± SD", en el mismo
-- orden en que aparecen en la tabla del paper.
-- @name t2_per_session_todas
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
