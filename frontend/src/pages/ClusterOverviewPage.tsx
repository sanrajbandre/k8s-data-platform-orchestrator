import { useQuery } from '@tanstack/react-query';
import { apiFetch } from '../api-client/http';

export function ClusterOverviewPage() {
  const metrics = useQuery({
    queryKey: ['cluster-overview'],
    queryFn: () => apiFetch('/metrics/dashboards/cluster-overview'),
  });

  return (
    <section>
      <div className="card">
        <h2>Cluster Overview</h2>
        <p>Node health, CPU/memory, pod restarts, and summary cards.</p>
        <pre>{JSON.stringify(metrics.data ?? {}, null, 2)}</pre>
      </div>
    </section>
  );
}
