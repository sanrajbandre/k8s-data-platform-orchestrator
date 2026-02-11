import { FormEvent, useState } from 'react';
import { apiFetch } from '../api-client/http';

export function NamespacesPage() {
  const [clusterId, setClusterId] = useState(1);
  const [namespaces, setNamespaces] = useState<string[]>([]);

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    const response = await apiFetch(`/clusters/${clusterId}/namespaces`);
    setNamespaces(response.items ?? []);
  };

  return (
    <section>
      <div className="card">
        <h2>Namespaces</h2>
        <form onSubmit={onSubmit}>
          <label>Cluster ID</label>
          <input type="number" value={clusterId} onChange={(e) => setClusterId(Number(e.target.value))} />
          <button type="submit">Load Namespaces</button>
        </form>
        <pre>{JSON.stringify(namespaces, null, 2)}</pre>
      </div>
    </section>
  );
}
