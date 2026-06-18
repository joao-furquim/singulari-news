import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

interface AdminRouteProps {
  children: React.ReactNode;
  roles: Array<'admin' | 'reviewer'>;
  redirectTo?: string;
}

export function AdminRoute({ children, roles, redirectTo = '/' }: AdminRouteProps) {
  const { user, isAuthenticated } = useAuth();

  if (!isAuthenticated || !user) return <Navigate to="/" replace />;
  if (!(roles as string[]).includes(user.role)) return <Navigate to={redirectTo} replace />;

  return <>{children}</>;
}
