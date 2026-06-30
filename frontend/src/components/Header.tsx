import type { Game } from "../types/api";

type HeaderProps = {
  code?: string;
  game?: Game | null;
  showExit?: boolean;
  showBack?: boolean;
  onExit?: () => void;
  onBack?: () => void;
  onVideo?: () => void;
};

export function Header({ code, game, showExit = true, showBack = false, onExit, onBack, onVideo }: HeaderProps) {
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
        {onVideo && (
          <button
            onClick={onVideo}
            title="Ver video del juego"
            className="flex items-center gap-2 bg-[#FF0000] hover:bg-[#cc0000] px-3 py-2 rounded-lg transition transform hover:scale-[1.03] shadow"
          >
            <svg viewBox="0 0 28 20" className="w-6 h-4" aria-hidden="true">
              <path
                d="M27.4 3.1a3.5 3.5 0 0 0-2.46-2.48C22.77 0 14 0 14 0S5.23 0 3.06.62A3.5 3.5 0 0 0 .6 3.1C0 5.28 0 10 0 10s0 4.72.6 6.9a3.5 3.5 0 0 0 2.46 2.48C5.23 20 14 20 14 20s8.77 0 10.94-.62a3.5 3.5 0 0 0 2.46-2.48C28 14.72 28 10 28 10s0-4.72-.6-6.9Z"
                fill="#fff"
              />
              <path d="M11.2 14.29 18.5 10l-7.3-4.29v8.58Z" fill="#FF0000" />
            </svg>
            <span className="hidden sm:inline text-sm font-bold">Video</span>
          </button>
        )}
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
