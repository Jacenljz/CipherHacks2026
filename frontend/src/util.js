// Convert a 2-letter ISO country code to its flag emoji.
export function flag(cc) {
  if (!cc || cc.length !== 2) return '🏴'
  return cc
    .toUpperCase()
    .replace(/./g, (c) => String.fromCodePoint(127397 + c.charCodeAt(0)))
}
