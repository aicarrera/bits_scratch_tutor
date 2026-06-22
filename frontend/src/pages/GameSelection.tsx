import { useEffect, useMemo, useState } from "react";

import { api } from "../api/client";
import { BitRobot } from "../components/BitRobot";
import { GameCard } from "../components/GameCard";
import { Header } from "../components/Header";
import type { ChatMessage, Conversation, Game, GameCategory, GamesCatalog, Student } from "../types/api";

type GameSelectionProps = {
  student: Student;
  onSelected: (game: Game, sessionId: string, conversation: Conversation) => void;
};

function CompletedModal({
  game,
  historial,
  onRestart,
  onCancel,
}: {
  game: Game;
  historial: Conversation;
  onRestart: () => void;
  onCancel: () => void;
}) {
  const [showHistory, setShowHistory] = useState(false);

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-xl shadow-2xl p-6 max-w-lg w-full fade-in">
        <div className="flex justify-center mb-4">
          <BitRobot size={80} mood="happy" />
        </div>
        <h3 className="text-2xl font-bold text-center text-gray-800 mb-2">¡Ya terminaste este juego! 🏆</h3>
        <p className="text-center text-gray-600 mb-5">
          Completaste <span className="font-semibold text-[#2E9DF7]">{game.titulo}</span> con tu profe.
          ¿Quieres volver a jugarlo o ver el historial de tu conversación?
        </p>

        {showHistory && (
          <div className="border-2 border-gray-100 rounded-lg p-3 mb-5 max-h-64 overflow-y-auto bg-gray-50 space-y-2">
            {historial.mensajes.map((msg: ChatMessage) => (
              <div
                key={msg.id}
                className={`flex ${msg.rol === "nino" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-[80%] px-4 py-2 rounded-lg text-sm ${
                    msg.rol === "nino"
                      ? "bg-[#FF8C42] text-white"
                      : "bg-white border border-gray-200 text-gray-800"
                  }`}
                >
                  {msg.contenido}
                </div>
              </div>
            ))}
          </div>
        )}

        <div className="space-y-2">
          <button
            onClick={() => setShowHistory((v) => !v)}
            className="w-full py-3 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 font-semibold rounded-lg transition"
          >
            {showHistory ? "Ocultar historial" : "📜 Ver historial de la conversación"}
          </button>
          <div className="grid grid-cols-2 gap-3">
            <button
              onClick={onCancel}
              className="py-3 bg-gray-100 hover:bg-gray-200 text-gray-700 font-bold rounded-lg transition"
            >
              Cancelar
            </button>
            <button
              onClick={onRestart}
              className="py-3 bg-[#7EC242] hover:bg-[#6ab038] text-white font-bold rounded-lg shadow-md transition"
            >
              🔄 Volver a iniciar
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export function GameSelection({ student, onSelected }: GameSelectionProps) {
  const [catalog, setCatalog] = useState<GamesCatalog>({ categorias: [], juegos: [] });
  const [activeCategory, setActiveCategory] = useState("todos");
  const [loadingCatalog, setLoadingCatalog] = useState(true);
  const [selecting, setSelecting] = useState(false);
  const [error, setError] = useState("");
  const [completedGame, setCompletedGame] = useState<Game | null>(null);
  const [completedHistory, setCompletedHistory] = useState<Conversation | null>(null);

  useEffect(() => {
    let mounted = true;
    async function loadCatalog() {
      setLoadingCatalog(true);
      try {
        const response = await api.getGames();
        if (mounted) {
          setCatalog(response);
        }
      } catch (caughtError) {
        if (mounted) {
          setError(caughtError instanceof Error ? caughtError.message : "No se pudieron cargar los juegos.");
        }
      } finally {
        if (mounted) {
          setLoadingCatalog(false);
        }
      }
    }
    void loadCatalog();
    return () => {
      mounted = false;
    };
  }, []);

  const categoriesById = useMemo(() => {
    return new Map<string, GameCategory>(catalog.categorias.map((category) => [category.id, category]));
  }, [catalog.categorias]);

  const filteredGames = useMemo(() => {
    if (activeCategory === "todos") {
      return catalog.juegos;
    }
    return catalog.juegos.filter((game) => game.categoria_id === activeCategory);
  }, [activeCategory, catalog.juegos]);

  const handleSelect = async (game: Game, forceNew = false) => {
    setSelecting(true);
    setError("");
    try {
      const result = await api.openGame(student.id, game.id, forceNew);
      if (result.ya_completado && result.historial_completado) {
        setCompletedGame(game);
        setCompletedHistory(result.historial_completado);
        return;
      }
      if (result.sesion_id && result.conversation) {
        onSelected(game, result.sesion_id, result.conversation);
      }
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "No se pudo abrir el juego.");
    } finally {
      setSelecting(false);
    }
  };

  const handleRestartCompleted = async () => {
    if (!completedGame) return;
    const game = completedGame;
    setCompletedGame(null);
    setCompletedHistory(null);
    await handleSelect(game, true);
  };

  const categoryFilters = [
    { id: "todos", nombre: "Todos", icono: "🌟", color_hex: "#2E9DF7" },
    ...catalog.categorias,
  ];

  return (
    <div className="min-h-screen flex flex-col">
      <Header code={student.codigo_publico} showExit={false} />
      <div className="flex-1 p-6 max-w-6xl mx-auto w-full">
        <div className="text-center mb-6 fade-in">
          <div className="flex justify-center mb-3">
            <BitRobot size={80} />
          </div>
          <h2 className="text-3xl font-bold text-gray-800">
            ¿Qué quieres hacer hoy, <span style={{ color: "#2E9DF7" }}>{student.codigo_publico}</span>?
          </h2>
          <p className="text-gray-600 mt-2">Escoge un juego o crea algo libre ✨</p>
        </div>

        {error && <p className="text-[#E74C3C] text-sm mb-4 text-center fade-in">{error}</p>}
        {loadingCatalog ? (
          <div className="flex justify-center items-center py-20">
            <div className="text-xl font-bold text-gray-500 animate-pulse">Cargando juegos...</div>
          </div>
        ) : (
          <>
            <div className="flex flex-wrap gap-2 justify-center mb-6">
              {categoryFilters.map((category) => (
                <button
                  key={category.id}
                  onClick={() => setActiveCategory(category.id)}
                  className={`px-4 py-2 rounded-lg font-semibold transition ${
                    activeCategory === category.id ? "text-white shadow-md" : "bg-white text-gray-700 border-2 border-gray-200 hover:border-gray-300"
                  }`}
                  style={activeCategory === category.id ? { backgroundColor: category.color_hex ?? "#2E9DF7" } : {}}
                >
                  {category.icono} {category.nombre}
                </button>
              ))}
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredGames.map((game) => (
                <GameCard
                  key={game.id}
                  game={game}
                  category={game.categoria_id ? categoriesById.get(game.categoria_id) : undefined}
                  disabled={selecting}
                  onSelect={(selectedGame) => void handleSelect(selectedGame)}
                />
              ))}
            </div>
          </>
        )}
      </div>

      {completedGame && completedHistory && (
        <CompletedModal
          game={completedGame}
          historial={completedHistory}
          onRestart={() => void handleRestartCompleted()}
          onCancel={() => {
            setCompletedGame(null);
            setCompletedHistory(null);
          }}
        />
      )}
    </div>
  );
}
