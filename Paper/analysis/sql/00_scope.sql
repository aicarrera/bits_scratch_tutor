-- =====================================================================
-- 00_scope.sql — Vistas de alcance del estudio (se ejecutan una vez,
-- después de build_sqlite.py). Definen QUIÉN y QUÉ entra en el análisis.
-- =====================================================================
--
-- Decisiones de alcance (justificadas en ANALISIS.md):
--
--   1. Solo el grupo "ESTUDIANTES NIVEL 0" (bd4b3eb8-…). Se excluyen:
--        · el grupo "CreaBits Demo"  → cuentas de prueba del equipo
--          (tigre-azul-7, demo-ia-1, leon-rojo-3)
--        · las cuentas voluntario-1…10 (grupo_id NULL) → pruebas piloto
--   2. Solo las TRES jornadas de recolección (sábados, hora de Ecuador
--      UTC-5): 2026-07-11, 2026-07-18 y 2026-08-01.
--   3. Un/a niño/a "participó" si tiene ≥1 sesión dentro de ese alcance.
--
-- Nota sobre reasignaciones de código: `tigre-rosado-25b` (Danna Almeida)
-- y `tigre-rosado-8b` (Valentina Jimenez) son NIÑAS DISTINTAS de
-- `tigre-rosado-25` y `tigre-rosado-8`; usaron el código de una compañera
-- ausente el 18/07 y el equipo creó una fila separada (ver
-- estudiantes.notas_investigador). Se cuentan como participantes propias.
-- =====================================================================

DROP VIEW IF EXISTS v_msg_pub;
DROP VIEW IF EXISTS v_ms_pub;
DROP VIEW IF EXISTS v_metricas_sesion;
DROP VIEW IF EXISTS v_cohorte;
DROP VIEW IF EXISTS v_msg_estudio;
DROP VIEW IF EXISTS v_conv_estudio;
DROP VIEW IF EXISTS v_participantes;
DROP VIEW IF EXISTS v_sesiones_estudio;
DROP VIEW IF EXISTS v_jornadas;

-- Las tres jornadas de recolección de datos.
CREATE VIEW v_jornadas (fecha_local, jornada) AS
SELECT '2026-07-11', 1 UNION ALL
SELECT '2026-07-18', 2 UNION ALL
SELECT '2026-08-01', 3;

-- Sesiones dentro del alcance.
CREATE VIEW v_sesiones_estudio AS
SELECT s.*, jo.jornada
FROM v_sesiones s
JOIN estudiantes  e  ON e.id = s.estudiante_id
JOIN v_jornadas   jo ON jo.fecha_local = s.fecha_local
WHERE e.grupo_id = 'bd4b3eb8-4c9b-4e20-a916-944db2f72e1d';

-- Niños/as que participaron, con su demografía y clasificación de edad.
CREATE VIEW v_participantes AS
SELECT
    e.id, e.codigo_publico, e.nombre_completo, e.edad, e.genero_opcion,
    CASE
        WHEN e.edad IS NULL              THEN 'no_registrada'
        WHEN e.edad BETWEEN 10 AND 13    THEN 'en_rango_10_13'
        ELSE 'fuera_de_rango'
    END                                          AS clase_edad,
    COUNT(s.id)                                  AS n_sesiones,
    COUNT(DISTINCT s.jornada)                    AS n_jornadas
FROM estudiantes e
JOIN v_sesiones_estudio s ON s.estudiante_id = e.id
GROUP BY e.id;

-- Conversaciones de las sesiones en alcance (relación 1:1 con sesión).
CREATE VIEW v_conv_estudio AS
SELECT c.*, s.jornada
FROM v_conversaciones c
JOIN v_sesiones_estudio s ON s.id = c.sesion_id;

-- ---------------------------------------------------------------------
-- Mensajes de las sesiones en alcance, con clasificación de cada turno.
--
--   es_apertura = mensaje semilla `instruccion_nino` que el sistema
--                 inserta al abrir la conversación (rol='tutor',
--                 proveedor_llm='system'); NO es una respuesta del LLM.
--   es_chip     = el texto del niño coincide EXACTAMENTE con una de las
--                 `opciones_respuesta` que Bit ofreció en su mensaje
--                 inmediatamente anterior → el niño tocó un chip.
--   es_libre    = mensaje del niño escrito a mano (no chip).
--   es_ayuda    = mensaje libre que pide ayuda / información / plantea un
--                 objetivo a Bit. Es la definición de "Questions" en la
--                 Tabla 2 (ver ANALISIS.md §Definiciones).
--
-- `txt` normaliza el texto para el emparejamiento léxico: minúsculas, sin
-- tildes/ñ, signos de puntuación → espacio, y con espacios en los
-- extremos, de modo que ' que ' empareja la palabra completa y no el
-- interior de "quiero" o "porque".
-- ---------------------------------------------------------------------
CREATE VIEW v_msg_estudio AS
WITH base AS (
    SELECT m.*, s.jornada, s.estado AS estado_sesion,
           ' ' || replace(replace(replace(replace(replace(replace(replace(
                  replace(replace(replace(replace(replace(replace(replace(
                  replace(replace(replace(replace(replace(replace(replace(
                      lower(m.contenido),
                      'á','a'),'é','e'),'í','i'),'ó','o'),'ú','u'),'ñ','n'),'ü','u'),
                      'Á','a'),'É','e'),'Í','i'),'Ó','o'),'Ú','u'),'Ñ','n'),'Ü','u'),
                      ',',' '),'.',' '),';',' '),':',' '),'!',' '),'¡',' '),
                      char(10),' ')
           || ' '                                            AS txt,
           (SELECT t.metadata FROM mensajes t
             WHERE t.conversacion_id = m.conversacion_id
               AND t.orden_mensaje  < m.orden_mensaje
               AND t.rol = 'tutor'
             ORDER BY t.orden_mensaje DESC LIMIT 1)           AS meta_tutor_previo
    FROM v_mensajes m
    JOIN v_sesiones_estudio s ON s.id = m.sesion_id
),
marcado AS (
    SELECT b.*,
        CASE WHEN b.rol = 'tutor' AND b.proveedor_llm = 'system'
             THEN 1 ELSE 0 END                                AS es_apertura,
        CASE WHEN b.rol = 'nino' AND b.meta_tutor_previo IS NOT NULL
                  AND EXISTS (SELECT 1
                              FROM json_each(COALESCE(
                                   json_extract(b.meta_tutor_previo,'$.opciones_respuesta'),'[]')) j
                              WHERE j.value = b.contenido)
             THEN 1 ELSE 0 END                                AS es_chip
    FROM base b
)
SELECT m.*,
       CASE WHEN m.rol = 'nino' AND m.es_chip = 0 THEN 1 ELSE 0 END AS es_libre,
       CASE WHEN m.rol = 'nino' AND m.es_chip = 0 AND (
            -- (a) marca explícita de interrogación
               instr(m.contenido, '?') > 0
            OR instr(m.contenido, char(191)) > 0                   -- '¿'
            -- (b) pronombre/adverbio interrogativo (palabra completa,
            --     incluidas abreviaturas y errores ortográficos frecuentes)
            OR m.txt LIKE '%como%'      OR m.txt LIKE '%komo%'
            OR m.txt LIKE '% cmo%'      OR m.txt LIKE '% c o %'
            OR m.txt LIKE '% que %'     OR m.txt LIKE '% q %'
            OR m.txt LIKE '% k %'       OR m.txt LIKE '% qe %'
            OR m.txt LIKE '% ke %'
            OR m.txt LIKE '%cual%'      OR m.txt LIKE '%cuant%'
            OR m.txt LIKE '%donde%'     OR m.txt LIKE '% dnd%'
            OR m.txt LIKE '%cuando%'    OR m.txt LIKE '%quien%'
            OR m.txt LIKE '%por que%'   OR m.txt LIKE '%porque%'
            OR m.txt LIKE '% xq %'      OR m.txt LIKE '% pq %'
            OR m.txt LIKE '%para que%'
            -- (c) petición explícita de ayuda / pista / demostración
            OR m.txt LIKE '%ayud%'      OR m.txt LIKE '%allud%'
            OR m.txt LIKE '%alluname%'  OR m.txt LIKE '%hayud%'
            OR m.txt LIKE '% auda%'     OR m.txt LIKE '%pista%'
            OR m.txt LIKE '%dime%'      OR m.txt LIKE '%dame%'
            OR m.txt LIKE '%muestra%'   OR m.txt LIKE '%ensena%'
            OR m.txt LIKE '%explica%'
            -- (d) señal de bloqueo / no encuentro / no funciona
            OR m.txt LIKE '%no entiendo%'  OR m.txt LIKE '% no se %'
            OR m.txt LIKE '%nose%'         OR m.txt LIKE '%no encuentro%'
            OR m.txt LIKE '%no la encuentro%' OR m.txt LIKE '%nola%'
            OR m.txt LIKE '%no lo encuentro%' OR m.txt LIKE '%no me aparece%'
            OR m.txt LIKE '%no aparece%'   OR m.txt LIKE '%no exi%'
            OR m.txt LIKE '%no puedo%'     OR m.txt LIKE '%no me sale%'
            OR m.txt LIKE '%no funciona%'  OR m.txt LIKE '%no lo veo%'
            OR m.txt LIKE '%no lo tengo%'  OR m.txt LIKE '%no pas% nada%'
            OR m.txt LIKE '%sigo sin%'     OR m.txt LIKE '%no quiere%'
            OR m.txt LIKE '%se puso loco%' OR m.txt LIKE '%sigue loco%'
            OR m.txt LIKE '%solo %'        OR m.txt LIKE '%le falta%'
            OR m.txt LIKE '%me falta%'
            -- (e) enunciado de objetivo dirigido a Bit ("quiero que…")
            OR m.txt LIKE '%quiero%'       OR m.txt LIKE '%qiero%'
            OR m.txt LIKE '%necesito%'     OR m.txt LIKE '%nesesito%'
            -- (f) petición del siguiente paso
            OR m.txt LIKE '%siguiente%'    OR m.txt LIKE '%sigiente%'
            OR m.txt LIKE '%y ahora%'      OR m.txt LIKE '%y aora%'
            OR m.txt LIKE '%que mas%'      OR m.txt LIKE '%despues%'
            OR m.txt LIKE '%empiezo%'      OR m.txt LIKE '%comienzo%'
            OR m.txt LIKE '%comienso%'     OR m.txt LIKE '%empezamos%'
            OR m.txt LIKE '%comensamos%'   OR m.txt LIKE '%comen%semos%'
           ) THEN 1 ELSE 0 END                                AS es_ayuda
FROM marcado m;

-- ---------------------------------------------------------------------
-- Cohortes de análisis. Toda la Tabla 2 se reporta para las dos, de modo
-- que el filtro por edad sea explícito y auditable:
--
--   A_todos       → los 28 niños/as que usaron a Bit en las 3 jornadas.
--   B_edad_10_13  → los 19 con edad registrada dentro de 10–13 años
--                   (excluye 2 de 16 años y 7 sin edad registrada).
-- ---------------------------------------------------------------------
CREATE VIEW v_cohorte AS
SELECT id AS estudiante_id, 'A_todos'      AS cohorte FROM v_participantes
UNION ALL
SELECT id,                  'B_edad_10_13'          FROM v_participantes
WHERE clase_edad = 'en_rango_10_13';

-- ---------------------------------------------------------------------
-- Métricas por sesión (unidad de análisis de la Tabla 2).
--
--   turnos       = intercambios niño→Bit. Cada mensaje del niño recibe
--                  exactamente una respuesta generada por el LLM, así que
--                  turnos = nº de respuestas del LLM = nº de mensajes del
--                  niño (verificado: 1350 = 1350 en el corpus).
--   msg_bit      = TODOS los mensajes de Bit = respuestas del LLM + el
--                  mensaje de apertura (`instruccion_nino`) que el sistema
--                  siembra al abrir la conversación.
--   duracion_min = tiempo activo. NO se usa `fin_en - inicio_en`: una
--                  sesión queda abierta hasta que el docente la cierra o
--                  el navegador dispara el beacon de abandono, lo que da
--                  duraciones de días. Se mide como la suma, por jornada,
--                  del lapso entre el primer y el último mensaje de esa
--                  sesión ese día (6 sesiones del estudio continuaron en
--                  un sábado posterior tras ser reanudadas).
-- ---------------------------------------------------------------------
CREATE VIEW v_metricas_sesion AS
WITH span AS (
    SELECT sesion_id, fecha_local,
           (julianday(MAX(creado_utc)) - julianday(MIN(creado_utc))) * 1440.0 AS min_dia
    FROM v_msg_estudio
    GROUP BY sesion_id, fecha_local
),
dur AS (
    SELECT sesion_id, SUM(min_dia) AS duracion_min, COUNT(*) AS n_dias
    FROM span GROUP BY sesion_id
)
SELECT
    s.id                                                  AS sesion_id,
    s.estudiante_id, s.jornada, s.fecha_local, s.estado,
    c.juego_id,
    COUNT(m.id)                                           AS mensajes,
    SUM(m.rol = 'nino')                                   AS msg_nino,
    SUM(m.rol = 'tutor')                                  AS msg_bit,
    SUM(m.rol = 'tutor' AND m.es_apertura = 0)            AS msg_bit_llm,
    SUM(m.rol = 'tutor' AND m.es_apertura = 0)            AS turnos,
    SUM(m.es_ayuda)                                       AS preguntas,
    SUM(m.es_chip)                                        AS chips_usados,
    SUM(m.es_libre)                                       AS msg_libres,
    SUM(CASE WHEN m.rol = 'tutor' THEN m.n_bloques ELSE 0 END)   AS bloques_sugeridos,
    SUM(CASE WHEN m.rol = 'tutor' THEN m.n_opciones ELSE 0 END)  AS opciones_ofrecidas,
    SUM(COALESCE(m.input_tokens, 0))                      AS input_tokens,
    SUM(COALESCE(m.output_tokens, 0))                     AS output_tokens,
    COALESCE(d.duracion_min, 0)                           AS duracion_min,
    COALESCE(d.n_dias, 0)                                 AS n_dias,
    f.nivel_satisfaccion
FROM v_sesiones_estudio s
JOIN v_conversaciones  c ON c.sesion_id = s.id
LEFT JOIN v_msg_estudio m ON m.sesion_id = s.id
LEFT JOIN dur          d ON d.sesion_id = s.id
LEFT JOIN v_feedback   f ON f.sesion_id = s.id
GROUP BY s.id;

-- ---------------------------------------------------------------------
-- Vistas de la COHORTE PUBLICADA (B: 25 niños/as de 10 a 13 años).
-- TODO lo que se reporta en el paper sale de aquí — tablas y resultados
-- de apoyo — para que no haya dos poblaciones distintas en el texto.
-- Los 3 excluidos (leon-azul-2 y tigre-rosado-25b, de 16 años, y
-- tigre-rosado-11, sin edad recuperable) aportan 4 sesiones y 64 mensajes.
-- ---------------------------------------------------------------------
CREATE VIEW v_ms_pub AS
SELECT ms.* FROM v_metricas_sesion ms
JOIN v_cohorte k ON k.estudiante_id = ms.estudiante_id
WHERE k.cohorte = 'B_edad_10_13';

CREATE VIEW v_msg_pub AS
SELECT m.* FROM v_msg_estudio m
JOIN v_cohorte k ON k.estudiante_id = m.estudiante_id
WHERE k.cohorte = 'B_edad_10_13';
