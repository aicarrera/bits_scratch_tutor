import type { Game } from "../types/api";

type HeaderProps = {
  code?: string;
  game?: Game | null;
  showExit?: boolean;
  showBack?: boolean;
  onExit?: () => void;
  onBack?: () => void;
};

export function Header({ code, game, showExit = true, showBack = false, onExit, onBack }: HeaderProps) {
  return (
    <div className="bg-[#1a1a1a] text-white px-4 sm:px-6 py-4 flex items-center justify-between shadow-lg">
      <div className="flex items-center gap-3 min-w-0">
        {showBack && (
          <button onClick={onBack} className="text-white/70 hover:text-white text-2xl mr-1" title="Volver">
            ←
          </button>
        )}
        <div className="flex items-center shrink-0">
          <span style={{ color: "#2E9DF7" }} className="font-black text-2xl">
            C
          </span>
          <span style={{ color: "#E74C3C" }} className="font-black text-2xl">
            r
          </span>
          <span style={{ color: "#F4C842" }} className="font-black text-2xl">
            e
          </span>
          <span style={{ color: "#7EC242" }} className="font-black text-2xl">
            a
          </span>
          <span style={{ color: "#E91E63" }} className="font-black text-2xl">
            B
          </span>
          <span style={{ color: "#FF8C42" }} className="font-black text-2xl">
            i
          </span>
          <span style={{ color: "#FF8C42" }} className="font-black text-2xl">
            T
          </span>
          <span style={{ color: "#9B59B6" }} className="font-black text-2xl">
            s
          </span>
        </div>
        {game && (
          <div className="hidden sm:block ml-2 px-3 py-1 bg-white/10 rounded-full text-sm truncate">
            {game.icono} {game.titulo}
          </div>
        )}
      </div>
      <div className="flex items-center gap-3 shrink-0">
        {code && <div className="hidden sm:block text-sm bg-white/10 px-3 py-1 rounded-full">🎫 {code}</div>}
        {showExit && (
          <button onClick={onExit} className="text-sm bg-white/10 hover:bg-white/20 px-3 py-2 rounded-lg transition">
            Salir
          </button>
        )}
      </div>
    </div>
  );
}
