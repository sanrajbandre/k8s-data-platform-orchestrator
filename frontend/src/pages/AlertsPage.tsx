import { useQuery } from '@tanstack/react-query';
import { apiFetch } from '../api-client/http';

export function AlertsPage() {
  const incidents = useQuery({
    queryKey: ['incidents'],
    queryFn: () => apiFetch('/alerts/incidents'),
  });

  return (
    <section>
      <div className="card">
        <h2>Alerts</h2>
        <p>Rule management, incidents, and notification channels.</p>
        <pre>{JSON.stringify(incidents.data ?? [], null, 2)}</pre>
      </div>
    </section>
  );
}
