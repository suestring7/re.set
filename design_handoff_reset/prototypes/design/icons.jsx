// Hand-drawn-feeling SVG iconography for exercises
// Each is intentionally rough/playful, avoiding clinical fitness-app vibes.
const ExIcon = {
  // Stretch — flowing curves, body posture hints
  S1: ({ c = 'currentColor' }) => (
    <svg viewBox="0 0 48 48" fill="none" stroke={c} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="24" cy="14" r="5" />
      <path d="M24 19 Q 22 28 26 36" />
      <path d="M24 22 Q 30 22 32 18" />
      <path d="M24 22 Q 18 22 16 18" />
      <path d="M14 12 Q 24 6 34 12" strokeDasharray="2 2" opacity=".4" />
    </svg>
  ),
  S2: ({ c = 'currentColor' }) => (
    <svg viewBox="0 0 48 48" fill="none" stroke={c} strokeWidth="1.5" strokeLinecap="round">
      <circle cx="24" cy="16" r="5" />
      <path d="M24 21 L 24 36" />
      <path d="M30 18 Q 26 14 24 18" />
      <path d="M32 16 L 36 16" strokeDasharray="2 2" />
    </svg>
  ),
  S3: ({ c = 'currentColor' }) => (
    <svg viewBox="0 0 48 48" fill="none" stroke={c} strokeWidth="1.5" strokeLinecap="round">
      <circle cx="24" cy="14" r="4" />
      <path d="M16 22 Q 24 18 32 22" />
      <path d="M14 24 L 14 18" />
      <path d="M34 24 L 34 18" />
      <path d="M24 22 L 24 36" />
    </svg>
  ),
  S4: ({ c = 'currentColor' }) => (
    <svg viewBox="0 0 48 48" fill="none" stroke={c} strokeWidth="1.5" strokeLinecap="round">
      <rect x="6" y="8" width="3" height="32" />
      <rect x="39" y="8" width="3" height="32" />
      <circle cx="24" cy="18" r="4" />
      <path d="M24 22 L 24 36" />
      <path d="M20 24 L 12 22" />
      <path d="M28 24 L 36 22" />
    </svg>
  ),
  // Generic stretch
  S: ({ c = 'currentColor' }) => (
    <svg viewBox="0 0 48 48" fill="none" stroke={c} strokeWidth="1.5" strokeLinecap="round">
      <circle cx="24" cy="14" r="4" />
      <path d="M24 18 Q 22 28 26 36" />
      <path d="M14 22 Q 24 18 34 22" />
    </svg>
  ),
  // Core — torso / breath
  C1: ({ c = 'currentColor' }) => (
    <svg viewBox="0 0 48 48" fill="none" stroke={c} strokeWidth="1.5" strokeLinecap="round">
      <circle cx="24" cy="14" r="4" />
      <path d="M16 36 Q 24 30 32 36" />
      <ellipse cx="24" cy="26" rx="7" ry="5" />
      <path d="M24 21 L 24 31" strokeDasharray="2 2" />
    </svg>
  ),
  C: ({ c = 'currentColor' }) => (
    <svg viewBox="0 0 48 48" fill="none" stroke={c} strokeWidth="1.5" strokeLinecap="round">
      <circle cx="24" cy="14" r="4" />
      <path d="M18 36 L 18 24 Q 24 22 30 24 L 30 36" />
      <path d="M21 28 L 27 28" />
      <path d="M21 32 L 27 32" />
    </svg>
  ),
  // Strength
  T1: ({ c = 'currentColor' }) => (
    <svg viewBox="0 0 48 48" fill="none" stroke={c} strokeWidth="1.5" strokeLinecap="round">
      <circle cx="24" cy="12" r="4" />
      <path d="M24 16 L 24 28" />
      <path d="M18 28 L 18 38" />
      <path d="M30 28 L 30 38" />
      <path d="M14 22 L 34 22" />
    </svg>
  ),
  T9: ({ c = 'currentColor' }) => (
    <svg viewBox="0 0 48 48" fill="none" stroke={c} strokeWidth="1.5" strokeLinecap="round">
      <path d="M8 38 L 16 38 L 16 32 L 24 32 L 24 26 L 32 26 L 32 20 L 40 20" />
      <circle cx="32" cy="14" r="3" />
    </svg>
  ),
  T: ({ c = 'currentColor' }) => (
    <svg viewBox="0 0 48 48" fill="none" stroke={c} strokeWidth="1.5" strokeLinecap="round">
      <circle cx="24" cy="12" r="4" />
      <path d="M24 16 L 24 30" />
      <path d="M14 22 L 34 22" />
      <rect x="10" y="20" width="4" height="4" />
      <rect x="34" y="20" width="4" height="4" />
      <path d="M20 30 L 18 40" />
      <path d="M28 30 L 30 40" />
    </svg>
  ),
  // Bottle (with weight)
  B: ({ c = 'currentColor' }) => (
    <svg viewBox="0 0 48 48" fill="none" stroke={c} strokeWidth="1.5" strokeLinecap="round">
      <circle cx="24" cy="12" r="3.5" />
      <path d="M24 15.5 L 24 26" />
      <path d="M16 22 L 32 22" />
      <rect x="11" y="19" width="6" height="6" rx="1" />
      <rect x="31" y="19" width="6" height="6" rx="1" />
      <path d="M20 30 L 18 40" />
      <path d="M28 30 L 30 40" />
    </svg>
  ),
};

function getExIcon(ex) {
  if (!ex) return ExIcon.S;
  if (ExIcon[ex.id]) return ExIcon[ex.id];
  if (ex.subcategory === 'bottle') return ExIcon.B;
  if (ex.category === 'stretch') return ExIcon.S;
  if (ex.category === 'core') return ExIcon.C;
  if (ex.category === 'strength') return ExIcon.T;
  return ExIcon.S;
}

window.ExIcon = ExIcon;
window.getExIcon = getExIcon;
