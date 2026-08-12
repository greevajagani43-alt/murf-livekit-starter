/**
 * User ID persistence utility for Day 4
 *
 * Generates and persists a unique user ID in browser localStorage.
 * This ensures the same user gets the same ID across multiple calls.
 */

/**
 * Get a persistent user ID from localStorage.
 * If none exists, generate a new one and store it.
 *
 * Format: user_{timestamp}_{randomId}
 * Example: user_1723234567890_abc123def456
 */
export function getPersistentUserId(): string {
  const STORAGE_KEY = "saathi_user_id";

  // Check if we already have a stored user ID
  if (typeof window !== "undefined") {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      return stored;
    }

    // Generate new user ID
    const timestamp = Date.now();
    const randomId = Math.random().toString(36).substring(2, 15);
    const userId = `user_${timestamp}_${randomId}`;

    // Store it for future calls
    localStorage.setItem(STORAGE_KEY, userId);
    console.log("Generated new persistent user ID:", userId);

    return userId;
  }

  // Fallback for server-side rendering (shouldn't happen in practice)
  return `user_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
}

/**
 * Clear the stored user ID (for testing/reset purposes).
 * After calling this, the next call to getPersistentUserId() will generate a new ID.
 */
export function clearUserId(): void {
  if (typeof window !== "undefined") {
    localStorage.removeItem("saathi_user_id");
    console.log("Cleared persistent user ID");
  }
}

/**
 * Get the current stored user ID without generating a new one.
 * Returns null if no ID has been generated yet.
 */
export function getStoredUserId(): string | null {
  if (typeof window !== "undefined") {
    return localStorage.getItem("saathi_user_id");
  }
  return null;
}
