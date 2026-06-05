import { useEffect, useMemo, useState } from "react";

import { api } from "../api/client";
import { BitRobot } from "../components/BitRobot";
import { GameCard } from "../components/GameCard";
import { Header } from "../components/Header";
import type { Conversation, Game, GameCategory, GamesCatalog, LearningSession, Student } from "../types/api";

type GameSelectionProps = {
  student: Student;
  session: LearningSession;
  onSelected: (game: Game, conversation: Conversation) => void;
};

export function GameSelection({ student, session, onSelected }: GameSelectionProps) {
  const [catalog, setCatalog] = useState<GamesCatalog>({ categorias: [], juegos: [] });
  const [activeCategory, setActiveCategory] = useState("todos");
  const [loadingCatalog, setLoadingCatalog] = useState(true);
  const [selecting, setSelecting] = useState(false);
  const [error, setError] = useState("");

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

  const handleSelect = async (game: Game) => {
    setSelecting(true);
    setError("");
    try {
      const conversation = await api.openConversation(session.id, game.id);
      onSelected(game, conversation);
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "No se pudo abrir el juego.");
    } finally {
      setSelecting(false);
    }
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
    </div>
  );
}
