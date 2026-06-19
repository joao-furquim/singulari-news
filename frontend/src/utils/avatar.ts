const PALETTE = [
  { bg: '#1a3a5c', color: '#2d8eff' },
  { bg: '#1a2a0d', color: '#3fb950' },
  { bg: '#2a1a0d', color: '#d4a017' },
  { bg: '#1a0d2a', color: '#9050c0' },
  { bg: '#2a0d0d', color: '#e05050' },
  { bg: '#0d1a2a', color: '#3090b0' },
];

export function getInitials(name: string): string {
  return name
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((word) => word[0].toUpperCase())
    .join('');
}

export function getAvatarColor(name: string): { bg: string; color: string } {
  const index = (name.charCodeAt(0) || 0) % PALETTE.length;
  return PALETTE[index];
}
