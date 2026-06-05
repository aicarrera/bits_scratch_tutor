import { GamePreview } from "./GamePreview";
import type { Game, GameCategory } from "../types/api";

type GameCardProps = {
  game: Game;
  category?: GameCategory;
  disabled: boolean;
  onSelect: (game: Game) => void;
};

export function GameCard({ game, category, disabled, onSelect }: GameCardProps) {
  const color = game.color_acento ?? category?.color_hex ?? "#2E9DF7";
  return (
    <button
      disabled={disabled}
      onClick={() => onSelect(game)}
      className={`card-hover bg-white rounded-lg overflow-hidden shadow text-left fade-in border-2 border-transparent ${
        disabled ? "opacity-50 cursor-wait" : ""
      }`}
      style={{ borderColor: `${color}33` }}
    >
      <GamePreview gameId={game.id} color={color} />
      <div className="p-4">
        <div className="flex items-center gap-2 mb-1">
          <span className="text-2xl">{game.icono}</span>
          {category && (
            <span className="text-xs px-2 py-1 rounded-lg font-semibold" style={{ backgroundColor: `${color}22`, color }}>
              {category.icono} {category.nombre}
            </span>
          )}
        </div>
        <h3 className="font-bold text-gray-800 text-lg mb-1">{game.titulo}</h3>
        <p className="text-sm text-gray-600 mb-3">{game.descripcion_corta}</p>
        {game.duracion_estimada_min && <div className="text-xs text-gray-500">⏱️ ~{game.duracion_estimada_min} min</div>}
        {game.es_proyecto_libre && <div className="text-xs text-gray-500">✨ Tú decides qué crear</div>}
      </div>
    </button>
  );
}
