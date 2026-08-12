-- =====================================================================
-- 03_contexto.sql — Análisis de apoyo para §Data Collection y §Results
-- Requiere: build_sqlite.py + sql/00_scope.sql
-- TODO va sobre la COHORTE PUBLICADA (v_ms_pub / v_msg_pub): los 25
-- niños/as de 10 a 13 años, 98 sesiones, 2 738 mensajes. Q3.9 y Q3.11
-- son las únicas que comparan contra la cohorte completa de 28.
-- =====================================================================

-- ---------------------------------------------------------------------
-- Q3.1  Por ejercicio: intentos, desenlace y volumen de diálogo
--       (alimenta RQ2: patrones de finalización y abandono)
-- ---------------------------------------------------------------------
-- @name por_ejercicio
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
-- @name por_jornada
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
-- @name fases
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
-- @name modo_respuesta_nino
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
-- @name variantes_questions
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
-- @name bloques_top
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
-- @name uso_llm
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
-- @name reanudaciones
SELECT n_dias, COUNT(*) AS sesiones, ROUND(AVG(duracion_min),1) AS dur_media
FROM v_ms_pub
GROUP BY n_dias
ORDER BY n_dias;

-- ---------------------------------------------------------------------
-- Q3.9  Métricas por sesión EXCLUYENDO sesiones sin ningún intercambio
--       (13 sesiones de la cohorte B se abrieron y nunca se habló con Bit;
--        esta variante sirve como análisis de sensibilidad de la Tabla 2)
-- ---------------------------------------------------------------------
-- @name tabla2_sin_sesiones_vacias
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
-- @name cerradas_vs_abandonadas
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
-- @name verificacion_borrador
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
