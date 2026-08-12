# Análisis del backup para el paper (Tablas 1 y 2)

Reconstrucción del backup de producción en una base SQLite local, definición
del alcance del estudio, análisis de edades y cálculo completo de las dos
tablas que el borrador `sample.tex` dejó vacías.

| | |
|---|---|
| Backup | `Paper/db_cluster-09-08-2026@21-16-40.backup` (pg_dumpall texto, 12 761 líneas) |
| Fuente secundaria | Hoja de asistencia en papel (3 jornadas) — completa 6 de las 7 edades que faltaban |
| Base generada | `Paper/analysis/creabits_paper.db` |
| Reproducir | `python build_sqlite.py && python run_queries.py` |
| Resultados | `out/*.md` y `out/*.csv` (una consulta por archivo) |

---

## 1. Plan ejecutado

1. **ETL** — `build_sqlite.py` parsea los bloques `COPY … FROM stdin` del
   esquema `public` (los esquemas `auth`, `storage`, `realtime` y `vault` son
   infraestructura de Supabase y se descartan), decodifica el formato COPY
   TEXT de PostgreSQL (`\N`, `\t`, `\n`, `\\`, `\xHH`, octales), convierte los
   booleanos `t`/`f` a `1`/`0` y crea 15 tablas + 4 vistas de normalización.
2. **Normalización temporal** — todas las marcas de tiempo del backup son UTC
   con sufijo `+00`, que SQLite no sabe parsear. Las vistas `v_sesiones`,
   `v_conversaciones`, `v_mensajes` y `v_feedback` exponen `*_utc`, `*_local`
   (Ecuador, UTC−5, sin horario de verano) y `fecha_local`.
3. **Alcance** — `sql/00_scope.sql` decide quién y qué entra al análisis.
4. **Consultas** — `sql/01_demografia.sql` (Tabla 1), `sql/02_tabla2.sql`
   (Tabla 2), `sql/03_contexto.sql` (apoyo para §Data Collection y §Results).

### Filas importadas

| Tabla | Filas | | Tabla | Filas |
|---|---:|---|---|---:|
| `estudiantes` | 74 | | `mensajes` | 3 432 |
| `sesiones` | 140 | | `feedback_sesion` | 78 |
| `conversaciones` | 140 | | `eventos` | 645 |
| `juegos` | 7 | | `asentimientos` | 140 |
| `versiones_juego` | 7 | | `grupos` | 2 |

---

## 2. Alcance: qué es "el estudio"

El backup mezcla tres cosas. Solo la tercera es el estudio.

| Origen | Cuentas | Sesiones | Se usa |
|---|---|---:|---|
| Grupo *CreaBits Demo* | `tigre-azul-7`, `demo-ia-1`, `leon-rojo-3` | 28 | ❌ pruebas del equipo |
| Sin grupo (`grupo_id IS NULL`) | `voluntario-1` … `voluntario-10` | 10 | ❌ piloto de voluntarios |
| Grupo **ESTUDIANTES NIVEL 0** | 61 códigos, 28 con actividad | 102 | ✅ **el estudio** |

Las 102 sesiones del grupo NIVEL 0 caen **todas** dentro de los tres sábados, así
que el filtro por grupo y el filtro por fecha coinciden: ningún dato del estudio
se pierde por acotar las fechas, y ninguna prueba del equipo se cuela por grupo.

**Las tres jornadas de recolección** son los tres sábados con actividad masiva
del grupo NIVEL 0 — coincide con lo que dice §Data Collection ("three
consecutive Saturday sessions from 9:00 to 12:00"):

| Jornada | Fecha (local) | Niños | Sesiones | Primera → última sesión |
|---:|---|---:|---:|---|
| 1 | sáb 2026-07-11 | 22 | 47 | 09:52 → 11:48 |
| 2 | sáb 2026-07-18 | 18 | 34 | 09:33 → 11:42 |
| 3 | sáb 2026-08-01 | 18 | 21 | 11:17 → 11:39 |

> Los tres sábados **no son consecutivos**: el 25/07 no hubo jornada. Conviene
> corregir "three consecutive Saturday sessions" → "three Saturday sessions
> over four weeks".
>
> El 01/08 casi todos los niños **reanudaron** una sesión previa en lugar de
> abrir una nueva (15 eventos `session_reactivated`), por eso solo aparecen 21
> filas de sesión nuevas pese a haber 18 niños y 771 mensajes ese día.

### Reasignaciones de código

`estudiantes.notas_investigador` documenta dos reasignaciones:
`tigre-rosado-25b` (Danna Almeida) y `tigre-rosado-8b` (Valentina Jimenez)
usaron el 18/07 el código de una compañera ausente, y el equipo creó una fila
aparte. **Son niñas distintas** de `tigre-rosado-25` y `tigre-rosado-8`, así
que cuentan como participantes propias. Sin esto, el conteo se equivocaría en 2.

---

## 3. Análisis de edades

La base tenía **7 de 28 edades vacías** (25 % de la muestra). La hoja de
asistencia en papel cierra 6 de esas 7.

### Por qué la hoja es fiable

Antes de usarla la validé contra la base: **23 puntos de control, cero
contradicciones.**

- Las **21 edades** que ya estaban en `estudiantes` coinciden una a una con
  las de la hoja.
- Las **2 reasignaciones** que el equipo había anotado en
  `notas_investigador` (`tigre-rosado-8b` Valentina Jimenez 12 y
  `tigre-rosado-25b` Danna Almeida 16) aparecen en la hoja con el mismo
  nombre y la misma edad.

La hoja también explica las cuatro notas impresas ("Antes le pertenecía a
Almeida Mejillones…"): los códigos `leon-azul-1`, `-2`, `-3` y
`tigre-rosado-3` se reasignaron antes de empezar, que es justo la razón por
la que el padrón Excel del repositorio ya no cuadra con la base.

### Qué se tomó de la hoja

| Código | Se completó con | Evidencia |
|---|---|---|
| `tigre-rosado-1` | Yesli Acosta Delgado, 10 | fila impresa, presente las 3 jornadas |
| `tigre-rosado-19` | Madison Elisa Ordoñez Mero, 13 | fila impresa, presente las 3 jornadas |
| `tigre-rosado-25` | Michelle Elisabe Quito Moreira, 12 | fila impresa; ✗ el 18/07, y la base tiene sus 2 sesiones solo el 11/07 |
| `leon-azul-17` | Billy Navas, 10 | manuscrito, solo 01/08; la base tiene exactamente 1 sesión el 01/08 |
| `tigre-rosado-7` | Emely Nazareno, 12 | manuscrito, columna "NUEVOS" |
| `tigre-rosado-9` | Johana Mina, 12 | manuscrito, columna "NUEVOS" |

Los dos últimos merecen justificación, porque la hoja las anota entrando el
18/07 con el código de una compañera y recibiendo código propio después. Los
logs lo confirman: **el 01/08, entre las 11:18 y las 11:32, hay cinco
códigos `tigre-rosado` distintos con una sesión cada uno del mismo ejercicio
(`ej_003`)** — `-1`, `-7`, `-9`, `-11` y `-19`. Son cinco niñas trabajando a
la vez, lo que solo cuadra si Emely y Johana ya usaban su propio código.

### Qué NO se tomó

| | Motivo |
|---|---|
| `tigre-rosado-11` | **No aparece en la hoja**, ni impreso ni manuscrito. 1 sesión el 01/08 (ej_003, 12 turnos, cerrada). Queda como única edad desconocida. |
| `tigre-rosado-6`, `tigre-rosado-10` | Códigos "NUEVOS" de Valentina y Danna: asignados pero con **cero sesiones**. No afectan nada. |
| Las marcas de asistencia como medida de actividad | La hoja registra presencia física, no uso de Bit: 4 niños marcados presentes no abrieron sesión ese día (`leon-azul-2`, `leon-azul-16`, `tigre-rosado-12` el 18/07; `tigre-rosado-3` el 01/08). La actividad sale siempre de los logs. |
| Identidad de `tigre-rosado-1` y `-19` el 18/07 | Contradicción irresoluble: la hoja marca presentes a las dueñas (Yesli, Madison) **y** apunta a Emely y Johana en esos mismos códigos ese día. Ver sensibilidad abajo. |

### El resultado: la Tabla 1 del borrador era correcta

Con las 6 edades aplicadas, el subconjunto de 10–13 años reproduce
**exactamente** lo que ya tenía `sample.tex`:

| Edad | M | F | Total | Borrador |
|---|---:|---:|---:|---:|
| 10 | 5 | 1 | 6 | 6 ✓ |
| 11 | 7 | 4 | 11 | 11 ✓ |
| 12 | 2 | 4 | 6 | 6 ✓ |
| 13 | 1 | 1 | 2 | 2 ✓ |
| **Total** | **15** | **10** | **25** | **15 / 10 / 25** ✓ |

Es decir: la Tabla 1 se construyó a partir de esta hoja, restringida a
10–13 años. Lo único que hay que ajustar en el texto es que **28 niños usaron
a Bit**, no 25: los 3 que el borrador omitía son los dos de 16 años
(`leon-azul-2` Dustin Zapata, `tigre-rosado-25b` Danna Almeida) y
`tigre-rosado-11`. Aportan 4 de las 102 sesiones.

Con las 27 edades conocidas: media **11.5**, SD **1.55**, mediana **11**,
rango **10–16**.

### Sensibilidad

| | A — todos | B — 10 a 13 (se publica) |
|---|---:|---:|
| Niños | 28 | 25 |
| Sesiones | 102 | 98 |
| Mensajes | 2 802 | 2 738 |
| Turnos/sesión | 13.2 ± 13.3 | 13.5 ± 13.5 |
| Duración/sesión | 13.9 ± 13.8 | 13.8 ± 13.9 |
| Cerradas % | 42.2 | 41.8 |
| Satisfacción | 3.9 ± 1.2 | 3.9 ± 1.2 |

Ningún valor se mueve más de 1 punto porcentual. Lo mismo ocurre con la
ambigüedad de `tigre-rosado-1` / `-19` el 18/07: son 5 de 102 sesiones y las
edades en disputa difieren en 1–2 años (10 vs 12; 13 vs 12), dentro del rango
publicado en ambos casos, así que ni la Tabla 1 ni la Tabla 2 cambian.

---

## 4. Definiciones operativas

Cuatro decisiones que hay que declarar en el paper, porque no son obvias.

**Sesión.** Una fila de `sesiones` = un niño trabajando un ejercicio. El backend
(`open_or_resume`) **reanuda** la sesión existente si no fue cerrada por el
docente, así que 5 sesiones del estudio continuaron en un sábado posterior.

**Duración.** *No* se usa `fin_en − inicio_en`: una sesión queda abierta hasta
que el docente la cierra o el navegador dispara el beacon de abandono, lo que
produce duraciones de hasta 46 155 min (32 días). Se define como la **suma, por
jornada, del lapso entre el primer y el último mensaje** de esa sesión ese día.

**Turno.** Un intercambio niño→Bit. Cada mensaje del niño recibe exactamente una
respuesta del LLM (verificado: 1 350 = 1 350), así que
`turnos = mensajes del niño = respuestas del LLM`. `Messages` por sesión
≈ 2 × turnos + 1 (el mensaje de apertura).

**Mensajes de Bit.** Incluyen el mensaje semilla `instruccion_nino` que el
sistema inserta al abrir cada conversación (`proveedor_llm='system'`): 102 de
los 1 452. Así `Child msg. + Bit msg. = Messages`. Las respuestas realmente
generadas por el LLM son 1 350.

### "Questions": cómo se cuenta

Los niños casi nunca escriben signos de interrogación (solo 44 de 1 350
mensajes), así que contar `?` subestimaría gravemente. Además el **74 % de los
mensajes del niño son toques en un chip** de respuesta rápida, no texto propio.
La clasificación de cada mensaje del niño:

| Clase | n | % | Definición |
|---|---:|---:|---|
| Chip | 1 001 | 74.1 | el texto coincide **exactamente** con una `opciones_respuesta` del mensaje anterior de Bit |
| Texto libre | 349 | 25.9 | el resto (escrito a mano) |
| └ **Petición de ayuda** | **224** | **16.6** | texto libre + léxico interrogativo / de ayuda / de objetivo |

`es_ayuda` (la métrica que se publica como *Questions*) marca un mensaje libre
que contiene: signo `?`/`¿`; interrogativo (`como`, `que`, `cual`, `cuanto`,
`donde`, `quien`, `por que`, incluidas abreviaturas y faltas de ortografía
frecuentes a esta edad — `q`, `k`, `komo`, `xq`); petición explícita
(`ayuda`, `pista`, `dime`, `dame`, `muestrame`, `explica`); señal de bloqueo
(`no entiendo`, `no se`, `no encuentro`, `no me sale`, `no funciona`,
`sigo sin`, `le falta`); enunciado de objetivo dirigido a Bit (`quiero que…`,
`necesito…`); o petición del siguiente paso (`y ahora`, `que mas`, `siguiente
paso`, `como empiezo`).

Se revisaron a mano las 349 clasificaciones. Quedan fuera saludos (`hola`),
asentimientos (`ya`, `si`, `ok`, `gracias`, `listo`) y respuestas de contenido
(`el gato se mueve`, `una casa`, `la bandera verde`). El error residual
estimado es ~2 % (p. ej. `gracias por tu ayuda` cuenta como petición). La
consulta `Q3.5` publica las tres variantes para que el lector pueda recalcular.

---

## 5. TABLA 1 — Demografía (completa)

Cohorte publicada: los **25 niños/as de 10 a 13 años**. Consultas `Q1.3`–`Q1.5`.

| Attribute | Item | Freq | Attribute | Item | Freq |
|---|---|---:|---|---|---:|
| Age | 10 | 6 | Gender | Male | 15 |
| | 11 | 11 | | Female | 10 |
| | 12 | 6 | | Non-specified | 0 |
| | 13 | 2 | | | |
| **Total students** | | **25** | | | |

Idéntica a la que ya tenía el borrador. El único cambio necesario está en el
texto que la introduce, porque **28 niños usaron a Bit**:

> Twenty-eight children used the tutor across the three sessions. Of these,
> 25 were aged 10--13 (Table 1) and form the analysis cohort: 15 boys and 10
> girls, with 11 the most common age. Three further children are excluded
> from the reported figures --- two aged 16, and one whose age could be
> recovered from neither the attendance record nor the system logs. Together
> they account for 4 of the 102 logged sessions, and including them changes
> no value in Table 2 by more than one percentage point.

---

## 6. TABLA 2 — Corpus de interacción (completa)

Valores por sesión: media ± SD (SD muestral, n−1). La columna B es la que se
publica; A se incluye como control.

| | **B — 25 niños (10–13)** | A — los 28 |
|---|---:|---:|
| **Data totals** | | |
| Children | **25** | 28 |
| Sessions | **98** | 102 |
| Messages | **2 738** | 2 802 |
| Child msg. | **1 320** | 1 350 |
| Bit msg. | **1 418** | 1 452 |
| Exercises | **6** | 6 |
| **Per session** | | |
| Turns | **13.5 ± 13.5** | 13.2 ± 13.3 |
| Messages | **27.9 ± 27.1** | 27.5 ± 26.7 |
| Questions | **2.2 ± 2.7** | 2.2 ± 2.7 |
| Duration (min) | **13.8 ± 13.9** | 13.9 ± 13.8 |
| Blocks sugg. | **6.8 ± 7.6** | 6.6 ± 7.5 |
| **Outcomes** | | |
| Closed % | **41.8** | 42.2 |
| Abandoned % | **42.9** | 42.2 |
| Active % | **15.3** | 15.7 |
| Satisf. (1–5) | **3.9 ± 1.2** | 3.9 ± 1.2 |

Notas al pie que conviene incluir:

- *Exercises* = 6 ejercicios del catálogo (`ej_001`…`ej_006`); además 2 sesiones
  usaron *Proyecto libre*, que no es un ejercicio y se excluye del conteo.
  **El borrador decía "4 exercises"; son 6.**
- *Satisf.* se calcula sobre las 60 sesiones (de 98) que registraron feedback
  — 61.2 % de cobertura. Distribución: 1★ 3, 2★ 3, 3★ 17, 4★ 10, 5★ 27.
- La SD alta en *Turns*, *Messages* y *Duration* viene de 13 sesiones que se
  abrieron y nunca produjeron un intercambio. Excluyéndolas (`Q3.9`, n = 85):
  turnos 15.5 ± 13.4, duración 15.9 ± 13.7, cerradas 42.4 %.
- *Bit msg.* incluye el mensaje de apertura sembrado por el sistema (98);
  las respuestas generadas por el LLM son 1 320.

### Cifras pendientes en el borrador

| §Data Collection decía | Real (cohorte publicada) |
|---|---|
| "[81, revisar!!!!] sessions" | **98** (102 contando a los 3 excluidos) |
| "approximately [2,000, revisar!!!] messages" | **2 738** (2 802 con los 3) |
| "across 4 exercises" | **6 ejercicios** + proyecto libre |

---

## 7. Resultados de apoyo (§Results)

Todo lo que sigue sale de la **cohorte publicada** (`v_ms_pub` / `v_msg_pub`):
25 niños/as, 98 sesiones, 2 738 mensajes. No hay ninguna cifra en el paper
calculada sobre una población distinta.

**Por ejercicio** (`Q3.1`) — el gradiente de abandono es el hallazgo más
fuerte para RQ2:

| Ejercicio | Ses. | Niños | Cerradas % | Abandon. % | Turnos | Dur. min |
|---|---:|---:|---:|---:|---:|---:|
| ej_006 Historia con escenarios | 18 | 18 | 72.2 | 11.1 | 14.3 | 9.6 |
| ej_002 Mariposa cambia de disfraz | 20 | 19 | 60.0 | 25.0 | 6.5 | 6.1 |
| ej_001 Haz bailar al gato | 24 | 21 | 33.3 | 58.3 | 19.2 | 21.6 |
| ej_003 Atrapa la estrella | 19 | 18 | 31.6 | 47.4 | 19.8 | 22.9 |
| ej_005 Diálogo entre personajes | 14 | 14 | 14.3 | 78.6 | 5.4 | 6.6 |
| ej_004 Salta obstáculos | 1 | 1 | 0 | 100 | 7.0 | 5.6 |

`ej_005` (dos personajes coordinados con mensajes) se abandona en el 79 % de
los intentos tras solo 5 turnos: los niños se van rápido, no se agotan
intentando. `ej_006`, en el otro extremo, se cierra en el 72 % de los casos.

**Por jornada** (`Q3.2`) — la tasa de cierre cae el tercer sábado (43.5 % →
50.0 % → 25.0 %) mientras la duración media sube (13.9 → 9.2 → 20.6 min): el
01/08 casi todos trabajaron `ej_003`, el ejercicio más largo del catálogo.

**Fases pedagógicas de Bit** (`Q3.3`, RQ4) — el andamiaje progresivo se
sostiene en la práctica: `pista` 46.8 %, `predecir` 28.6 %, `confirmar`
10.4 %, `responder` 6.9 %, apertura 6.9 %, `necesita_aclaracion` 0.3 %. Solo
el 7 % de las respuestas entrega directamente la solución.

**Interacción amigable** (`Q3.4`) — 74.7 % de los mensajes del niño son
chips; los 334 escritos a mano promedian 3.7 palabras.

**Cerradas vs abandonadas** (`Q3.10`, RQ3, n = 85 con ≥1 intercambio) —
apenas se distinguen por volumen (14.6 vs 15.7 turnos; 14.1 vs 17.2 min),
pero sí por **cómo** responde el niño: 67.8 % de uso de chips en las cerradas
vs 57.5 % en las abandonadas. Abandonar no es hablar menos, es escribir más
texto libre — señal de que el flujo guiado dejó de funcionar.

**LLM** (`Q3.7`) — las 1 320 respuestas salieron de
`google/gemini-2.5-flash` vía OpenRouter: 4 872 104 tokens de entrada
(3 691 de media) y 266 988 de salida (202 de media).

**Bloques más sugeridos** (`Q3.6`) — `Mover pasos` (95), `Al presionar
bandera verde` (80), `Decir durante segundos` (56), `Siguiente disfraz` (54),
`Cambiar x` (52). 29 bloques distintos, todos validados contra el catálogo.

---

## 8. Limitaciones del dato

1. **Una edad desconocida** (`tigre-rosado-11`, 1 sesión): la base tenía 7
   vacías y la hoja de asistencia cerró 6. La atribución de `tigre-rosado-1` y
   `-19` el 18/07 es ambigua (ver §3), pero afecta a 5 sesiones y a edades que
   difieren en 1–2 años dentro del mismo rango publicado.
2. **Feedback en el 60.8 % de las sesiones**: la media de satisfacción no cubre
   las sesiones abandonadas silenciosamente, que es justo donde cabría esperar
   satisfacción baja → el 3.9 es probablemente un techo optimista.
3. **`activa` es un estado residual**, no un desenlace: son sesiones que
   quedaron abiertas al terminar la jornada (15.7 %). No significa "en curso".
4. **`ej_003` y `ej_004` comparten `descripcion_solucion`** en la tabla
   `juegos` (ambas describen "Atrapa la estrella"): error de carga que afecta
   al prompt del tutor en `ej_004`. Solo 1 sesión lo usó.
5. **La duración es tiempo entre mensajes**, no tiempo dedicado al ejercicio: el
   niño puede estar trabajando en Scratch sin escribirle a Bit.
6. **El roster Excel no sirve como fuente de edades** — no las trae, y sus
   nombres por código ya no coinciden con `estudiantes` (los códigos se
   reasignaron en la práctica). La base es la fuente autoritativa.

---

## 9. Índice de consultas

| Archivo | Consultas |
|---|---|
| `sql/00a_hoja_asistencia.sql` | completa 6 edades desde la hoja en papel (idempotente, documenta lo descartado) |
| `sql/00_scope.sql` | vistas de alcance: `v_jornadas`, `v_sesiones_estudio`, `v_participantes`, `v_conv_estudio`, `v_msg_estudio`, `v_cohorte`, `v_metricas_sesion`, y **`v_ms_pub` / `v_msg_pub`** (la cohorte publicada, de donde sale todo lo que se reporta) |
| `sql/01_demografia.sql` | `padron`, `cobertura_edad`, `tabla1_edad`, `tabla1_genero`, `tabla1_cruce`, `edad_stats`, `edad_mediana`, `asistencia`, `jornadas_por_nino` |
| `sql/02_tabla2.sql` | `totales`, `por_sesion`, `outcomes`, `satisfaccion`, `cobertura_feedback`, `satisfaccion_dist`, `tabla2_armada` |
| `sql/03_contexto.sql` | `por_ejercicio`, `por_jornada`, `fases`, `modo_respuesta_nino`, `variantes_questions`, `bloques_top`, `uso_llm`, `reanudaciones`, `tabla2_sin_sesiones_vacias`, `cerradas_vs_abandonadas`, `verificacion_borrador` |

Cada consulta deja su SQL y su resultado en `out/<archivo>.md` y su tabla en
`out/<archivo>__<nombre>.csv`.
