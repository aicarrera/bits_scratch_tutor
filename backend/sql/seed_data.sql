-- Grupo demo
INSERT INTO grupos (id, nombre, descripcion) VALUES
  ('00000000-0000-0000-0000-000000000001', 'CreaBits Demo', 'Grupo local para pruebas')
ON CONFLICT DO NOTHING;

-- Estudiantes demo
-- nombre_completo y email_referencia son opcionales y solo los ve el profe/investigador
INSERT INTO estudiantes (codigo_publico, grupo_id, nombre_completo, email_referencia, edad, genero_opcion, experiencia_scratch, experiencia_ia) VALUES
  ('tigre-azul-7',  '00000000-0000-0000-0000-000000000001', 'Estudiante Demo 1', NULL, 9,  'prefiero_no_decir', 'un_poco',  'ninguna'),
  ('demo-ia-1',     '00000000-0000-0000-0000-000000000001', 'Estudiante Demo 2', NULL, 10, 'prefiero_no_decir', 'ninguna',  'alguna'),
  ('leon-rojo-3',   '00000000-0000-0000-0000-000000000001', 'Estudiante Demo 3', NULL, 8,  'prefiero_no_decir', 'ninguna',  'ninguna')
ON CONFLICT (codigo_publico) DO NOTHING;

-- Categorías
INSERT INTO categorias_juego (id, nombre, icono, color_hex, orden) VALUES
  ('animaciones', 'Animaciones', '🎬', '#E91E63', 1),
  ('juegos',      'Juegos',      '🎮', '#7EC242', 2),
  ('historias',   'Historias',   '📖', '#FF8C42', 3),
  ('libre',       'Libre',       '✨', '#9B59B6', 4)
ON CONFLICT (id) DO NOTHING;

-- Juegos
INSERT INTO juegos (id, categoria_id, titulo, icono, descripcion_corta, duracion_estimada_min, es_proyecto_libre) VALUES
  ('ej_001',        'animaciones', 'Haz bailar al gato',          '🐱', 'Anima un personaje para que baile con música.',        20, false),
  ('ej_002',        'animaciones', 'Mariposa cambia de disfraz',  '🦋', 'Crea una animación suave usando disfraces.',           15, false),
  ('ej_003',        'juegos',      'Atrapa la estrella',          '⭐', 'Mueve un personaje y suma puntos al tocar estrellas.', 25, false),
  ('ej_004',        'juegos',      'Salta obstáculos',            '🟩', 'Programa un salto y evita objetos que se acercan.',    30, false),
  ('ej_005',        'historias',   'Diálogo entre personajes',    '💬', 'Haz que dos personajes conversen en orden.',           20, false),
  ('ej_006',        'historias',   'Historia con escenarios',     '🏞️', 'Cambia fondos para contar una historia.',              25, false),
  ('proyecto_libre','libre',       'Proyecto libre',              '🚀', 'Crea una idea propia con ayuda de Bit.',               NULL, true)
ON CONFLICT (id) DO NOTHING;

-- Versiones de juego (v1 para cada juego)
INSERT INTO versiones_juego (juego_id, version, instruccion_nino, objetivos_pedagogicos, pistas_progresivas, criterios_completado, preguntas_frecuentes_esperadas, system_prompt) VALUES

('ej_001', 'v1',
 '¡Vamos a hacer bailar al gato! Primero piensa: ¿qué bloque hace que el programa empiece?',
 '["Usar evento bandera verde","Mover y girar el personaje","Usar repetición para animar"]',
 '["Fíjate en la categoría Eventos para arrancar el programa.","En Movimiento hay bloques que giran y mueven al gato.","Para que baile de verdad, usa Repetir de la categoría Control."]',
 '["El estudiante explica su avance con sus propias palabras","El proyecto tiene al menos una acción visible al ejecutarse"]',
 '["¿Qué bloque inicio?","¿Cómo hago que se mueva?","¿Cómo lo repito?"]',
 'Eres Bit, tutor de Scratch para niños de 8 a 10 años. Responde en español simple y animado. Usa la estrategia Hint Progression. Nunca des la solución completa. Escala las pistas de vaga a concreta. Una o dos oraciones por turno, máximo un emoji.

Este ejercicio enseña: eventos (bandera verde), movimiento (mover pasos, girar), control (repetir veces). Bloques clave: eventos_bandera_verde, movimiento_mover_pasos, movimiento_girar_derecha_grados, control_repetir_veces, control_por_siempre.'),

('ej_002', 'v1',
 '¡Vamos a animar una mariposa cambiando sus disfraces! ¿Dónde crees que están los disfraces?',
 '["Usar disfraces para animar","Agregar pausas para suavizar la animación"]',
 '["Los disfraces viven en la categoría Apariencia.","Para que la animación se vea bien, agrega un Esperar entre cambios de disfraz.","Prueba: siguiente disfraz → esperar → siguiente disfraz. ¿Qué pasa?"]',
 '["El estudiante explica su avance con sus propias palabras","El proyecto tiene al menos una acción visible al ejecutarse"]',
 '["¿Dónde están los disfraces?","¿Cómo la animo?","¿Por qué se ve raro?"]',
 'Eres Bit, tutor de Scratch para niños de 8 a 10 años. Responde en español simple y animado. Usa la estrategia Hint Progression. Nunca des la solución completa. Escala las pistas de vaga a concreta. Una o dos oraciones por turno, máximo un emoji.

Este ejercicio enseña: apariencia (siguiente disfraz), control (esperar, por siempre). Bloques clave: apariencia_siguiente_disfraz, apariencia_cambiar_disfraz, control_esperar_segundos, control_por_siempre, eventos_bandera_verde.'),

('ej_003', 'v1',
 '¡Vamos a crear un juego donde tu personaje atrapa estrellas! ¿Cómo harías que se mueva con las flechas?',
 '["Controlar personaje con teclas","Detectar colisión con objeto","Usar variable para puntaje"]',
 '["Para las flechas, busca en Eventos un bloque que reaccione a teclas.","Para detectar si tocas la estrella, mira la categoría Sensores.","Los puntos se guardan en una Variable que va subiendo cuando tocas la estrella."]',
 '["El estudiante explica su avance con sus propias palabras","El proyecto tiene al menos una acción visible al ejecutarse"]',
 '["¿Cómo me muevo con flechas?","¿Cómo cuento puntos?","¿Cómo sé si toco la estrella?"]',
 'Eres Bit, tutor de Scratch para niños de 8 a 10 años. Responde en español simple y animado. Usa la estrategia Hint Progression. Nunca des la solución completa. Escala las pistas de vaga a concreta. Una o dos oraciones por turno, máximo un emoji.

Este ejercicio enseña: eventos (tecla presionada), movimiento (cambiar x/y), sensores (tocando), variables (cambiar). Bloques clave: eventos_tecla_presionada, movimiento_cambiar_x, movimiento_cambiar_y, sensores_tocando, variables_boton_crear, variables_cambiar, control_por_siempre.'),

('ej_004', 'v1',
 '¡Vamos a crear un juego de saltar obstáculos! Primero imagina: ¿cómo sube y baja el personaje al saltar?',
 '["Programar un salto con gravedad simple","Mover obstáculos automáticamente","Detectar colisión para terminar el juego"]',
 '["Para saltar, la posición Y del personaje tiene que subir y luego bajar.","Los obstáculos se mueven solos usando Por Siempre y cambiando su posición X.","Para detectar si chocas, usa el bloque Tocando del sensor."]',
 '["El estudiante explica su avance con sus propias palabras","El proyecto tiene al menos una acción visible al ejecutarse"]',
 '["¿Cómo salto?","¿Cómo muevo el obstáculo?","¿Cómo sé si perdí?"]',
 'Eres Bit, tutor de Scratch para niños de 8 a 10 años. Responde en español simple y animado. Usa la estrategia Hint Progression. Nunca des la solución completa. Escala las pistas de vaga a concreta. Una o dos oraciones por turno, máximo un emoji.

Este ejercicio enseña: movimiento (cambiar y, fijar y), control (por siempre, si entonces), sensores (tocando). Bloques clave: movimiento_cambiar_y, movimiento_fijar_y, control_por_siempre, control_si_entonces, sensores_tocando, eventos_tecla_presionada.'),

('ej_005', 'v1',
 '¡Vamos a crear un diálogo entre dos personajes! Primero decide qué dirá el primero y qué dirá el segundo.',
 '["Hacer hablar personajes en orden","Usar mensajes para coordinar personajes"]',
 '["Para que el personaje hable, busca en Apariencia un bloque que muestre texto.","Para que hablen en orden, el primero debe enviar un mensaje cuando termine.","El segundo personaje empieza cuando recibe ese mensaje."]',
 '["El estudiante explica su avance con sus propias palabras","El proyecto tiene al menos una acción visible al ejecutarse"]',
 '["¿Cómo hablo?","¿Cómo hablan en orden?","¿Qué es un mensaje?"]',
 'Eres Bit, tutor de Scratch para niños de 8 a 10 años. Responde en español simple y animado. Usa la estrategia Hint Progression. Nunca des la solución completa. Escala las pistas de vaga a concreta. Una o dos oraciones por turno, máximo un emoji.

Este ejercicio enseña: apariencia (decir durante segundos), eventos (enviar mensaje, al recibir mensaje). Bloques clave: apariencia_decir_segundos, apariencia_decir, eventos_enviar_mensaje, eventos_enviar_mensaje_y_esperar, eventos_al_recibir_mensaje.'),

('ej_006', 'v1',
 '¡Vamos a contar una historia con distintos escenarios! ¿Cuál será el primer lugar de tu historia?',
 '["Cambiar fondos para narrar escenas","Coordinar personajes y fondos con mensajes"]',
 '["Para cambiar la escena, busca en Apariencia el bloque que cambia el fondo.","Cuando el fondo cambie, el personaje puede decir algo para continuar la historia.","Usa mensajes para que el cambio de escena active acciones de los personajes."]',
 '["El estudiante explica su avance con sus propias palabras","El proyecto tiene al menos una acción visible al ejecutarse"]',
 '["¿Cómo cambio el fondo?","¿Cómo hago que pase algo al cambiar?"]',
 'Eres Bit, tutor de Scratch para niños de 8 a 10 años. Responde en español simple y animado. Usa la estrategia Hint Progression. Nunca des la solución completa. Escala las pistas de vaga a concreta. Una o dos oraciones por turno, máximo un emoji.

Este ejercicio enseña: apariencia (cambiar fondo), eventos (enviar mensaje, al recibir), apariencia (decir). Bloques clave: apariencia_cambiar_fondo, apariencia_decir_segundos, eventos_enviar_mensaje, eventos_al_recibir_mensaje.'),

('proyecto_libre', 'v1',
 '¡Cuéntame qué quieres crear hoy y lo convertimos en pasos pequeños!',
 '["Explorar creativamente Scratch","Dividir ideas en pasos concretos"]',
 '["Primero decide: ¿qué hace tu personaje principal?","Piensa en tres partes: cómo empieza, qué pasa en el medio, cómo termina.","Elige un bloque de Eventos para arrancar tu proyecto y pruébalo."]',
 '["El estudiante explica su avance con sus propias palabras","El proyecto tiene al menos una acción visible al ejecutarse"]',
 '["¿Cómo empiezo?","¿Qué bloque uso para mi idea?"]',
 'Eres Bit, tutor de Scratch para niños de 8 a 10 años. Responde en español simple y animado. Usa la estrategia Hint Progression. Nunca des la solución completa. Escala las pistas de vaga a concreta. Una o dos oraciones por turno, máximo un emoji.

Proyecto libre: adapta las sugerencias a la idea del niño. Ayuda a estructurar: personaje → acción → evento de inicio. Sugiere bloques solo cuando el niño tenga una idea concreta.')

ON CONFLICT (juego_id, version) DO NOTHING;
