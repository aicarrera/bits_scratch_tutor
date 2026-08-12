-- =====================================================================
-- 00a_hoja_asistencia.sql — Completa las edades que faltaban en la base
-- a partir de la HOJA DE ASISTENCIA en papel ("Lista de asistencia –
-- CreaBits Tutor", 3 jornadas: 11/07, 18/07, 01/08).
--
-- Se aplica DESPUÉS de build_sqlite.py. Es idempotente.
--
-- Por qué se puede confiar en la hoja: las 21 edades que ya estaban en la
-- base coinciden UNA A UNA con las de la hoja, y las dos reasignaciones
-- que el equipo había anotado en `notas_investigador` (tigre-rosado-8b
-- Valentina Jimenez 12 y tigre-rosado-25b Danna Almeida 16) aparecen en la
-- hoja con el mismo nombre y la misma edad. Cero contradicciones en 23
-- puntos de control.
--
-- La hoja registra ASISTENCIA FÍSICA, no uso de Bit: 4 niños marcados
-- presentes no abrieron ninguna sesión ese día (leon-azul-2 y leon-azul-16
-- y tigre-rosado-12 el 18/07; tigre-rosado-3 el 01/08). Por eso la hoja se
-- usa SOLO como fuente de identidad y edad; la actividad sigue saliendo de
-- los logs.
-- =====================================================================

-- ---------------------------------------------------------------------
-- Filas impresas de la hoja: dueñas/dueños originales del código.
-- Los tres primeros son gaps que la base tenía vacíos.
-- ---------------------------------------------------------------------
UPDATE estudiantes SET nombre_completo = 'Yesli Acosta Delgado', edad = 10
 WHERE codigo_publico = 'tigre-rosado-1'  AND edad IS NULL;

UPDATE estudiantes SET nombre_completo = 'Madison Elisa Ordoñez Mero', edad = 13
 WHERE codigo_publico = 'tigre-rosado-19' AND edad IS NULL;

UPDATE estudiantes SET nombre_completo = 'Michelle Elisabe Quito Moreira', edad = 12
 WHERE codigo_publico = 'tigre-rosado-25' AND edad IS NULL;

-- ---------------------------------------------------------------------
-- Filas manuscritas ("NUEVOS"): niñas/niños incorporados sobre la marcha.
--
-- Billy Navas es directo: la hoja le asigna leon-azul-17 y solo marca el
-- 01/08; la base tiene exactamente una sesión de ese código, el 01/08.
--
-- Emely y Johana entraron el 18/07 usando el código de una compañera y el
-- 01/08 recibieron código propio (columna "NUEVOS" de la hoja). La base lo
-- respalda: el 01/08, entre las 11:18 y las 11:32, hay CINCO códigos
-- tigre-rosado distintos con una sesión cada uno del mismo ejercicio
-- (ej_003) — -1, -7, -9, -11 y -19 — es decir, cinco niñas distintas a la
-- vez. Eso solo cuadra si Emely y Johana ya usaban su código propio.
-- ---------------------------------------------------------------------
UPDATE estudiantes SET nombre_completo = 'Billy Navas', edad = 10
 WHERE codigo_publico = 'leon-azul-17' AND edad IS NULL;

UPDATE estudiantes
   SET nombre_completo    = 'Emely Nazareno', edad = 12,
       notas_investigador = 'Hoja de asistencia: ingresó el 18/07 usando '
                            || 'tigre-rosado-1; el 01/08 recibió código propio.'
 WHERE codigo_publico = 'tigre-rosado-7' AND edad IS NULL;

UPDATE estudiantes
   SET nombre_completo    = 'Johana Mina', edad = 12,
       notas_investigador = 'Hoja de asistencia: ingresó el 18/07 usando '
                            || 'tigre-rosado-19; el 01/08 recibió código propio.'
 WHERE codigo_publico = 'tigre-rosado-9' AND edad IS NULL;

-- ---------------------------------------------------------------------
-- NO SE APLICA — queda documentado por qué:
--
-- · tigre-rosado-11 (1 sesión el 01/08, ej_003, 12 turnos, cerrada) NO
--   aparece en la hoja, ni impreso ni manuscrito. Su dueña original según
--   el padrón Excel sería Arlett Elizabeth Gamboa Guevara, pero ese padrón
--   ya demostró estar desactualizado (sus nombres por código no coinciden
--   con los de la base en al menos 4 casos). Se deja `edad IS NULL`.
--
-- · tigre-rosado-6 y tigre-rosado-10 (códigos "NUEVOS" de Valentina y
--   Danna) tienen CERO sesiones: se asignaron pero nunca se usaron. No
--   afectan al análisis.
--
-- · Las dos sesiones del 18/07 de tigre-rosado-1 y las tres de
--   tigre-rosado-19 quedan atribuidas a la dueña impresa del código
--   (Yesli, Madison), que la hoja marca presente ese día. La hoja también
--   apunta a Emely y Johana en esos códigos el 18/07: la contradicción no
--   se puede resolver desde los logs. Son 5 de 102 sesiones y las edades
--   en disputa difieren en 1-2 años (10 vs 12; 13 vs 12), así que no mueve
--   ningún agregado. Ver §Sensibilidad en ANALISIS.md.
-- ---------------------------------------------------------------------
