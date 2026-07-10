-- Importa estudiantes Nivel 0 al esquema Postgres (Supabase).
-- Formato de codigo_publico (USUARIO): mujeres = tigre-rosado-N, hombres = leon-azul-N.
-- Idempotente: se puede correr varias veces sin duplicar (ON CONFLICT / NOT EXISTS).
-- NOTA: la tabla `estudiantes` no tiene columna de nombre en las migraciones; el nombre
--       real va como comentario y el mapeo autoritativo vive en el Excel (columna USUARIO).

BEGIN;

-- 1) Grupo (idempotente por nombre)
INSERT INTO grupos (id, nombre, descripcion, activo, creado_en)
SELECT gen_random_uuid(), 'ESTUDIANTES NIVEL 0', 'Estudiantes Nivel 0 programa Scratch', true, now()
WHERE NOT EXISTS (SELECT 1 FROM grupos WHERE nombre = 'ESTUDIANTES NIVEL 0');

-- 2) Estudiantes (idempotente por codigo_publico)
INSERT INTO estudiantes (id, codigo_publico, grupo_id, genero_opcion, activo, creado_en)
VALUES
  (gen_random_uuid(), 'tigre-rosado-1', (SELECT id FROM grupos WHERE nombre='ESTUDIANTES NIVEL 0' ORDER BY creado_en LIMIT 1), 'femenino', true, now()),  -- Acosta Delgado Yesli
  (gen_random_uuid(), 'tigre-rosado-2', (SELECT id FROM grupos WHERE nombre='ESTUDIANTES NIVEL 0' ORDER BY creado_en LIMIT 1), 'femenino', true, now()),  -- Alarcon Janeth
  (gen_random_uuid(), 'leon-azul-1', (SELECT id FROM grupos WHERE nombre='ESTUDIANTES NIVEL 0' ORDER BY creado_en LIMIT 1), 'masculino', true, now()),  -- Almeida Mejillones Allan Jair
  (gen_random_uuid(), 'leon-azul-2', (SELECT id FROM grupos WHERE nombre='ESTUDIANTES NIVEL 0' ORDER BY creado_en LIMIT 1), 'masculino', true, now()),  -- Almeida Mejillones Wilmer Jair
  (gen_random_uuid(), 'tigre-rosado-3', (SELECT id FROM grupos WHERE nombre='ESTUDIANTES NIVEL 0' ORDER BY creado_en LIMIT 1), 'femenino', true, now()),  -- Almeida Mejillones Allison Neomy
  (gen_random_uuid(), 'leon-azul-3', (SELECT id FROM grupos WHERE nombre='ESTUDIANTES NIVEL 0' ORDER BY creado_en LIMIT 1), 'masculino', true, now()),  -- Almeida Mejillones Andy Jariel
  (gen_random_uuid(), 'tigre-rosado-4', (SELECT id FROM grupos WHERE nombre='ESTUDIANTES NIVEL 0' ORDER BY creado_en LIMIT 1), 'femenino', true, now()),  -- Alvarado Lañon Keysha Paulette
  (gen_random_uuid(), 'leon-azul-4', (SELECT id FROM grupos WHERE nombre='ESTUDIANTES NIVEL 0' ORDER BY creado_en LIMIT 1), 'masculino', true, now()),  -- Araque Bermúdez Keiner Alexander
  (gen_random_uuid(), 'leon-azul-5', (SELECT id FROM grupos WHERE nombre='ESTUDIANTES NIVEL 0' ORDER BY creado_en LIMIT 1), 'masculino', true, now()),  -- Araque Bermúdez Leonarvis Geremias
  (gen_random_uuid(), 'tigre-rosado-5', (SELECT id FROM grupos WHERE nombre='ESTUDIANTES NIVEL 0' ORDER BY creado_en LIMIT 1), 'femenino', true, now()),  -- Armendariz Magallanes Aisha Samara
  (gen_random_uuid(), 'leon-azul-6', (SELECT id FROM grupos WHERE nombre='ESTUDIANTES NIVEL 0' ORDER BY creado_en LIMIT 1), 'masculino', true, now()),  -- Arroyo Castro Snayder Victor
  (gen_random_uuid(), 'tigre-rosado-6', (SELECT id FROM grupos WHERE nombre='ESTUDIANTES NIVEL 0' ORDER BY creado_en LIMIT 1), 'femenino', true, now()),  -- Astudillo Shirley
  (gen_random_uuid(), 'leon-azul-7', (SELECT id FROM grupos WHERE nombre='ESTUDIANTES NIVEL 0' ORDER BY creado_en LIMIT 1), 'masculino', true, now()),  -- Ayoví Angulo Yeyder Sneyder
  (gen_random_uuid(), 'leon-azul-8', (SELECT id FROM grupos WHERE nombre='ESTUDIANTES NIVEL 0' ORDER BY creado_en LIMIT 1), 'masculino', true, now()),  -- Burbano Cuero Neymar Mateo
  (gen_random_uuid(), 'tigre-rosado-7', (SELECT id FROM grupos WHERE nombre='ESTUDIANTES NIVEL 0' ORDER BY creado_en LIMIT 1), 'femenino', true, now()),  -- Calderon Eliana
  (gen_random_uuid(), 'tigre-rosado-8', (SELECT id FROM grupos WHERE nombre='ESTUDIANTES NIVEL 0' ORDER BY creado_en LIMIT 1), 'femenino', true, now()),  -- Canga Vasconez Scarlett Catalina
  (gen_random_uuid(), 'tigre-rosado-9', (SELECT id FROM grupos WHERE nombre='ESTUDIANTES NIVEL 0' ORDER BY creado_en LIMIT 1), 'femenino', true, now()),  -- Castro Espin Ruth
  (gen_random_uuid(), 'leon-azul-9', (SELECT id FROM grupos WHERE nombre='ESTUDIANTES NIVEL 0' ORDER BY creado_en LIMIT 1), 'masculino', true, now()),  -- Cisneros Fausto
  (gen_random_uuid(), 'leon-azul-10', (SELECT id FROM grupos WHERE nombre='ESTUDIANTES NIVEL 0' ORDER BY creado_en LIMIT 1), 'masculino', true, now()),  -- Cisneros Chancay Laionel
  (gen_random_uuid(), 'tigre-rosado-10', (SELECT id FROM grupos WHERE nombre='ESTUDIANTES NIVEL 0' ORDER BY creado_en LIMIT 1), 'femenino', true, now()),  -- Corozo Estrada Desire
  (gen_random_uuid(), 'leon-azul-11', (SELECT id FROM grupos WHERE nombre='ESTUDIANTES NIVEL 0' ORDER BY creado_en LIMIT 1), 'masculino', true, now()),  -- Delgado Medina Jesús
  (gen_random_uuid(), 'leon-azul-12', (SELECT id FROM grupos WHERE nombre='ESTUDIANTES NIVEL 0' ORDER BY creado_en LIMIT 1), 'masculino', true, now()),  -- Escalante Merchan Edgar Gabriel
  (gen_random_uuid(), 'leon-azul-13', (SELECT id FROM grupos WHERE nombre='ESTUDIANTES NIVEL 0' ORDER BY creado_en LIMIT 1), 'masculino', true, now()),  -- Escalante Merchan Andrés David
  (gen_random_uuid(), 'leon-azul-14', (SELECT id FROM grupos WHERE nombre='ESTUDIANTES NIVEL 0' ORDER BY creado_en LIMIT 1), 'masculino', true, now()),  -- Freire Lirio Alex Sean
  (gen_random_uuid(), 'tigre-rosado-11', (SELECT id FROM grupos WHERE nombre='ESTUDIANTES NIVEL 0' ORDER BY creado_en LIMIT 1), 'femenino', true, now()),  -- Gamboa Guevara Arlett Elizabeth
  (gen_random_uuid(), 'leon-azul-15', (SELECT id FROM grupos WHERE nombre='ESTUDIANTES NIVEL 0' ORDER BY creado_en LIMIT 1), 'masculino', true, now()),  -- Guananga Usca Jose Daniel
  (gen_random_uuid(), 'leon-azul-16', (SELECT id FROM grupos WHERE nombre='ESTUDIANTES NIVEL 0' ORDER BY creado_en LIMIT 1), 'masculino', true, now()),  -- Guerrero Quiñonez Juan Ángel
  (gen_random_uuid(), 'tigre-rosado-12', (SELECT id FROM grupos WHERE nombre='ESTUDIANTES NIVEL 0' ORDER BY creado_en LIMIT 1), 'femenino', true, now()),  -- Guerrero Quiñonez Brittany Noelia
  (gen_random_uuid(), 'leon-azul-17', (SELECT id FROM grupos WHERE nombre='ESTUDIANTES NIVEL 0' ORDER BY creado_en LIMIT 1), 'masculino', true, now()),  -- Herrera Jeremy
  (gen_random_uuid(), 'tigre-rosado-13', (SELECT id FROM grupos WHERE nombre='ESTUDIANTES NIVEL 0' ORDER BY creado_en LIMIT 1), 'femenino', true, now()),  -- Jimenez Paredes Domenica Valentina
  (gen_random_uuid(), 'tigre-rosado-14', (SELECT id FROM grupos WHERE nombre='ESTUDIANTES NIVEL 0' ORDER BY creado_en LIMIT 1), 'femenino', true, now()),  -- Jimenez Paredes Dasha Valentina
  (gen_random_uuid(), 'leon-azul-18', (SELECT id FROM grupos WHERE nombre='ESTUDIANTES NIVEL 0' ORDER BY creado_en LIMIT 1), 'masculino', true, now()),  -- Jonás Samuel
  (gen_random_uuid(), 'tigre-rosado-15', (SELECT id FROM grupos WHERE nombre='ESTUDIANTES NIVEL 0' ORDER BY creado_en LIMIT 1), 'femenino', true, now()),  -- Lino Mite Jurybel
  (gen_random_uuid(), 'tigre-rosado-16', (SELECT id FROM grupos WHERE nombre='ESTUDIANTES NIVEL 0' ORDER BY creado_en LIMIT 1), 'femenino', true, now()),  -- López Odalys
  (gen_random_uuid(), 'leon-azul-19', (SELECT id FROM grupos WHERE nombre='ESTUDIANTES NIVEL 0' ORDER BY creado_en LIMIT 1), 'masculino', true, now()),  -- Luna Beltrán Luis Steven
  (gen_random_uuid(), 'leon-azul-20', (SELECT id FROM grupos WHERE nombre='ESTUDIANTES NIVEL 0' ORDER BY creado_en LIMIT 1), 'masculino', true, now()),  -- Mariscal Ezequiel
  (gen_random_uuid(), 'tigre-rosado-17', (SELECT id FROM grupos WHERE nombre='ESTUDIANTES NIVEL 0' ORDER BY creado_en LIMIT 1), 'femenino', true, now()),  -- Mina Arroyo Johana Jasuri
  (gen_random_uuid(), 'leon-azul-21', (SELECT id FROM grupos WHERE nombre='ESTUDIANTES NIVEL 0' ORDER BY creado_en LIMIT 1), 'masculino', true, now()),  -- Morante Choez Benjamín Daniel
  (gen_random_uuid(), 'leon-azul-22', (SELECT id FROM grupos WHERE nombre='ESTUDIANTES NIVEL 0' ORDER BY creado_en LIMIT 1), 'masculino', true, now()),  -- Morante Choez Ezequiel David
  (gen_random_uuid(), 'leon-azul-23', (SELECT id FROM grupos WHERE nombre='ESTUDIANTES NIVEL 0' ORDER BY creado_en LIMIT 1), 'masculino', true, now()),  -- Moreno Mina Leonel Benjamín
  (gen_random_uuid(), 'leon-azul-24', (SELECT id FROM grupos WHERE nombre='ESTUDIANTES NIVEL 0' ORDER BY creado_en LIMIT 1), 'masculino', true, now()),  -- Mujica Sanchez Xavier Alejandro
  (gen_random_uuid(), 'tigre-rosado-18', (SELECT id FROM grupos WHERE nombre='ESTUDIANTES NIVEL 0' ORDER BY creado_en LIMIT 1), 'femenino', true, now()),  -- Nazareno Moreano Kasandra Emeli
  (gen_random_uuid(), 'tigre-rosado-19', (SELECT id FROM grupos WHERE nombre='ESTUDIANTES NIVEL 0' ORDER BY creado_en LIMIT 1), 'femenino', true, now()),  -- Ordoñez Mero Madison Elisa
  (gen_random_uuid(), 'leon-azul-25', (SELECT id FROM grupos WHERE nombre='ESTUDIANTES NIVEL 0' ORDER BY creado_en LIMIT 1), 'masculino', true, now()),  -- Ordoñez Mero Keiler Antonio
  (gen_random_uuid(), 'tigre-rosado-20', (SELECT id FROM grupos WHERE nombre='ESTUDIANTES NIVEL 0' ORDER BY creado_en LIMIT 1), 'femenino', true, now()),  -- Paredes Lady Jimena
  (gen_random_uuid(), 'tigre-rosado-21', (SELECT id FROM grupos WHERE nombre='ESTUDIANTES NIVEL 0' ORDER BY creado_en LIMIT 1), 'femenino', true, now()),  -- Parrales Kerly
  (gen_random_uuid(), 'leon-azul-26', (SELECT id FROM grupos WHERE nombre='ESTUDIANTES NIVEL 0' ORDER BY creado_en LIMIT 1), 'masculino', true, now()),  -- Pérez Cedeño Thiago Raúl
  (gen_random_uuid(), 'leon-azul-27', (SELECT id FROM grupos WHERE nombre='ESTUDIANTES NIVEL 0' ORDER BY creado_en LIMIT 1), 'masculino', true, now()),  -- Quiñonez Justin
  (gen_random_uuid(), 'tigre-rosado-22', (SELECT id FROM grupos WHERE nombre='ESTUDIANTES NIVEL 0' ORDER BY creado_en LIMIT 1), 'femenino', true, now()),  -- Quiñonez Rodriguez Yelena Valentina
  (gen_random_uuid(), 'tigre-rosado-23', (SELECT id FROM grupos WHERE nombre='ESTUDIANTES NIVEL 0' ORDER BY creado_en LIMIT 1), 'femenino', true, now()),  -- Quiñonez Rodriguez Yahnia Valeska
  (gen_random_uuid(), 'tigre-rosado-24', (SELECT id FROM grupos WHERE nombre='ESTUDIANTES NIVEL 0' ORDER BY creado_en LIMIT 1), 'femenino', true, now()),  -- Quito Elizabeth
  (gen_random_uuid(), 'tigre-rosado-25', (SELECT id FROM grupos WHERE nombre='ESTUDIANTES NIVEL 0' ORDER BY creado_en LIMIT 1), 'femenino', true, now()),  -- Quito Moreira Michelle Elisabe
  (gen_random_uuid(), 'leon-azul-28', (SELECT id FROM grupos WHERE nombre='ESTUDIANTES NIVEL 0' ORDER BY creado_en LIMIT 1), 'masculino', true, now()),  -- Quito Moreira Angel Josue
  (gen_random_uuid(), 'leon-azul-29', (SELECT id FROM grupos WHERE nombre='ESTUDIANTES NIVEL 0' ORDER BY creado_en LIMIT 1), 'masculino', true, now()),  -- Robles Pérez Thiago Alexander
  (gen_random_uuid(), 'leon-azul-30', (SELECT id FROM grupos WHERE nombre='ESTUDIANTES NIVEL 0' ORDER BY creado_en LIMIT 1), 'masculino', true, now()),  -- Rubio Armendariz Natanael Sanider
  (gen_random_uuid(), 'leon-azul-31', (SELECT id FROM grupos WHERE nombre='ESTUDIANTES NIVEL 0' ORDER BY creado_en LIMIT 1), 'masculino', true, now()),  -- Tenorio Rios Angel Daniel
  (gen_random_uuid(), 'leon-azul-32', (SELECT id FROM grupos WHERE nombre='ESTUDIANTES NIVEL 0' ORDER BY creado_en LIMIT 1), 'masculino', true, now()),  -- Ulloa Thiago
  (gen_random_uuid(), 'leon-azul-33', (SELECT id FROM grupos WHERE nombre='ESTUDIANTES NIVEL 0' ORDER BY creado_en LIMIT 1), 'masculino', true, now()),  -- Zambrano Figueroa Isaac
  (gen_random_uuid(), 'leon-azul-34', (SELECT id FROM grupos WHERE nombre='ESTUDIANTES NIVEL 0' ORDER BY creado_en LIMIT 1), 'masculino', true, now())  -- Zambrano Saltos Kenny
ON CONFLICT (codigo_publico) DO NOTHING;

COMMIT;

-- Verificacion rapida:
-- SELECT codigo_publico, genero_opcion FROM estudiantes
--   WHERE grupo_id = (SELECT id FROM grupos WHERE nombre='ESTUDIANTES NIVEL 0' ORDER BY creado_en LIMIT 1)
--   ORDER BY genero_opcion, length(codigo_publico), codigo_publico;
