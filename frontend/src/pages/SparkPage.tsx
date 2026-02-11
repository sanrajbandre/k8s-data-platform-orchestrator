import { FormEvent, useState } from 'react';
import { apiFetch } from '../api-client/http';

export function SparkPage() {
  const [clusterId, setClusterId] = useState(1);
  const [namespace, setNamespace] = useState('default');
  const [name, setName] = useState('spark-batch');
  const [image, setImage] = useState('ghcr.io/spark:4.0.0');
  const [result, setResult] = useState('');

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    try {
      const response = await apiFetch('/services/spark/applications', {
        method: 'POST',
        body: JSON.stringify({
          cluster_id: clusterId,
          namespace,
          spec_json: { name, image, type: 'Scala' },
        }),
      });
      setResult(JSON.stringify(response, null, 2));
    } catch (err) {
      setResult(String(err));
    }
  };

  return (
    <section>
      <div className="card">
        <h2>Spark 4.x</h2>
        <p>Deploy SparkApplication CR intents via operator mode.</p>
        <form onSubmit={onSubmit}>
          <label>Cluster ID</label>
          <input type="number" value={clusterId} onChange={(e) => setClusterId(Number(e.target.value))} />
          <label>Namespace</label>
          <input value={namespace} onChange={(e) => setNamespace(e.target.value)} />
          <label>Name</label>
          <input value={name} onChange={(e) => setName(e.target.value)} />
          <label>Image</label>
          <input value={image} onChange={(e) => setImage(e.target.value)} />
          <button type="submit">Create Spark Intent</button>
        </form>
        <pre>{result}</pre>
      </div>
    </section>
  );
}
