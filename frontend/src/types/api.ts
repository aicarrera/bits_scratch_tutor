export type Student = {
  id: string;
  codigo_publico: string;
  grupo_id: string | null;
  edad: number | null;
  genero_opcion: string | null;
  experiencia_scratch: string | null;
  experiencia_ia: string | null;
  activo: boolean;
  creado_en: string | null;
};

export type LearningSession = {
  id: string;
  estudiante_id: string;
  grupo_id: string | null;
  inicio_en: string | null;
  fin_en: string | null;
  asentimiento_aceptado: boolean;
  dispositivo_tipo: string | null;
  estado: string;
  modo_llm: string;
};

export type GameCategory = {
  id: string;
  nombre: string;
  icono: string | null;
  color_hex: string | null;
  descripcion: string | null;
  orden: number;
};

export type Game = {
  id: string;
  categoria_id: string | null;
  titulo: string;
  icono: string | null;
  descripcion_corta: string | null;
  duracion_estimada_min: number | null;
  es_proyecto_libre: boolean;
  instruccion_nino: string;
  version_juego_id: string | null;
  version: string | null;
  objetivos_pedagogicos: unknown[];
  color_acento: string | null;
};

export type GamesCatalog = {
  categorias: GameCategory[];
  juegos: Game[];
};

export type BloqueSugerido = {
  id: string;
  imagen: string;
  nombre: string | null;
};

export type TutorFase = "predecir" | "pista" | "confirmar" | "responder" | "explorar";

export type ChatMessage = {
  id: string;
  conversacion_id: string;
  sesion_id: string;
  estudiante_id: string;
  rol: "nino" | "tutor" | "sistema";
  contenido: string;
  orden_mensaje: number;
  creado_en: string | null;
  proveedor_llm: string | null;
  modelo_llm: string | null;
  prompt_version: string | null;
  input_tokens: number | null;
  output_tokens: number | null;
  metadata: Record<string, unknown>;
  fase: TutorFase | null;
  bloques_sugeridos: BloqueSugerido[];
};

export type Conversation = {
  id: string;
  sesion_id: string;
  estudiante_id: string;
  juego_id: string;
  version_juego_id: string | null;
  estado: string;
  inicio_en: string | null;
  fin_en: string | null;
  mensajes: ChatMessage[];
};

export type MessageExchange = {
  mensaje_nino: ChatMessage;
  mensaje_tutor: ChatMessage;
};

export type GameCompletionEntry = {
  orden: number;
  sesion_id: string;
  completado_en: string | null;
  conversation: Conversation;
};

export type GameHistoryItem = {
  game_id: string;
  game_titulo: string;
  game_icono: string | null;
  completions: GameCompletionEntry[];
};

export type StudentGameHistory = {
  historial: GameHistoryItem[];
};

export type GameOpenResult = {
  sesion_id: string | null;
  estado_sesion: string | null;
  conversation: Conversation | null;
  ya_completado: boolean;
  historial_completado: Conversation | null;
};
