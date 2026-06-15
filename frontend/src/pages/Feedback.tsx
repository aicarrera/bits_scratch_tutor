import { useState } from "react";

import { api } from "../api/client";
import { BitRobot } from "../components/BitRobot";
import { Header } from "../components/Header";
import type { LearningSession, Student } from "../types/api";

type FeedbackProps = {
  student: Student;
  session: LearningSession;
  onDone: () => void;
};

const feedbackOptions = [
  { nivel: 1, icon: "😞", label: "Muy mal", color: "bg-red-50 hover:bg-red-100" },
  { nivel: 2, icon: "🙁", label: "Mal", color: "bg-orange-50 hover:bg-orange-100" },
  { nivel: 3, icon: "😐", label: "Más o menos", color: "bg-yellow-50 hover:bg-yellow-100" },
  { nivel: 4, icon: "🙂", label: "Bien", color: "bg-lime-50 hover:bg-lime-100" },
  { nivel: 5, icon: "😊", label: "Muy bien", color: "bg-green-50 hover:bg-green-100" },
] as const;

export function Feedback({ student, session, onDone }: FeedbackProps) {
  const [selected, setSelected] = useState<number | null>(null);
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const submit = async (nivel: number, etiqueta: string) => {
    setSelected(nivel);
    setLoading(true);
    setError("");
    try {
      await api.submitFeedback(session.id, nivel, etiqueta);
      setSubmitted(true);
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "No se pudo guardar tu respuesta.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Header code={student.codigo_publico} showExit={false} />
      <div className="flex-1 flex items-center justify-center p-6">
        <div className="bg-white rounded-lg shadow-2xl p-8 max-w-md w-full text-center fade-in">
          <div className="flex justify-center mb-4">
            <BitRobot size={140} mood="happy" />
          </div>
          <h2 className="text-3xl font-bold text-gray-800 mb-2">¡Buen trabajo! 🎉</h2>
          <p className="text-gray-600 mb-6">
            Gracias por hablar conmigo hoy, <span style={{ color: "#2E9DF7" }}>{student.codigo_publico}</span>.
          </p>
          {!submitted ? (
            <>
              <p className="text-gray-700 font-semibold mb-4">¿Cómo te sentiste?</p>
              <div className="grid grid-cols-5 gap-2 mb-6">
                {feedbackOptions.map((option) => (
                  <button
                    key={option.nivel}
                    onClick={() => void submit(option.nivel, option.label)}
                    disabled={loading}
                    className={`py-3 rounded-lg transition transform hover:scale-105 ${option.color} ${
                      selected === option.nivel ? "ring-2 ring-[#2E9DF7]" : ""
                    }`}
                  >
                    <div className="text-3xl">{option.icon}</div>
                    <div className="text-[11px] mt-1 text-gray-600 leading-tight">{option.label}</div>
                  </button>
                ))}
              </div>
              {error && <p className="text-[#E74C3C] text-sm mb-4">{error}</p>}
            </>
          ) : (
            <div className="bg-blue-50 rounded-lg p-4 mb-6 fade-in">
              <p className="text-gray-700">¡Gracias por contarme! Tu respuesta quedó guardada.</p>
            </div>
          )}
          <button onClick={onDone} className="w-full py-3 bg-[#2E9DF7] hover:bg-[#1a8de8] text-white font-bold rounded-lg shadow-md transition">
            Cerrar sesión
          </button>
        </div>
      </div>
    </div>
  );
}
