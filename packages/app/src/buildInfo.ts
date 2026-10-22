// Set from VITE_BUILD_SHA at build time. The GitHub Pages workflow that used to stamp it has been
// removed, so it reads `local` on Vercel unless the variable is configured there. Absent in a
// local dev/build (`local`/`null`); when stamped, the live site can be checked against `git log`
// instead of trusted blind — see docs/assumptions.md for the incident this exists to prevent.
export const BUILD_SHA = (import.meta.env.VITE_BUILD_SHA as string | undefined) || 'local'
export const BUILD_TIME_ISO = (import.meta.env.VITE_BUILD_TIME as string | undefined) || null
