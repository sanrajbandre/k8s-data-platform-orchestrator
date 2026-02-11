import { useQuery } from '@tanstack/react-query';
import { apiFetch } from '../api-client/http';

export function AIInsightsPage() {
  const usage = useQuery({
    queryKey: ['ai-usage'],
    queryFn: () => apiFetch('/ai/usage'),
  });

  return (
    <section>
      <div className="card">
        <h2>AI Insights</h2>
        <p>Incident summaries and token/cost telemetry.</p>
        <pre>{JSON.stringify(usage.data ?? {}, null, 2)}</pre>
      </div>
    </section>
  );
}
