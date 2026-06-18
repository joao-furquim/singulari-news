import { useAuth } from '../contexts/AuthContext';

export function useAuthGuard(openAuthModal: () => void) {
  const { isAuthenticated, setPendingAction } = useAuth();

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
