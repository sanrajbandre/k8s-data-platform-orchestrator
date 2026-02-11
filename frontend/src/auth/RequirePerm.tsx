import { ReactElement } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuthStore } from './store';

export function RequirePerm({ perm, children }: { perm: string; children: ReactElement }) {
  const perms = useAuthStore((s) => s.permissions);
  if (!perms.includes(perm) && !perms.includes('admin.all')) {
    return <Navigate to="/" replace />;
  }
  return children;
}
