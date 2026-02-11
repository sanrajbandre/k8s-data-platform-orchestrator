import { useQuery } from '@tanstack/react-query';
import { apiFetch } from '../api-client/http';

export function AdminPage() {
  const users = useQuery({
    queryKey: ['users'],
    queryFn: () => apiFetch('/users'),
  });

  return (
    <section>
      <div className="card">
        <h2>Admin</h2>
        <p>User, role, permission, and feature-flag management.</p>
        <pre>{JSON.stringify(users.data ?? [], null, 2)}</pre>
      </div>
    </section>
  );
}
