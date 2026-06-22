CREATE TABLE grupos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre TEXT NOT NULL,
    descripcion TEXT,
    fecha_inicio DATE,
    fecha_fin DATE,
    activo BOOLEAN NOT NULL DEFAULT true,
    creado_en TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX ix_grupos_activo ON grupos (activo);

CREATE TABLE usuarios_app (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT NOT NULL UNIQUE,
    nombre_completo TEXT NOT NULL,
    rol VARCHAR(32) NOT NULL,
    grupo_id UUID REFERENCES grupos(id) ON DELETE SET NULL,
    activo BOOLEAN NOT NULL DEFAULT true,
    creado_en TIMESTAMPTZ NOT NULL DEFAULT now(),
    ultimo_acceso_en TIMESTAMPTZ,
    CONSTRAINT ck_usuarios_app_rol CHECK (rol IN ('researcher','teacher','technical_admin','super_admin'))
);
CREATE INDEX ix_usuarios_app_grupo_id ON usuarios_app (grupo_id);
CREATE INDEX ix_usuarios_app_rol ON usuarios_app (rol);

CREATE TABLE estudiantes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    -- Código pseudónimo visible en la app (ej: "tigre-azul-7")
    codigo_publico TEXT NOT NULL UNIQUE,
    grupo_id UUID REFERENCES grupos(id) ON DELETE SET NULL,
    -- Datos reales del niño — solo accesibles por el profe/investigador, nunca expuestos en la app
    nombre_completo TEXT,
    email_referencia TEXT,
    notas_investigador TEXT,
    -- Datos demográficos anónimos (los llena el niño en el onboarding)
    edad SMALLINT,
    genero_opcion VARCHAR(32),
    experiencia_scratch VARCHAR(32),
    experiencia_ia VARCHAR(32),
    activo BOOLEAN NOT NULL DEFAULT true,
    creado_en TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT ck_estudiantes_edad CHECK (edad IS NULL OR edad BETWEEN 8 AND 10),
    CONSTRAINT ck_estudiantes_genero CHECK (genero_opcion IS NULL OR genero_opcion IN ('femenino','masculino','prefiero_no_decir','otro')),
    CONSTRAINT ck_estudiantes_experiencia_scratch CHECK (experiencia_scratch IS NULL OR experiencia_scratch IN ('ninguna','un_poco','mucha')),
    CONSTRAINT ck_estudiantes_experiencia_ia CHECK (experiencia_ia IS NULL OR experiencia_ia IN ('ninguna','alguna','frecuente'))
);
CREATE INDEX ix_estudiantes_codigo_publico ON estudiantes (codigo_publico);
CREATE INDEX ix_estudiantes_grupo_id ON estudiantes (grupo_id);

CREATE TABLE categorias_juego (
    id TEXT PRIMARY KEY,
    nombre TEXT NOT NULL,
    icono TEXT,
    color_hex TEXT,
    descripcion TEXT,
    orden SMALLINT NOT NULL DEFAULT 0,
    activo BOOLEAN NOT NULL DEFAULT true
);

CREATE TABLE juegos (
    id TEXT PRIMARY KEY,
    categoria_id TEXT REFERENCES categorias_juego(id) ON DELETE SET NULL,
    titulo TEXT NOT NULL,
    icono TEXT,
    descripcion_corta TEXT,
    duracion_estimada_min SMALLINT,
    es_proyecto_libre BOOLEAN NOT NULL DEFAULT false,
    activo BOOLEAN NOT NULL DEFAULT true,
    creado_en TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX ix_juegos_activo ON juegos (activo);
CREATE INDEX ix_juegos_categoria_id ON juegos (categoria_id);

CREATE TABLE versiones_juego (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    juego_id TEXT NOT NULL REFERENCES juegos(id) ON DELETE CASCADE,
    version TEXT NOT NULL,
    instruccion_nino TEXT NOT NULL,
    objetivos_pedagogicos JSON NOT NULL,
    pistas_progresivas JSON NOT NULL,
    criterios_completado JSON NOT NULL,
    preguntas_frecuentes_esperadas JSON NOT NULL,
    system_prompt TEXT NOT NULL,
    activo BOOLEAN NOT NULL DEFAULT true,
    creado_en TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_versiones_juego_juego_version UNIQUE (juego_id, version)
);
CREATE INDEX ix_versiones_juego_juego_id ON versiones_juego (juego_id);
CREATE INDEX ix_versiones_juego_activo ON versiones_juego (activo);

CREATE TABLE sesiones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    estudiante_id UUID NOT NULL REFERENCES estudiantes(id) ON DELETE CASCADE,
    grupo_id UUID REFERENCES grupos(id) ON DELETE SET NULL,
    inicio_en TIMESTAMPTZ NOT NULL DEFAULT now(),
    fin_en TIMESTAMPTZ,
    asentimiento_aceptado BOOLEAN NOT NULL DEFAULT false,
    dispositivo_tipo TEXT,
    estado VARCHAR(16) NOT NULL DEFAULT 'activa',
    modo_llm VARCHAR(16) NOT NULL DEFAULT 'mock',
    metadata JSON NOT NULL,
    CONSTRAINT ck_sesiones_estado CHECK (estado IN ('activa','cerrada','abandonada','anulada'))
);
CREATE INDEX ix_sesiones_estudiante_id ON sesiones (estudiante_id);
CREATE INDEX ix_sesiones_grupo_id ON sesiones (grupo_id);
CREATE INDEX ix_sesiones_inicio_en ON sesiones (inicio_en);

CREATE TABLE asentimientos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sesion_id UUID NOT NULL REFERENCES sesiones(id) ON DELETE CASCADE,
    estudiante_id UUID NOT NULL REFERENCES estudiantes(id) ON DELETE CASCADE,
    version_texto TEXT NOT NULL,
    aceptado BOOLEAN NOT NULL,
    aceptado_en TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX ix_asentimientos_sesion_id ON asentimientos (sesion_id);
CREATE INDEX ix_asentimientos_estudiante_id ON asentimientos (estudiante_id);

CREATE TABLE conversaciones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sesion_id UUID NOT NULL REFERENCES sesiones(id) ON DELETE CASCADE,
    estudiante_id UUID NOT NULL REFERENCES estudiantes(id) ON DELETE CASCADE,
    juego_id TEXT NOT NULL REFERENCES juegos(id) ON DELETE RESTRICT,
    version_juego_id UUID REFERENCES versiones_juego(id) ON DELETE SET NULL,
    estado VARCHAR(16) NOT NULL DEFAULT 'activa',
    inicio_en TIMESTAMPTZ NOT NULL DEFAULT now(),
    fin_en TIMESTAMPTZ,
    metadata JSON NOT NULL,
    CONSTRAINT ck_conversaciones_estado CHECK (estado IN ('activa','cerrada','abandonada'))
);
CREATE INDEX ix_conversaciones_sesion_id ON conversaciones (sesion_id);
CREATE INDEX ix_conversaciones_estudiante_id ON conversaciones (estudiante_id);
CREATE INDEX ix_conversaciones_juego_id ON conversaciones (juego_id);

CREATE TABLE mensajes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversacion_id UUID NOT NULL REFERENCES conversaciones(id) ON DELETE CASCADE,
    sesion_id UUID NOT NULL REFERENCES sesiones(id) ON DELETE CASCADE,
    estudiante_id UUID NOT NULL REFERENCES estudiantes(id) ON DELETE CASCADE,
    rol VARCHAR(16) NOT NULL,
    contenido TEXT NOT NULL,
    orden_mensaje INTEGER NOT NULL,
    creado_en TIMESTAMPTZ NOT NULL DEFAULT now(),
    proveedor_llm TEXT,
    modelo_llm TEXT,
    prompt_version TEXT,
    input_tokens INTEGER,
    output_tokens INTEGER,
    metadata JSON NOT NULL,
    CONSTRAINT uq_mensajes_conversacion_orden UNIQUE (conversacion_id, orden_mensaje),
    CONSTRAINT ck_mensajes_rol CHECK (rol IN ('nino','tutor','sistema')),
    CONSTRAINT ck_mensajes_input_tokens CHECK (input_tokens IS NULL OR input_tokens >= 0),
    CONSTRAINT ck_mensajes_output_tokens CHECK (output_tokens IS NULL OR output_tokens >= 0)
);
CREATE INDEX ix_mensajes_conversacion_id ON mensajes (conversacion_id);
CREATE INDEX ix_mensajes_conversacion_orden ON mensajes (conversacion_id, orden_mensaje);
CREATE INDEX ix_mensajes_estudiante_id ON mensajes (estudiante_id);
CREATE INDEX ix_mensajes_sesion_id ON mensajes (sesion_id);
CREATE INDEX ix_mensajes_creado_en ON mensajes (creado_en);

CREATE TABLE eventos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    estudiante_id UUID REFERENCES estudiantes(id) ON DELETE CASCADE,
    sesion_id UUID REFERENCES sesiones(id) ON DELETE CASCADE,
    conversacion_id UUID REFERENCES conversaciones(id) ON DELETE SET NULL,
    tipo_evento TEXT NOT NULL,
    payload JSON NOT NULL,
    creado_en TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX ix_eventos_tipo_evento ON eventos (tipo_evento);
CREATE INDEX ix_eventos_estudiante_id ON eventos (estudiante_id);
CREATE INDEX ix_eventos_sesion_id ON eventos (sesion_id);
CREATE INDEX ix_eventos_conversacion_id ON eventos (conversacion_id);
CREATE INDEX ix_eventos_creado_en ON eventos (creado_en);

CREATE TABLE feedback_sesion (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sesion_id UUID NOT NULL UNIQUE REFERENCES sesiones(id) ON DELETE CASCADE,
    estudiante_id UUID NOT NULL REFERENCES estudiantes(id) ON DELETE CASCADE,
    nivel_satisfaccion SMALLINT NOT NULL,
    etiqueta TEXT,
    comentario_extra TEXT,
    creado_en TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT ck_feedback_nivel_satisfaccion CHECK (nivel_satisfaccion BETWEEN 1 AND 5)
);
CREATE INDEX ix_feedback_sesion_sesion_id ON feedback_sesion (sesion_id);
CREATE INDEX ix_feedback_sesion_estudiante_id ON feedback_sesion (estudiante_id);
CREATE INDEX ix_feedback_sesion_nivel_satisfaccion ON feedback_sesion (nivel_satisfaccion);

CREATE TABLE exportaciones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    solicitado_por UUID REFERENCES usuarios_app(id) ON DELETE SET NULL,
    formato VARCHAR(8) NOT NULL,
    alcance VARCHAR(32) NOT NULL,
    filtros JSON NOT NULL,
    total_registros INTEGER,
    archivo_path TEXT,
    creado_en TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT ck_exportaciones_formato CHECK (formato IN ('json','csv')),
    CONSTRAINT ck_exportaciones_alcance CHECK (alcance IN ('sesiones','mensajes','feedback','eventos','dataset_completo')),
    CONSTRAINT ck_exportaciones_total CHECK (total_registros IS NULL OR total_registros >= 0)
);
CREATE INDEX ix_exportaciones_solicitado_por ON exportaciones (solicitado_por);
CREATE INDEX ix_exportaciones_creado_en ON exportaciones (creado_en);

CREATE TABLE auditoria (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id UUID REFERENCES usuarios_app(id) ON DELETE SET NULL,
    accion TEXT NOT NULL,
    entidad TEXT NOT NULL,
    entidad_id TEXT,
    detalle JSON NOT NULL,
    creado_en TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX ix_auditoria_usuario_id ON auditoria (usuario_id);
CREATE INDEX ix_auditoria_accion ON auditoria (accion);
CREATE INDEX ix_auditoria_entidad ON auditoria (entidad);
