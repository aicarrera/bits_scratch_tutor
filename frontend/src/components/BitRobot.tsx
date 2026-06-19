type BitRobotProps = {
  size?: number;
  mood?: "happy" | "thinking" | "sad";
  animated?: boolean;
};

export function BitRobot({ size = 120, mood = "happy", animated = true }: BitRobotProps) {
  const eyeY = mood === "thinking" ? 35 : 38;
  const mouthPath =
    mood === "happy" ? "M 35 55 Q 50 65 65 55" : mood === "thinking" ? "M 38 58 L 62 58" : "M 35 60 Q 50 50 65 60";

  return (
    <svg width={size} height={size} viewBox="0 0 100 100" className={animated ? "bit-bounce" : ""} aria-hidden="true">
      <line x1="50" y1="8" x2="50" y2="18" stroke="#9B59B6" strokeWidth="2.5" strokeLinecap="round" />
      <circle cx="50" cy="6" r="3.5" fill="#E91E63" />
      <rect x="20" y="18" width="60" height="50" rx="14" fill="#2E9DF7" stroke="#1a1a1a" strokeWidth="2.5" />
      <ellipse cx="30" cy="28" rx="8" ry="4" fill="#fff" opacity="0.25" />
      <circle cx="36" cy={eyeY} r="6" fill="#fff" />
      <circle cx="64" cy={eyeY} r="6" fill="#fff" />
      <circle cx="37" cy={eyeY + 1} r="3" fill="#1a1a1a" />
      <circle cx="65" cy={eyeY + 1} r="3" fill="#1a1a1a" />
      <circle cx="38" cy={eyeY} r="1" fill="#fff" />
      <circle cx="66" cy={eyeY} r="1" fill="#fff" />
      <circle cx="26" cy="50" r="4" fill="#FF8C42" opacity="0.5" />
      <circle cx="74" cy="50" r="4" fill="#FF8C42" opacity="0.5" />
      <path d={mouthPath} stroke="#1a1a1a" strokeWidth="2.5" fill="none" strokeLinecap="round" />
      <rect x="30" y="68" width="40" height="22" rx="6" fill="#F4C842" stroke="#1a1a1a" strokeWidth="2.5" />
      <circle cx="40" cy="79" r="2" fill="#E74C3C" />
      <circle cx="50" cy="79" r="2" fill="#7EC242" />
      <circle cx="60" cy="79" r="2" fill="#9B59B6" />
      <rect x="12" y="72" width="8" height="14" rx="3" fill="#2E9DF7" stroke="#1a1a1a" strokeWidth="2" />
      <rect x="80" y="72" width="8" height="14" rx="3" fill="#2E9DF7" stroke="#1a1a1a" strokeWidth="2" />
    </svg>
  );
}
