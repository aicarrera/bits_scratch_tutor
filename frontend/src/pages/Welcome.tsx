import { useState } from "react";

import { api } from "../api/client";
import { BitRobot } from "../components/BitRobot";
import { Header } from "../components/Header";
import type { Student } from "../types/api";

type WelcomeProps = {
  onValidated: (student: Student) => void;
};

export function Welcome({ onValidated }: WelcomeProps) {
  const [code, setCode] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleEnter = async () => {
    const normalizedCode = code.trim().toLowerCase();
    if (!normalizedCode) {
      setError("Escribe tu código para entrar");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const student = await api.validateCode(normalizedCode);
      onValidated(student);
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "No reconozco ese código. Pídele ayuda a tu profe.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Header showExit={false} />
      <div className="flex-1 flex items-center justify-center p-6">
        <div className="bg-white rounded-lg shadow-2xl p-8 max-w-md w-full fade-in">
          <div className="flex justify-center mb-4">
            <BitRobot size={140} />
          </div>
          <h1 className="text-3xl font-bold text-center text-gray-800 mb-2">
            ¡Hola! Soy <span style={{ color: "#2E9DF7" }}>Bit</span> 👋
          </h1>
          <p className="text-center text-gray-600 mb-6">Tu ayudante de Scratch. ¿Empezamos?</p>
          <label className="block text-sm font-semibold text-gray-700 mb-2">Escribe tu código:</label>
          <input
            type="text"
            value={code}
            onChange={(event) => {
              setCode(event.target.value);
              setError("");
            }}
            onKeyDown={(event) => {
              if (event.key === "Enter") {
                void handleEnter();
              }
            }}
            placeholder="tigre-azul-7"
            className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg text-lg focus:border-[#2E9DF7] focus:outline-none transition text-center"
          />
          {error && <p className="text-[#E74C3C] text-sm mt-2 text-center fade-in">{error}</p>}
          <button
            onClick={() => void handleEnter()}
            disabled={loading}
            className="w-full mt-6 py-4 bg-[#2E9DF7] hover:bg-[#1a8de8] disabled:bg-gray-400 text-white font-bold text-lg rounded-lg shadow-md hover:shadow-lg transition transform hover:scale-[1.02]"
          >
            {loading ? "Buscando..." : "Entrar →"}
          </button>
          <p className="text-xs text-gray-400 text-center mt-6">¿No tienes código? Pídele a tu profe.</p>
        </div>
      </div>
    </div>
  );
}
