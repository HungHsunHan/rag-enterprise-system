export interface JwtClaims {
  [key: string]: any
}

/**
 * Decode a JWT payload safely (base64url to JSON).
 * Returns null if token is invalid.
 */
export function decodeJwt(token: string): JwtClaims | null {
  try {
    const parts = token.split('.')
    if (parts.length !== 3) return null
    const payload = parts[1]
    const normalized = payload.replace(/-/g, '+').replace(/_/g, '/')
    const padding = '='.repeat((4 - (normalized.length % 4)) % 4)
    const decoded = atob(normalized + padding)
    return JSON.parse(decoded)
  } catch {
    return null
  }
}
