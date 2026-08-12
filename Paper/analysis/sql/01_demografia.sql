-- =====================================================================
-- 01_demografia.sql — Tabla 1 del paper (tab:demographics)
-- Requiere: build_sqlite.py + sql/00_scope.sql
-- =====================================================================

-- ---------------------------------------------------------------------
-- Q1.1  PADRÓN DEFINITIVO — la lista de estudiantes que usa el análisis.
--       Una fila por niño/a, con su actividad en cada jornada.
--       28 filas: las 25 de la cohorte publicada (10–13 años) primero,
--       luego los 3 excluidos.
--       j1 = 11/07, j2 = 18/07, j3 = 01/08 (sesiones abiertas ese día).
-- ---------------------------------------------------------------------
-- @name padron
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
-- @name cobertura_edad
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
-- @name tabla1_edad
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
-- @name tabla1_genero
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
-- @name tabla1_cruce
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
-- @name edad_stats
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
-- @name edad_mediana
SELECT AVG(edad) AS mediana
FROM (SELECT edad FROM v_participantes WHERE edad IS NOT NULL
      ORDER BY edad
      LIMIT 2 - (SELECT COUNT(*) FROM v_participantes WHERE edad IS NOT NULL) % 2
      OFFSET (SELECT (COUNT(*) - 1) / 2
              FROM v_participantes WHERE edad IS NOT NULL));

-- ---------------------------------------------------------------------
-- Q1.8  Asistencia por jornada (cuántos niños distintos cada sábado)
-- ---------------------------------------------------------------------
-- @name asistencia
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
-- @name jornadas_por_nino
SELECT n_jornadas, COUNT(*) AS ninos
FROM v_participantes
GROUP BY n_jornadas
ORDER BY n_jornadas;
