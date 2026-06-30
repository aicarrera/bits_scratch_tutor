# Consultas de Investigación — CreaBits Tutor

Todas las consultas funcionan directamente en Supabase → SQL Editor o en cualquier cliente PostgreSQL.

---

## ÍNDICE

1. [Completación de juegos](#1-completación-de-juegos)
2. [Sesiones por estudiante](#2-sesiones-por-estudiante)
3. [Análisis de abandono](#3-análisis-de-abandono)
4. [Mensajes y diálogo](#4-mensajes-y-diálogo)
5. [Satisfacción y feedback](#5-satisfacción-y-feedback)
6. [Tokens y uso del LLM](#6-tokens-y-uso-del-llm)
7. [Perfil de estudiantes](#7-perfil-de-estudiantes)
8. [Conversación completa de un juego](#8-conversación-completa-de-un-juego)

---

## 1. Completación de juegos

### 1.1 Estudiantes que completaron un juego específico

Una conversación "cerrada" = el estudiante terminó ese juego.

```sql
SELECT
    e.codigo_publico,
    e.edad,
    e.experiencia_scratch,
    c.inicio_en,
    c.fin_en,
    EXTRACT(EPOCH FROM (c.fin_en - c.inicio_en)) / 60 AS duracion_min
FROM conversaciones c
JOIN estudiantes e ON e.id = c.estudiante_id
WHERE c.juego_id = 'ej_001'
  AND c.estado = 'cerrada'
ORDER BY c.fin_en DESC;
```

### 1.2 Conteo de estudiantes que completaron cada juego

```sql
SELECT
    j.titulo,
    j.id AS juego_id,
    COUNT(DISTINCT c.estudiante_id) AS estudiantes_completaron
FROM juegos j
LEFT JOIN conversaciones c ON c.juego_id = j.id AND c.estado = 'cerrada'
GROUP BY j.id, j.titulo
ORDER BY estudiantes_completaron DESC;
```

### 1.3 Tasa de completación por juego (completadas vs total iniciadas)

```sql
SELECT
    j.titulo,
    j.id AS juego_id,
    COUNT(c.id)                                                   AS total_intentos,
    COUNT(c.id) FILTER (WHERE c.estado = 'cerrada')               AS completadas,
    COUNT(c.id) FILTER (WHERE c.estado = 'abandonada')            AS abandonadas,
    ROUND(
        100.0 * COUNT(c.id) FILTER (WHERE c.estado = 'cerrada')
        / NULLIF(COUNT(c.id), 0), 1
    ) AS tasa_completacion_pct
FROM juegos j
LEFT JOIN conversaciones c ON c.juego_id = j.id
GROUP BY j.id, j.titulo
ORDER BY tasa_completacion_pct DESC NULLS LAST;
```

### 1.4 Cuántos intentos necesitó cada estudiante para completar un juego

Un "intento" = una conversación iniciada para ese juego.

```sql
SELECT
    e.codigo_publico,
    c.juego_id,
    COUNT(c.id)                                         AS total_intentos,
    MIN(c.inicio_en) FILTER (WHERE c.estado = 'cerrada') AS primera_completacion
FROM conversaciones c
JOIN estudiantes e ON e.id = c.estudiante_id
GROUP BY e.codigo_publico, c.juego_id
HAVING COUNT(c.id) FILTER (WHERE c.estado = 'cerrada') > 0
ORDER BY total_intentos DESC;
```

### 1.5 Estudiantes que completaron todos los juegos activos

```sql
SELECT
    e.codigo_publico,
    COUNT(DISTINCT c.juego_id) AS juegos_completados
FROM conversaciones c
JOIN estudiantes e ON e.id = c.estudiante_id
WHERE c.estado = 'cerrada'
GROUP BY e.codigo_publico
HAVING COUNT(DISTINCT c.juego_id) = (
    SELECT COUNT(*) FROM juegos WHERE activo = TRUE AND es_proyecto_libre = FALSE
)
ORDER BY e.codigo_publico;
```

### 1.6 Tiempo promedio para completar cada juego (en minutos)

```sql
SELECT
    j.titulo,
    j.duracion_estimada_min                             AS duracion_estimada,
    ROUND(AVG(
        EXTRACT(EPOCH FROM (c.fin_en - c.inicio_en)) / 60
    )::numeric, 1)                                      AS duracion_real_promedio_min,
    COUNT(c.id)                                         AS n_completaciones
FROM conversaciones c
JOIN juegos j ON j.id = c.juego_id
WHERE c.estado = 'cerrada'
  AND c.fin_en IS NOT NULL
GROUP BY j.id, j.titulo, j.duracion_estimada_min
ORDER BY duracion_real_promedio_min;
```

---

## 2. Sesiones por estudiante

### 2.1 Resumen de sesiones de un estudiante (por código público)

```sql
SELECT
    s.id          AS sesion_id,
    s.inicio_en,
    s.fin_en,
    s.estado      AS estado_sesion,
    s.modo_llm,
    EXTRACT(EPOCH FROM (s.fin_en - s.inicio_en)) / 60 AS duracion_min,
    COUNT(c.id)   AS conversaciones_en_sesion
FROM sesiones s
JOIN estudiantes e ON e.id = s.estudiante_id
LEFT JOIN conversaciones c ON c.sesion_id = s.id
WHERE e.codigo_publico = 'CODIGO_AQUI'
GROUP BY s.id
ORDER BY s.inicio_en DESC;
```

### 2.2 Número de sesiones necesarias antes de completar un juego

Cuenta todas las sesiones que el estudiante tuvo antes de su primera completación de un juego.

```sql
WITH primera_completacion AS (
    SELECT
        c.estudiante_id,
        c.juego_id,
        MIN(c.fin_en) AS completado_en
    FROM conversaciones c
    WHERE c.estado = 'cerrada'
    GROUP BY c.estudiante_id, c.juego_id
)
SELECT
    e.codigo_publico,
    pc.juego_id,
    pc.completado_en,
    COUNT(DISTINCT s.id) AS sesiones_hasta_completar
FROM primera_completacion pc
JOIN estudiantes e ON e.id = pc.estudiante_id
JOIN sesiones s ON s.estudiante_id = pc.estudiante_id
    AND s.inicio_en <= pc.completado_en
GROUP BY e.codigo_publico, pc.juego_id, pc.completado_en
ORDER BY sesiones_hasta_completar DESC;
```

### 2.3 Actividad diaria — sesiones iniciadas por día

```sql
SELECT
    DATE(s.inicio_en AT TIME ZONE 'America/Guayaquil') AS fecha,
    COUNT(DISTINCT s.id)                                AS sesiones,
    COUNT(DISTINCT s.estudiante_id)                     AS estudiantes_activos
FROM sesiones s
GROUP BY fecha
ORDER BY fecha DESC;
```

### 2.4 Estudiantes sin ninguna sesión cerrada (nunca completaron ningún juego)

```sql
SELECT
    e.codigo_publico,
    e.edad,
    e.experiencia_scratch,
    e.creado_en
FROM estudiantes e
WHERE e.activo = TRUE
  AND NOT EXISTS (
      SELECT 1 FROM sesiones s
      WHERE s.estudiante_id = e.id AND s.estado = 'cerrada'
  )
ORDER BY e.creado_en DESC;
```

---

## 3. Análisis de abandono

### 3.1 En qué mensaje del diálogo se abandona cada juego (promedio)

Detecta en qué punto de la conversación los estudiantes se van.

```sql
SELECT
    c.juego_id,
    j.titulo,
    ROUND(AVG(sub.total_mensajes), 1) AS mensajes_promedio_al_abandonar
FROM conversaciones c
JOIN juegos j ON j.id = c.juego_id
JOIN LATERAL (
    SELECT COUNT(*) AS total_mensajes
    FROM mensajes m
    WHERE m.conversacion_id = c.id
) sub ON TRUE
WHERE c.estado = 'abandonada'
GROUP BY c.juego_id, j.titulo
ORDER BY mensajes_promedio_al_abandonar;
```

### 3.2 Diferencia de mensajes: completadas vs abandonadas por juego

```sql
SELECT
    c.juego_id,
    j.titulo,
    ROUND(AVG(sub.total) FILTER (WHERE c.estado = 'cerrada'), 1)    AS msgs_completadas,
    ROUND(AVG(sub.total) FILTER (WHERE c.estado = 'abandonada'), 1) AS msgs_abandonadas
FROM conversaciones c
JOIN juegos j ON j.id = c.juego_id
JOIN LATERAL (
    SELECT COUNT(*) AS total FROM mensajes m WHERE m.conversacion_id = c.id
) sub ON TRUE
GROUP BY c.juego_id, j.titulo
ORDER BY c.juego_id;
```

### 3.3 Juegos con mayor tasa de abandono

```sql
SELECT
    j.titulo,
    COUNT(c.id)                                             AS total_iniciados,
    COUNT(c.id) FILTER (WHERE c.estado = 'abandonada')      AS abandonados,
    ROUND(
        100.0 * COUNT(c.id) FILTER (WHERE c.estado = 'abandonada')
        / NULLIF(COUNT(c.id), 0), 1
    )                                                       AS tasa_abandono_pct
FROM conversaciones c
JOIN juegos j ON j.id = c.juego_id
GROUP BY j.id, j.titulo
ORDER BY tasa_abandono_pct DESC NULLS LAST;
```

---

## 4. Mensajes y diálogo

### 4.1 Total de mensajes por conversación con ratio niño/tutor

```sql
SELECT
    c.id          AS conversacion_id,
    e.codigo_publico,
    c.juego_id,
    c.estado,
    COUNT(m.id)                                              AS total_mensajes,
    COUNT(m.id) FILTER (WHERE m.rol = 'nino')               AS mensajes_nino,
    COUNT(m.id) FILTER (WHERE m.rol = 'tutor')              AS mensajes_tutor,
    ROUND(
        1.0 * COUNT(m.id) FILTER (WHERE m.rol = 'nino')
        / NULLIF(COUNT(m.id) FILTER (WHERE m.rol = 'tutor'), 0), 2
    )                                                        AS ratio_nino_tutor
FROM conversaciones c
JOIN estudiantes e ON e.id = c.estudiante_id
LEFT JOIN mensajes m ON m.conversacion_id = c.id
GROUP BY c.id, e.codigo_publico, c.juego_id, c.estado
ORDER BY total_mensajes DESC;
```

### 4.2 Longitud promedio de los mensajes del niño vs el tutor

Útil para analizar qué tan elaboradas son las respuestas.

```sql
SELECT
    c.juego_id,
    m.rol,
    ROUND(AVG(LENGTH(m.contenido)), 0) AS longitud_promedio_chars,
    COUNT(m.id)                        AS total_mensajes
FROM mensajes m
JOIN conversaciones c ON c.id = m.conversacion_id
WHERE m.rol IN ('nino', 'tutor')
GROUP BY c.juego_id, m.rol
ORDER BY c.juego_id, m.rol;
```

### 4.3 Conversaciones con más mensajes del niño que del tutor

Indica sesiones de mayor participación activa.

```sql
SELECT
    e.codigo_publico,
    c.juego_id,
    c.estado,
    COUNT(m.id) FILTER (WHERE m.rol = 'nino')  AS msgs_nino,
    COUNT(m.id) FILTER (WHERE m.rol = 'tutor') AS msgs_tutor
FROM conversaciones c
JOIN estudiantes e ON e.id = c.estudiante_id
JOIN mensajes m ON m.conversacion_id = c.id
GROUP BY c.id, e.codigo_publico, c.juego_id, c.estado
HAVING COUNT(m.id) FILTER (WHERE m.rol = 'nino')
     > COUNT(m.id) FILTER (WHERE m.rol = 'tutor')
ORDER BY msgs_nino DESC;
```

---

## 5. Satisfacción y feedback

### 5.1 Satisfacción promedio por juego (estudiantes que completaron)

```sql
SELECT
    c.juego_id,
    j.titulo,
    ROUND(AVG(f.nivel_satisfaccion), 2) AS satisfaccion_promedio,
    COUNT(f.id)                         AS respuestas
FROM feedback_sesion f
JOIN sesiones s ON s.id = f.sesion_id
JOIN conversaciones c ON c.sesion_id = s.id AND c.estado = 'cerrada'
JOIN juegos j ON j.id = c.juego_id
GROUP BY c.juego_id, j.titulo
ORDER BY satisfaccion_promedio DESC;
```

### 5.2 Distribución de satisfacción (1 a 5 estrellas)

```sql
SELECT
    nivel_satisfaccion AS estrellas,
    COUNT(*)           AS cantidad,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct
FROM feedback_sesion
GROUP BY nivel_satisfaccion
ORDER BY nivel_satisfaccion;
```

### 5.3 Feedback con comentario escrito

```sql
SELECT
    e.codigo_publico,
    f.nivel_satisfaccion,
    f.etiqueta,
    f.comentario_extra,
    f.creado_en
FROM feedback_sesion f
JOIN estudiantes e ON e.id = f.estudiante_id
WHERE f.comentario_extra IS NOT NULL
  AND TRIM(f.comentario_extra) <> ''
ORDER BY f.creado_en DESC;
```

### 5.4 Correlación satisfacción vs completación del juego

```sql
SELECT
    CASE
        WHEN EXISTS (
            SELECT 1 FROM conversaciones c2
            WHERE c2.sesion_id = f.sesion_id AND c2.estado = 'cerrada'
        ) THEN 'completó juego'
        ELSE 'no completó'
    END AS resultado,
    ROUND(AVG(f.nivel_satisfaccion), 2) AS satisfaccion_promedio,
    COUNT(*)                            AS n
FROM feedback_sesion f
GROUP BY resultado;
```

---

## 6. Tokens y uso del LLM

### 6.1 Tokens totales por conversación

```sql
SELECT
    c.id          AS conversacion_id,
    e.codigo_publico,
    c.juego_id,
    c.estado,
    SUM(m.input_tokens)  AS total_input_tokens,
    SUM(m.output_tokens) AS total_output_tokens,
    SUM(COALESCE(m.input_tokens, 0) + COALESCE(m.output_tokens, 0)) AS total_tokens
FROM conversaciones c
JOIN estudiantes e ON e.id = c.estudiante_id
JOIN mensajes m ON m.conversacion_id = c.id
WHERE m.rol = 'tutor'
GROUP BY c.id, e.codigo_publico, c.juego_id, c.estado
ORDER BY total_tokens DESC;
```

### 6.2 Uso de tokens por juego (solo conversaciones cerradas)

```sql
SELECT
    j.titulo,
    c.juego_id,
    COUNT(DISTINCT c.id)             AS conversaciones,
    SUM(m.input_tokens)              AS input_tokens_total,
    SUM(m.output_tokens)             AS output_tokens_total,
    ROUND(AVG(m.output_tokens), 0)   AS output_tokens_promedio_por_mensaje
FROM conversaciones c
JOIN juegos j ON j.id = c.juego_id
JOIN mensajes m ON m.conversacion_id = c.id
WHERE c.estado = 'cerrada'
  AND m.rol = 'tutor'
GROUP BY c.juego_id, j.titulo
ORDER BY output_tokens_total DESC;
```

### 6.3 Modelos LLM utilizados y su frecuencia

```sql
SELECT
    modelo_llm,
    proveedor_llm,
    COUNT(*)                   AS mensajes_generados,
    SUM(output_tokens)         AS total_output_tokens
FROM mensajes
WHERE rol = 'tutor'
  AND modelo_llm IS NOT NULL
GROUP BY modelo_llm, proveedor_llm
ORDER BY mensajes_generados DESC;
```

---

## 7. Perfil de estudiantes

### 7.1 Tasa de completación por nivel de experiencia en Scratch

```sql
SELECT
    e.experiencia_scratch,
    COUNT(DISTINCT e.id)                                                    AS total_estudiantes,
    COUNT(DISTINCT c.estudiante_id) FILTER (WHERE c.estado = 'cerrada')     AS completaron_algun_juego,
    ROUND(
        100.0 * COUNT(DISTINCT c.estudiante_id) FILTER (WHERE c.estado = 'cerrada')
        / NULLIF(COUNT(DISTINCT e.id), 0), 1
    )                                                                       AS pct_completaron
FROM estudiantes e
LEFT JOIN conversaciones c ON c.estudiante_id = e.id
WHERE e.activo = TRUE
GROUP BY e.experiencia_scratch
ORDER BY e.experiencia_scratch;
```

### 7.2 Tasa de completación por edad

```sql
SELECT
    e.edad,
    COUNT(DISTINCT e.id)                                                    AS total_estudiantes,
    COUNT(DISTINCT c.estudiante_id) FILTER (WHERE c.estado = 'cerrada')     AS completaron_algun_juego,
    ROUND(AVG(f.nivel_satisfaccion), 2)                                     AS satisfaccion_promedio
FROM estudiantes e
LEFT JOIN conversaciones c ON c.estudiante_id = e.id
LEFT JOIN sesiones s ON s.estudiante_id = e.id
LEFT JOIN feedback_sesion f ON f.sesion_id = s.id
WHERE e.activo = TRUE
GROUP BY e.edad
ORDER BY e.edad;
```

### 7.3 Experiencia IA vs completación

```sql
SELECT
    e.experiencia_ia,
    COUNT(DISTINCT e.id)                                                    AS total,
    COUNT(DISTINCT c.estudiante_id) FILTER (WHERE c.estado = 'cerrada')     AS completaron,
    ROUND(AVG(
        EXTRACT(EPOCH FROM (c.fin_en - c.inicio_en)) / 60
    ) FILTER (WHERE c.estado = 'cerrada'), 1)                               AS tiempo_promedio_min
FROM estudiantes e
LEFT JOIN conversaciones c ON c.estudiante_id = e.id
GROUP BY e.experiencia_ia
ORDER BY e.experiencia_ia;
```

### 7.4 Ranking de estudiantes por juegos completados

```sql
SELECT
    e.codigo_publico,
    e.edad,
    e.experiencia_scratch,
    COUNT(DISTINCT c.juego_id)          AS juegos_completados,
    ROUND(AVG(f.nivel_satisfaccion), 1) AS satisfaccion_promedio
FROM estudiantes e
JOIN conversaciones c ON c.estudiante_id = e.id AND c.estado = 'cerrada'
LEFT JOIN sesiones s ON s.estudiante_id = e.id
LEFT JOIN feedback_sesion f ON f.sesion_id = s.id
GROUP BY e.id, e.codigo_publico, e.edad, e.experiencia_scratch
ORDER BY juegos_completados DESC, satisfaccion_promedio DESC;
```

---

## 8. Conversación completa de un juego

### Cómo funciona la estructura

```
estudiantes  ──►  conversaciones  ──►  mensajes
   (1)               (N por juego)       (orden_mensaje: 1, 2, 3...)

rol posibles en mensajes:
  'nino'    → lo que escribió el estudiante
  'tutor'   → respuesta del LLM (Bit)
  'sistema' → mensajes de sistema / contexto
```

### 8.1 Conversación completa de un juego para un estudiante (por código público)

Reemplaza `'CODIGO_AQUI'` y `'ej_001'`.

```sql
SELECT
    m.orden_mensaje,
    m.rol,
    m.contenido,
    m.creado_en,
    m.input_tokens,
    m.output_tokens,
    c.estado        AS estado_conversacion,
    c.inicio_en     AS conversacion_inicio,
    c.fin_en        AS conversacion_fin
FROM mensajes m
JOIN conversaciones c ON c.id = m.conversacion_id
JOIN estudiantes e   ON e.id = c.estudiante_id
WHERE e.codigo_publico = 'CODIGO_AQUI'
  AND c.juego_id       = 'ej_001'
ORDER BY c.inicio_en, m.orden_mensaje;
```

### 8.2 Solo la última conversación (el intento más reciente)

```sql
SELECT
    m.orden_mensaje,
    m.rol,
    m.contenido,
    m.creado_en
FROM mensajes m
JOIN conversaciones c ON c.id = m.conversacion_id
JOIN estudiantes e   ON e.id = c.estudiante_id
WHERE e.codigo_publico = 'CODIGO_AQUI'
  AND c.juego_id       = 'ej_001'
  AND c.inicio_en = (
      SELECT MAX(c2.inicio_en)
      FROM conversaciones c2
      JOIN estudiantes e2 ON e2.id = c2.estudiante_id
      WHERE e2.codigo_publico = 'CODIGO_AQUI'
        AND c2.juego_id = 'ej_001'
  )
ORDER BY m.orden_mensaje;
```

### 8.3 Todas las conversaciones de todos los juegos de un estudiante

```sql
SELECT
    c.juego_id,
    j.titulo,
    c.estado,
    c.inicio_en,
    c.fin_en,
    m.orden_mensaje,
    m.rol,
    LEFT(m.contenido, 120) AS contenido_preview,
    m.input_tokens,
    m.output_tokens
FROM mensajes m
JOIN conversaciones c ON c.id = m.conversacion_id
JOIN juegos j         ON j.id = c.juego_id
JOIN estudiantes e    ON e.id = c.estudiante_id
WHERE e.codigo_publico = 'CODIGO_AQUI'
ORDER BY c.inicio_en, m.orden_mensaje;
```

### 8.4 Dataset completo de conversaciones para análisis cualitativo

Exporta todas las conversaciones cerradas con su diálogo completo, listo para análisis.

```sql
SELECT
    e.codigo_publico,
    e.edad,
    e.experiencia_scratch,
    e.experiencia_ia,
    j.titulo                                        AS juego,
    c.id::text                                      AS conversacion_id,
    c.estado,
    c.inicio_en,
    c.fin_en,
    EXTRACT(EPOCH FROM (c.fin_en - c.inicio_en))/60 AS duracion_min,
    m.orden_mensaje,
    m.rol,
    m.contenido,
    m.input_tokens,
    m.output_tokens,
    f.nivel_satisfaccion
FROM conversaciones c
JOIN estudiantes e    ON e.id = c.estudiante_id
JOIN juegos j         ON j.id = c.juego_id
JOIN mensajes m       ON m.conversacion_id = c.id
LEFT JOIN sesiones s  ON s.id = c.sesion_id
LEFT JOIN feedback_sesion f ON f.sesion_id = s.id
WHERE c.estado = 'cerrada'
ORDER BY c.inicio_en, m.orden_mensaje;
```

---

## Referencia rápida de valores en enumeraciones

| Tabla | Columna | Valores posibles |
|---|---|---|
| `conversaciones` | `estado` | `activa` · `cerrada` · `abandonada` |
| `sesiones` | `estado` | `activa` · `cerrada` · `abandonada` · `anulada` |
| `mensajes` | `rol` | `nino` · `tutor` · `sistema` |
| `estudiantes` | `experiencia_scratch` | `ninguna` · `un_poco` · `mucha` |
| `estudiantes` | `experiencia_ia` | `ninguna` · `alguna` · `frecuente` |
| `estudiantes` | `genero_opcion` | `femenino` · `masculino` · `prefiero_no_decir` · `otro` |
| `feedback_sesion` | `nivel_satisfaccion` | `1` a `5` |

## IDs de juegos (seed)

| ID | Título |
|---|---|
| `ej_001` | Primer juego / ejercicio 1 |
| `ej_002` | Ejercicio 2 |
| `ej_003` | Ejercicio 3 |
| `ej_004` | Ejercicio 4 |
| `ej_005` | Ejercicio 5 |
| `ej_006` | Ejercicio 6 |
| `proyecto_libre` | Proyecto libre |
