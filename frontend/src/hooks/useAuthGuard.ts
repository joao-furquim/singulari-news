/**
 * Hook for guarding user actions behind authentication.
 *
 * Returns `executeOrGuard`, a wrapper that either runs the given action
 * immediately (when authenticated) or stores it as a pending action and
 * opens the auth modal (when unauthenticated). After a successful login the
 * AuthContext replays the pending action automatically.
 *
 * @module useAuthGuard
 */

import { useAuth } from '../contexts/AuthContext';

/**
 * Provides a gate function that executes an action only when authenticated.
 *
 * @param openAuthModal - Callback that opens the authentication modal.
 * @returns An object with `executeOrGuard`, the gated action runner.
 *
 * @example
 * const { executeOrGuard } = useAuthGuard(() => setAuthOpen(true));
 * // In an onClick handler:
 * executeOrGuard(() => client.post('/news/123/favorite'));
 */
export function useAuthGuard(openAuthModal: () => void) {
  const { isAuthenticated, setPendingAction } = useAuth();

  /**
   * Run `action` immediately if the user is authenticated; otherwise store it
   * as a pending action and open the auth modal.
   *
   * @param action - Synchronous or async callback to execute.
   */
  const executeOrGuard = (action: () => void | Promise<void>) => {
    if (isAuthenticated) {
      void action();
    } else {
      setPendingAction(() => () => void action());
      openAuthModal();
    }
  };

  return { executeOrGuard };
}
