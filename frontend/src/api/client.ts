import type { Conversation, GamesCatalog, LearningSession, MessageExchange, Student } from "../types/api";

const API_URL = (import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000").replace(/\/$/, "");

type RequestOptions = {
  method?: "GET" | "POST" | "PATCH";
  body?: unknown;
  headers?: Record<string, string>;
};

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    method: options.method ?? "GET",
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
    body: options.body === undefined ? undefined : JSON.stringify(options.body),
  });

  if (!response.ok) {
    const payload = (await response.json().catch(() => null)) as { detail?: string } | null;
    throw new Error(payload?.detail ?? "No se pudo completar la acción.");
  }

  return response.json() as Promise<T>;
}

export const api = {
  async validateCode(codigoPublico: string): Promise<Student> {
    const response = await request<{ estudiante: Student }>("/api/v1/students/validate-code", {
      method: "POST",
      body: { codigo_publico: codigoPublico },
    });
    return response.estudiante;
  },

  createSession(studentId: string): Promise<LearningSession> {
    return request<LearningSession>("/api/v1/sessions", {
      method: "POST",
      body: {
        estudiante_id: studentId,
        asentimiento_aceptado: true,
        version_texto: "asentimiento-v1",
        dispositivo_tipo: "web",
        metadata: { frontend: "vite-react" },
      },
    });
  },

  getGames(): Promise<GamesCatalog> {
    return request<GamesCatalog>("/api/v1/games");
  },

  openConversation(sessionId: string, gameId: string): Promise<Conversation> {
    return request<Conversation>("/api/v1/conversations", {
      method: "POST",
      body: { sesion_id: sessionId, juego_id: gameId },
    });
  },

  sendMessage(conversationId: string, contenido: string): Promise<MessageExchange> {
    return request<MessageExchange>(`/api/v1/conversations/${conversationId}/messages`, {
      method: "POST",
      body: { contenido },
    });
  },

  finishSession(sessionId: string, adminCode: string): Promise<LearningSession> {
    return request<LearningSession>(`/api/v1/sessions/${sessionId}/finish`, {
      method: "POST",
      body: { admin_code: adminCode },
    });
  },

  submitFeedback(sessionId: string, nivel: number, etiqueta: string, comentarioExtra?: string): Promise<void> {
    return request<void>(`/api/v1/sessions/${sessionId}/feedback`, {
      method: "POST",
      body: {
        nivel_satisfaccion: nivel,
        etiqueta,
        comentario_extra: comentarioExtra || null,
      },
    });
  },
};
