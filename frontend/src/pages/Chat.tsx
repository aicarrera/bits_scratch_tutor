import { useEffect, useRef, useState } from "react";

import { api } from "../api/client";
import { BitRobot } from "../components/BitRobot";
import { Header } from "../components/Header";
import type { BloqueSugerido, ChatMessage, Conversation, Game, LearningSession, Student } from "../types/api";

type ChatProps = {
  student: Student;
  session: LearningSession;
  game: Game;
  conversation: Conversation;
  onConversationUpdated: (conversation: Conversation) => void;
  onBack: () => void;
  onFinished: (session: LearningSession) => void;
  onAbandoned: (session: LearningSession) => void;
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

export function Chat({
  student,
  session,
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
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, typing]);

  const sendMessage = async () => {
    const text = input.trim();
    if (!text || typing) return;
    setInput("");
    setTyping(true);
    try {
      const exchange = await api.sendMessage(conversation.id, text);
      const updatedMessages = [...messages, exchange.mensaje_nino, exchange.mensaje_tutor];
      setMessages(updatedMessages);
      onConversationUpdated({ ...conversation, mensajes: updatedMessages });
    } catch {
      const fallback: ChatMessage = {
        id: `local-error-${Date.now()}`,
        conversacion_id: conversation.id,
        sesion_id: session.id,
        estudiante_id: student.id,
        rol: "tutor",
        contenido: "No pude guardar ese mensaje. Pídele ayuda a tu profe y probemos otra vez.",
        orden_mensaje: messages.length + 1,
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
      setMessages((current) => [...current, fallback]);
    } finally {
      setTyping(false);
    }
  };

  const finishSession = async () => {
    setFinishError("");
    setFinishLoading(true);
    try {
      const closedSession = await api.finishSession(session.id, adminCode.trim());
      setFinishOpen(false);
      onFinished(closedSession);
    } catch (caughtError) {
      setFinishError(caughtError instanceof Error ? caughtError.message : "Código de profesor inválido.");
    } finally {
      setFinishLoading(false);
    }
  };

  const handleExit = async () => {
    setAbandonLoading(true);
    try {
      const abandonedSession = await api.abandonSession(session.id);
      onAbandoned(abandonedSession);
    } catch {
      // Even if the API call fails, redirect to feedback
      onAbandoned(session);
    } finally {
      setAbandonLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col h-screen">
      <Header code={student.codigo_publico} game={game} onExit={() => setFinishOpen(true)} showBack onBack={onBack} />

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
          <button onClick={onBack} className="text-xs text-gray-500 hover:text-gray-700 transition">
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
