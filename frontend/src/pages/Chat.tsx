import { useEffect, useRef, useState } from "react";

import { api } from "../api/client";
import { BitRobot } from "../components/BitRobot";
import { Header } from "../components/Header";
import type {
  BloqueSugerido,
  ChatMessage,
  Conversation,
  Game,
  GameHistoryItem,
  Student,
  StudentGameHistory,
} from "../types/api";

type ChatProps = {
  student: Student;
  sessionId: string;
  game: Game;
  conversation: Conversation;
  onConversationUpdated: (conversation: Conversation) => void;
  onBack: () => void;
  onFinished: () => void;
  onAbandoned: () => void;
};

const FASE_LABELS: Record<string, string> = {
  predecir: "¿Qué crees que hace?",
  pista: "Pista",
  confirmar: "¡Así se hace!",
  responder: "",
  explorar: "Piénsalo",
};

const FASE_COLORS: Record<string, string> = {
  predecir: "bg-purple-100 text-purple-700",
  pista: "bg-yellow-100 text-yellow-700",
  confirmar: "bg-green-100 text-green-700",
  responder: "",
  explorar: "bg-blue-100 text-blue-700",
};

const ORDINALS = ["Primera", "Segunda", "Tercera", "Cuarta", "Quinta", "Sexta", "Séptima", "Octava", "Novena", "Décima"];

function ordinalLabel(n: number): string {
  return n <= 10 ? `${ORDINALS[n - 1]} vez` : `${n}.ª vez`;
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString("es-ES", { day: "numeric", month: "short" });
}

function BlockCard({ bloque }: { bloque: BloqueSugerido }) {
  const [imgError, setImgError] = useState(false);
  const imgSrc = `/bloques/${bloque.imagen}.png`;

  return (
    <div className="inline-flex flex-col items-center bg-white border-2 border-indigo-100 rounded-xl p-2 shadow-sm min-w-22.5 max-w-27.5">
      {!imgError ? (
        <img
          src={imgSrc}
          alt={bloque.nombre ?? bloque.id}
          className="w-20 h-14 object-contain"
          onError={() => setImgError(true)}
        />
      ) : (
        <div className="w-20 h-14 flex items-center justify-center bg-indigo-50 rounded-lg text-2xl">
          🧩
        </div>
      )}
      <span className="text-[10px] text-center text-gray-600 mt-1 leading-tight">
        {bloque.nombre ?? bloque.id}
      </span>
    </div>
  );
}

function TutorMessage({ message }: { message: ChatMessage }) {
  const faseLabel = message.fase ? FASE_LABELS[message.fase] : "";
  const faseColor = message.fase ? FASE_COLORS[message.fase] : "";
  const hasBloques = message.bloques_sugeridos.length > 0;

  return (
    <div className="flex gap-3 justify-start fade-in">
      <div className="shrink-0">
        <BitRobot size={48} animated={false} />
      </div>
      <div className="max-w-[80%] space-y-2">
        {faseLabel && (
          <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${faseColor}`}>
            {faseLabel}
          </span>
        )}
        <div className="bg-white border-2 border-gray-100 px-5 py-3 rounded-lg shadow-sm text-gray-800">
          <p className="text-base leading-relaxed">{message.contenido}</p>
        </div>
        {hasBloques && (
          <div className="flex flex-wrap gap-2 pt-1">
            {message.bloques_sugeridos.map((bloque) => (
              <BlockCard key={bloque.id} bloque={bloque} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function HistoryPanel({
  student,
  currentGameId,
  onClose,
}: {
  student: Student;
  currentGameId: string;
  onClose: () => void;
}) {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<StudentGameHistory | null>(null);
  const [expandedGame, setExpandedGame] = useState<string | null>(currentGameId);
  const [expandedCompletion, setExpandedCompletion] = useState<string | null>(null);

  useEffect(() => {
    api
      .getGameHistory(student.id)
      .then((result) => setData(result))
      .catch(() => setData({ historial: [] }))
      .finally(() => setLoading(false));
  }, [student.id]);

  return (
    <div className="flex flex-col h-full">
      {/* Panel header */}
      <div className="flex items-center justify-between px-3 py-2 border-b-2 border-gray-100 bg-indigo-50 shrink-0">
        <span className="text-xs font-bold text-indigo-700">📜 Historial de juegos</span>
        <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-lg leading-none">
          ✕
        </button>
      </div>

      {/* Panel content */}
      <div className="flex-1 overflow-y-auto p-2">
        {loading ? (
          <p className="text-center text-gray-400 text-xs py-6 animate-pulse">Cargando...</p>
        ) : !data || data.historial.length === 0 ? (
          <div className="text-center py-8 px-3">
            <div className="text-3xl mb-2">🏆</div>
            <p className="text-gray-400 text-xs">Aún no has terminado ningún juego.</p>
            <p className="text-gray-300 text-[10px] mt-1">Los juegos completados con tu profe aparecerán aquí.</p>
          </div>
        ) : (
          <div className="space-y-1">
            {data.historial.map((item: GameHistoryItem) => (
              <div key={item.game_id} className="border border-gray-100 rounded-lg overflow-hidden">
                {/* Game row */}
                <button
                  onClick={() => setExpandedGame(expandedGame === item.game_id ? null : item.game_id)}
                  className={`w-full flex items-center gap-2 px-3 py-2 text-left hover:bg-gray-50 transition ${
                    item.game_id === currentGameId ? "bg-indigo-50" : "bg-white"
                  }`}
                >
                  <span className="text-base shrink-0">{item.game_icono ?? "🎮"}</span>
                  <span className="flex-1 text-xs font-semibold text-gray-700 truncate">{item.game_titulo}</span>
                  <span className="text-[10px] text-indigo-500 shrink-0 font-medium">
                    {item.completions.length}✓
                  </span>
                  <span className="text-gray-400 text-xs shrink-0">
                    {expandedGame === item.game_id ? "▾" : "▸"}
                  </span>
                </button>

                {/* Completions list */}
                {expandedGame === item.game_id && (
                  <div className="bg-gray-50 border-t border-gray-100">
                    {item.completions.map((completion) => (
                      <div key={completion.sesion_id} className="border-b border-gray-100 last:border-0">
                        {/* Completion row */}
                        <button
                          onClick={() =>
                            setExpandedCompletion(
                              expandedCompletion === completion.sesion_id ? null : completion.sesion_id
                            )
                          }
                          className="w-full flex items-center gap-2 px-4 py-1.5 text-left hover:bg-indigo-50 transition"
                        >
                          <span className="text-[10px] font-semibold text-indigo-600 flex-1">
                            {ordinalLabel(completion.orden)}
                          </span>
                          {completion.completado_en && (
                            <span className="text-[10px] text-gray-400">
                              {formatDate(completion.completado_en)}
                            </span>
                          )}
                          <span className="text-gray-400 text-xs">
                            {expandedCompletion === completion.sesion_id ? "▾" : "▸"}
                          </span>
                        </button>

                        {/* Messages from that completion */}
                        {expandedCompletion === completion.sesion_id && (
                          <div className="max-h-56 overflow-y-auto px-3 pb-2 space-y-1 bg-white border-t border-indigo-100">
                            <p className="text-[9px] text-gray-400 pt-2 pb-1 font-semibold uppercase tracking-wide">
                              Conversación — {ordinalLabel(completion.orden)}
                            </p>
                            {completion.conversation.mensajes.map((msg) => (
                              <div
                                key={msg.id}
                                className={`flex ${msg.rol === "nino" ? "justify-end" : "justify-start"}`}
                              >
                                <div
                                  className={`max-w-[90%] px-2 py-1 rounded text-[10px] leading-snug ${
                                    msg.rol === "nino"
                                      ? "bg-[#FF8C42]/20 text-orange-800"
                                      : "bg-gray-100 text-gray-700"
                                  }`}
                                >
                                  {msg.contenido}
                                </div>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export function Chat({
  student,
  sessionId,
  game,
  conversation,
  onConversationUpdated,
  onBack,
  onFinished,
  onAbandoned,
}: ChatProps) {
  const [messages, setMessages] = useState<ChatMessage[]>(conversation.mensajes);
  const [input, setInput] = useState("");
  const [typing, setTyping] = useState(false);
  const [finishOpen, setFinishOpen] = useState(false);
  const [adminCode, setAdminCode] = useState("");
  const [finishError, setFinishError] = useState("");
  const [finishLoading, setFinishLoading] = useState(false);
  const [abandonLoading, setAbandonLoading] = useState(false);
  const [historialOpen, setHistorialOpen] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, typing]);

  const sendMessage = async () => {
    const text = input.trim();
    if (!text || typing) return;
    setInput("");
    setTyping(true);

    const tempId = `optimistic-${Date.now()}`;
    const optimisticChild: ChatMessage = {
      id: tempId,
      conversacion_id: conversation.id,
      sesion_id: sessionId,
      estudiante_id: student.id,
      rol: "nino",
      contenido: text,
      orden_mensaje: messages.length + 1,
      creado_en: new Date().toISOString(),
      proveedor_llm: null,
      modelo_llm: null,
      prompt_version: null,
      input_tokens: null,
      output_tokens: null,
      metadata: {},
      fase: null,
      bloques_sugeridos: [],
    };
    setMessages((prev) => [...prev, optimisticChild]);

    try {
      const exchange = await api.sendMessage(conversation.id, text);
      const updatedMessages = [...messages, exchange.mensaje_nino, exchange.mensaje_tutor];
      setMessages((prev) => {
        const base = prev.filter((m) => m.id !== tempId);
        return [...base, exchange.mensaje_nino, exchange.mensaje_tutor];
      });
      onConversationUpdated({ ...conversation, mensajes: updatedMessages });
    } catch {
      const fallback: ChatMessage = {
        id: `local-error-${Date.now()}`,
        conversacion_id: conversation.id,
        sesion_id: sessionId,
        estudiante_id: student.id,
        rol: "tutor",
        contenido: "No pude guardar ese mensaje. Pídele ayuda a tu profe y probemos otra vez.",
        orden_mensaje: messages.length + 2,
        creado_en: new Date().toISOString(),
        proveedor_llm: "frontend",
        modelo_llm: null,
        prompt_version: null,
        input_tokens: null,
        output_tokens: null,
        metadata: { local_error: true },
        fase: null,
        bloques_sugeridos: [],
      };
      setMessages((prev) => {
        const base = prev.filter((m) => m.id !== tempId);
        return [...base, optimisticChild, fallback];
      });
    } finally {
      setTyping(false);
    }
  };

  const finishSession = async () => {
    setFinishError("");
    setFinishLoading(true);
    try {
      await api.finishSession(sessionId, adminCode.trim());
      setFinishOpen(false);
      onFinished();
    } catch (caughtError) {
      setFinishError(caughtError instanceof Error ? caughtError.message : "Código de profesor inválido.");
    } finally {
      setFinishLoading(false);
    }
  };

  const handleExit = async () => {
    setAbandonLoading(true);
    try {
      await api.abandonSession(sessionId);
      onAbandoned();
    } catch {
      onAbandoned();
    } finally {
      setAbandonLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col h-screen">
      <Header code={student.codigo_publico} game={game} onExit={() => setFinishOpen(true)} />

      <div className="flex-1 flex overflow-hidden">
        {/* LEFT HISTORY SIDEBAR */}
        <div
          className={`${
            historialOpen ? "w-72" : "w-10"
          } shrink-0 border-r-2 border-gray-100 bg-white transition-all duration-200 flex flex-col overflow-hidden`}
        >
          {historialOpen ? (
            <HistoryPanel
              student={student}
              currentGameId={game.id}
              onClose={() => setHistorialOpen(false)}
            />
          ) : (
            <button
              onClick={() => setHistorialOpen(true)}
              title="Ver historial de juegos completados"
              className="flex-1 flex flex-col items-center justify-center gap-1 hover:bg-indigo-50 transition text-gray-400 hover:text-indigo-600"
            >
              <span className="text-lg">📜</span>
              <span
                className="text-[9px] font-bold tracking-wide text-gray-400 hover:text-indigo-600"
                style={{ writingMode: "vertical-rl", transform: "rotate(180deg)" }}
              >
                Historial
              </span>
            </button>
          )}
        </div>

        {/* MAIN CHAT AREA */}
        <div className="flex-1 overflow-y-auto chat-messages px-4 py-6">
          <div className="max-w-3xl mx-auto space-y-4">
            {messages.map((message) => {
              if (message.rol === "nino") {
                return (
                  <div key={message.id} className="flex gap-3 justify-end fade-in">
                    <div className="max-w-[75%] px-5 py-3 rounded-lg shadow-sm bg-[#FF8C42] text-white">
                      <p className="text-base leading-relaxed">{message.contenido}</p>
                    </div>
                    <div className="shrink-0 w-12 h-12 rounded-full bg-[#FF8C42] flex items-center justify-center text-white font-bold text-lg shadow">
                      {student.codigo_publico.charAt(0).toUpperCase()}
                    </div>
                  </div>
                );
              }
              return <TutorMessage key={message.id} message={message} />;
            })}

            {typing && (
              <div className="flex gap-3 justify-start fade-in">
                <div className="shrink-0">
                  <BitRobot size={48} animated={false} mood="thinking" />
                </div>
                <div className="bg-white border-2 border-gray-100 px-5 py-4 rounded-lg">
                  <div className="flex gap-1.5">
                    <div className="typing-dot w-2 h-2 bg-[#2E9DF7] rounded-full" />
                    <div className="typing-dot w-2 h-2 bg-[#2E9DF7] rounded-full" />
                    <div className="typing-dot w-2 h-2 bg-[#2E9DF7] rounded-full" />
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>
      </div>

      {/* Input area */}
      <div className="bg-white border-t-2 border-gray-100 p-4">
        <div className="max-w-3xl mx-auto flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(event) => setInput(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter") void sendMessage();
            }}
            placeholder="Escribe tu pregunta a Bit..."
            className="flex-1 px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-[#2E9DF7] focus:outline-none transition"
          />
          <button
            onClick={() => void sendMessage()}
            disabled={!input.trim() || typing}
            className="px-6 py-3 bg-[#2E9DF7] hover:bg-[#1a8de8] disabled:bg-gray-300 text-white font-bold rounded-lg shadow-md transition transform hover:scale-[1.02] disabled:transform-none"
          >
            Enviar
          </button>
        </div>
        <div className="max-w-3xl mx-auto mt-2 flex justify-center gap-6">
          <button
            onClick={onBack}
            className="text-xs text-gray-500 hover:text-gray-700 transition"
          >
            ← Cambiar de juego
          </button>
          <button
            onClick={() => void handleExit()}
            disabled={abandonLoading}
            className="text-xs text-[#E74C3C] hover:text-red-700 transition font-medium"
          >
            {abandonLoading ? "Guardando..." : "Quiero salir"}
          </button>
          <button onClick={() => setFinishOpen(true)} className="text-xs text-gray-500 hover:text-gray-700 transition">
            ✓ Finalizar (profe)
          </button>
        </div>
      </div>

      {/* Teacher finish modal */}
      {finishOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-2xl p-6 max-w-sm w-full fade-in">
            <h3 className="text-xl font-bold text-gray-800 mb-2">Código del profe</h3>
            <p className="text-sm text-gray-600 mb-4">Pídele a tu profe que escriba el código para terminar la sesión oficial.</p>
            <input
              type="password"
              value={adminCode}
              onChange={(event) => {
                setAdminCode(event.target.value);
                setFinishError("");
              }}
              onKeyDown={(event) => {
                if (event.key === "Enter") void finishSession();
              }}
              className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-[#2E9DF7] focus:outline-none transition text-center"
              autoFocus
            />
            {finishError && <p className="text-[#E74C3C] text-sm mt-2 text-center">{finishError}</p>}
            <div className="grid grid-cols-2 gap-3 mt-5">
              <button
                onClick={() => {
                  setFinishOpen(false);
                  setFinishError("");
                }}
                className="py-3 bg-gray-100 hover:bg-gray-200 text-gray-700 font-bold rounded-lg transition"
              >
                Volver
              </button>
              <button
                onClick={() => void finishSession()}
                disabled={finishLoading || !adminCode.trim()}
                className="py-3 bg-[#7EC242] hover:bg-[#6ab038] disabled:bg-gray-300 text-white font-bold rounded-lg transition"
              >
                {finishLoading ? "Revisando..." : "Finalizar"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
