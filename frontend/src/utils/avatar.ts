/**
 * Utilities for generating deterministic user avatar initials and colours.
 *
 * Used by the `UserAvatar` component to render a coloured initials badge
 * as a replacement for uploaded profile pictures. The colour is derived
 * from the first character of the user's name so the same name always
 * produces the same badge across sessions.
 *
 * @module avatar
 */

/** Fixed palette of background/foreground colour pairs for avatar badges. */
const PALETTE = [
  { bg: '#1a3a5c', color: '#2d8eff' },
  { bg: '#1a2a0d', color: '#3fb950' },
  { bg: '#2a1a0d', color: '#d4a017' },
  { bg: '#1a0d2a', color: '#9050c0' },
  { bg: '#2a0d0d', color: '#e05050' },
  { bg: '#0d1a2a', color: '#3090b0' },
];

/**
 * Derive up to two uppercase initials from a display name.
 *
 * Splits on whitespace, takes the first letter of each of the first two
 * words, and uppercases the result. Single-word names produce one initial.
 *
 * @param name - The user's display name (e.g. `"João Pedro"`).
 * @returns Initials string (e.g. `"JP"`).
 *
 * @example
 * getInitials('Alice Smith') // → 'AS'
 * getInitials('Bob')         // → 'B'
 */
export function getInitials(name: string): string {
  return name
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((word) => word[0].toUpperCase())
    .join('');
}

/**
 * Select a deterministic background/foreground colour pair for a name.
 *
 * Uses the char code of the first character modulo the palette length so
 * the same name always maps to the same colour.
 *
 * @param name - The user's display name.
 * @returns An object with `bg` (background hex) and `color` (text hex).
 *
 * @example
 * getAvatarColor('Alice') // → { bg: '#1a3a5c', color: '#2d8eff' }
 */
export function getAvatarColor(name: string): { bg: string; color: string } {
  const index = (name.charCodeAt(0) || 0) % PALETTE.length;
  return PALETTE[index];
}
