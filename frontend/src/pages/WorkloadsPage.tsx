import { FormEvent, useState } from 'react';
import { apiFetch } from '../api-client/http';

export function WorkloadsPage() {
  const [clusterId, setClusterId] = useState(1);
  const [namespace, setNamespace] = useState('default');
  const [workloads, setWorkloads] = useState<Record<string, unknown>>({});

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    const response = await apiFetch(`/k8s/${clusterId}/workloads?namespace=${encodeURIComponent(namespace)}`);
    setWorkloads(response);
  };

  return (
    <section>
      <div className="card">
        <h2>Workloads</h2>
        <form onSubmit={onSubmit}>
          <label>Cluster ID</label>
          <input type="number" value={clusterId} onChange={(e) => setClusterId(Number(e.target.value))} />
          <label>Namespace</label>
          <input value={namespace} onChange={(e) => setNamespace(e.target.value)} />
          <button type="submit">Load Workloads</button>
        </form>
        <pre>{JSON.stringify(workloads, null, 2)}</pre>
      </div>
    </section>
  );
}
