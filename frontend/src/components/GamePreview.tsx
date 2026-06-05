import type { ReactNode } from "react";

type GamePreviewProps = {
  gameId: string;
  color?: string;
};

export function GamePreview({ gameId, color = "#2E9DF7" }: GamePreviewProps) {
  const previews: Record<string, ReactNode> = {
    ej_001: (
      <svg viewBox="0 0 100 60" className="w-full h-24" aria-hidden="true">
        <rect width="100" height="60" fill="#FFF5E1" />
        <circle cx="35" cy="35" r="14" fill="#FF8C42" />
        <polygon points="25,25 28,18 32,25" fill="#FF8C42" />
        <polygon points="38,25 42,18 45,25" fill="#FF8C42" />
        <circle cx="32" cy="33" r="2" fill="#1a1a1a" />
        <circle cx="38" cy="33" r="2" fill="#1a1a1a" />
        <path d="M 33 38 Q 35 40 37 38" stroke="#1a1a1a" strokeWidth="1" fill="none" />
        <text x="55" y="32" fontSize="14" fill="#E91E63">
          ♪
        </text>
        <text x="68" y="40" fontSize="11" fill="#9B59B6">
          ♫
        </text>
      </svg>
    ),
    ej_002: (
      <svg viewBox="0 0 100 60" className="w-full h-24" aria-hidden="true">
        <rect width="100" height="60" fill="#E8F5E9" />
        <ellipse cx="40" cy="30" rx="10" ry="14" fill="#9B59B6" transform="rotate(-20 40 30)" />
        <ellipse cx="60" cy="30" rx="10" ry="14" fill="#E91E63" transform="rotate(20 60 30)" />
        <rect x="48" y="22" width="4" height="18" rx="2" fill="#1a1a1a" />
        <line x1="50" y1="22" x2="46" y2="16" stroke="#1a1a1a" strokeWidth="1.5" />
        <line x1="50" y1="22" x2="54" y2="16" stroke="#1a1a1a" strokeWidth="1.5" />
      </svg>
    ),
    ej_003: (
      <svg viewBox="0 0 100 60" className="w-full h-24" aria-hidden="true">
        <rect width="100" height="60" fill="#FFF9C4" />
        <polygon points="20,15 23,22 30,22 24,27 27,34 20,30 13,34 16,27 10,22 17,22" fill="#F4C842" stroke="#1a1a1a" strokeWidth="1" />
        <polygon points="70,40 73,47 80,47 74,52 77,59 70,55 63,59 66,52 60,47 67,47" fill="#F4C842" stroke="#1a1a1a" strokeWidth="1" />
        <rect x="40" y="30" width="20" height="20" rx="4" fill="#2E9DF7" stroke="#1a1a1a" strokeWidth="1.5" />
        <circle cx="46" cy="38" r="2" fill="#fff" />
        <circle cx="54" cy="38" r="2" fill="#fff" />
      </svg>
    ),
    ej_004: (
      <svg viewBox="0 0 100 60" className="w-full h-24" aria-hidden="true">
        <rect width="100" height="60" fill="#E3F2FD" />
        <line x1="0" y1="50" x2="100" y2="50" stroke="#1a1a1a" strokeWidth="2" />
        <circle cx="25" cy="35" r="8" fill="#7EC242" stroke="#1a1a1a" strokeWidth="1.5" />
        <rect x="55" y="38" width="12" height="12" fill="#E74C3C" stroke="#1a1a1a" strokeWidth="1.5" />
        <rect x="78" y="38" width="12" height="12" fill="#E74C3C" stroke="#1a1a1a" strokeWidth="1.5" />
      </svg>
    ),
    ej_005: (
      <svg viewBox="0 0 100 60" className="w-full h-24" aria-hidden="true">
        <rect width="100" height="60" fill="#FFF3E0" />
        <circle cx="30" cy="35" r="12" fill="#2E9DF7" stroke="#1a1a1a" strokeWidth="1.5" />
        <circle cx="70" cy="35" r="12" fill="#E91E63" stroke="#1a1a1a" strokeWidth="1.5" />
        <ellipse cx="50" cy="15" rx="14" ry="7" fill="#fff" stroke="#1a1a1a" strokeWidth="1" />
        <text x="44" y="18" fontSize="8" fill="#1a1a1a">
          ¡Hola!
        </text>
      </svg>
    ),
    ej_006: (
      <svg viewBox="0 0 100 60" className="w-full h-24" aria-hidden="true">
        <rect x="0" y="0" width="50" height="60" fill="#7EC242" />
        <rect x="50" y="0" width="50" height="60" fill="#FFE082" />
        <circle cx="15" cy="15" r="6" fill="#F4C842" />
        <polygon points="10,50 18,30 26,50" fill="#1B5E20" />
        <rect x="65" y="35" width="20" height="20" fill="#FF8C42" stroke="#1a1a1a" strokeWidth="1" />
        <line x1="50" y1="0" x2="50" y2="60" stroke="#1a1a1a" strokeWidth="2" strokeDasharray="3,3" />
      </svg>
    ),
    proyecto_libre: (
      <svg viewBox="0 0 100 60" className="w-full h-24" aria-hidden="true">
        <rect width="100" height="60" fill="#F3E5F5" />
        <text x="20" y="35" fontSize="24">
          ✨
        </text>
        <text x="45" y="42" fontSize="20">
          🎨
        </text>
        <text x="70" y="30" fontSize="22">
          🚀
        </text>
      </svg>
    ),
  };

  return previews[gameId] ?? (
    <svg viewBox="0 0 100 60" className="w-full h-24" aria-hidden="true">
      <rect width="100" height="60" fill={color} />
    </svg>
  );
}
