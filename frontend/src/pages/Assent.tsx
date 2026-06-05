import { useState } from "react";

import { api } from "../api/client";
import { BitRobot } from "../components/BitRobot";
import { Header } from "../components/Header";
import type { LearningSession, Student } from "../types/api";

type AssentProps = {
  student: Student;
  onAccepted: (session: LearningSession) => void;
  onRejected: () => void;
};

export function Assent({ student, onAccepted, onRejected }: AssentProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleAccept = async () => {
    setLoading(true);
    setError("");
    try {
      const session = await api.createSession(student.id);
      onAccepted(session);
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "No se pudo crear la sesión.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Header code={student.codigo_publico} showExit={false} />
      <div className="flex-1 flex items-center justify-center p-6">
        <div className="bg-white rounded-lg shadow-2xl p-8 max-w-2xl w-full fade-in">
          <div className="flex justify-center mb-4">
            <BitRobot size={120} />
          </div>
          <h2 className="text-2xl font-bold text-center text-gray-800 mb-2">
            ¡Qué bueno verte, <span style={{ color: "#2E9DF7" }}>{student.codigo_publico}</span>!
          </h2>
          <p className="text-center text-gray-500 mb-6">Antes de empezar, quiero contarte algo importante:</p>
          <div className="space-y-4 text-gray-700 text-lg">
            <div className="flex gap-3 items-start">
              <div className="text-2xl">🤖</div>
              <p>
                Yo soy un <strong>programa de computadora</strong>, no una persona real.
              </p>
            </div>
            <div className="flex gap-3 items-start">
              <div className="text-2xl">💬</div>
              <p>Vamos a conversar para que aprendas Scratch.</p>
            </div>
            <div className="flex gap-3 items-start">
              <div className="text-2xl">👀</div>
              <p>
                Lo que escribamos lo va a <strong>leer tu profe</strong>.
              </p>
            </div>
            <div className="flex gap-3 items-start">
              <div className="text-2xl">🚪</div>
              <p>
                Si no quieres seguir, dile a tu profe o aprieta <strong>Salir</strong>.
              </p>
            </div>
          </div>
          {error && <p className="text-[#E74C3C] text-sm mt-4 text-center fade-in">{error}</p>}
          <p className="text-center mt-8 text-gray-800 font-semibold">¿Quieres empezar?</p>
          <div className="grid grid-cols-2 gap-3 mt-4">
            <button onClick={onRejected} className="py-4 bg-gray-100 hover:bg-gray-200 text-gray-700 font-bold rounded-lg transition">
              No, mejor no
            </button>
            <button
              onClick={() => void handleAccept()}
              disabled={loading}
              className="py-4 bg-[#7EC242] hover:bg-[#6ab038] disabled:bg-gray-400 text-white font-bold rounded-lg shadow-md transition transform hover:scale-[1.02]"
            >
              {loading ? "Creando sesión..." : "¡Sí, vamos! ✨"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
