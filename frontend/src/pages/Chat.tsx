import { useEffect, useRef, useState } from "react";

import { api } from "../api/client";
import { BitRobot } from "../components/BitRobot";
import { Header } from "../components/Header";
import type { ChatMessage, Conversation, Game, LearningSession, Student } from "../types/api";

type ChatProps = {
  student: Student;
  session: LearningSession;
  game: Game;
  conversation: Conversation;
  onConversationUpdated: (conversation: Conversation) => void;
  onBack: () => void;
  onFinished: (session: LearningSession) => void;
};

export function Chat({ student, session, game, conversation, onConversationUpdated, onBack, onFinished }: ChatProps) {
  const [messages, setMessages] = useState<ChatMessage[]>(conversation.mensajes);
  const [input, setInput] = useState("");
  const [typing, setTyping] = useState(false);
  const [finishOpen, setFinishOpen] = useState(false);
  const [adminCode, setAdminCode] = useState("");
  const [finishError, setFinishError] = useState("");
  const [finishLoading, setFinishLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, typing]);

  const sendMessage = async () => {
    const text = input.trim();
    if (!text || typing) {
      return;
    }
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

  return (
    <div className="min-h-screen flex flex-col h-screen">
      <Header code={student.codigo_publico} game={game} onExit={() => setFinishOpen(true)} showBack onBack={onBack} />
      <div className="flex-1 overflow-y-auto chat-messages px-4 py-6">
        <div className="max-w-3xl mx-auto space-y-4">
          {messages.map((message) => {
            const isChild = message.rol === "nino";
            return (
              <div key={message.id} className={`flex gap-3 fade-in ${isChild ? "justify-end" : "justify-start"}`}>
                {!isChild && (
                  <div className="flex-shrink-0">
                    <BitRobot size={48} animated={false} />
                  </div>
                )}
                <div
                  className={`max-w-[75%] px-5 py-3 rounded-lg shadow-sm ${
                    isChild ? "bg-[#FF8C42] text-white" : "bg-white border-2 border-gray-100 text-gray-800"
                  }`}
                >
                  <p className="text-base leading-relaxed">{message.contenido}</p>
                </div>
                {isChild && (
                  <div className="flex-shrink-0 w-12 h-12 rounded-full bg-[#FF8C42] flex items-center justify-center text-white font-bold text-lg shadow">
                    {student.codigo_publico.charAt(0).toUpperCase()}
                  </div>
                )}
              </div>
            );
          })}
          {typing && (
            <div className="flex gap-3 justify-start fade-in">
              <div className="flex-shrink-0">
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
      <div className="bg-white border-t-2 border-gray-100 p-4">
        <div className="max-w-3xl mx-auto flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(event) => setInput(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter") {
                void sendMessage();
              }
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
        <div className="max-w-3xl mx-auto mt-2 flex justify-center gap-4">
          <button onClick={onBack} className="text-xs text-gray-500 hover:text-gray-700 transition">
            ← Cambiar de juego
          </button>
          <button onClick={() => setFinishOpen(true)} className="text-xs text-gray-500 hover:text-gray-700 transition">
            ✓ Finalizar
          </button>
        </div>
      </div>

      {finishOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-2xl p-6 max-w-sm w-full fade-in">
            <h3 className="text-xl font-bold text-gray-800 mb-2">Código del profe</h3>
            <p className="text-sm text-gray-600 mb-4">Pídele a tu profe que escriba el código para terminar.</p>
            <input
              type="password"
              value={adminCode}
              onChange={(event) => {
                setAdminCode(event.target.value);
                setFinishError("");
              }}
              onKeyDown={(event) => {
                if (event.key === "Enter") {
                  void finishSession();
                }
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
