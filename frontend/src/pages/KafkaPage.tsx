import { FormEvent, useState } from 'react';
import { apiFetch } from '../api-client/http';

export function KafkaPage() {
  const [clusterId, setClusterId] = useState(1);
  const [namespace, setNamespace] = useState('default');
  const [name, setName] = useState('kafka-main');
  const [mode, setMode] = useState('kraft');
  const [kafkaVersion, setKafkaVersion] = useState('4.0.0');
  const [strimziVersion, setStrimziVersion] = useState('0.46.0');
  const [result, setResult] = useState('');

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    const payload = {
      cluster_id: clusterId,
      namespace,
      kafka_mode: mode,
      kafka_version: kafkaVersion,
      strimzi_version: strimziVersion,
      spec_json: { name },
    };
    try {
      const response = await apiFetch('/services/kafka/clusters', {
        method: 'POST',
        body: JSON.stringify(payload),
      });
      setResult(JSON.stringify(response, null, 2));
    } catch (err) {
      setResult(String(err));
    }
  };

  return (
    <section>
      <div className="card">
        <h2>Kafka</h2>
        <p>KRaft is default. Legacy ZooKeeper mode is pinned to Kafka 3.8.1 + Strimzi 0.45.x.</p>
        <form onSubmit={onSubmit}>
          <label>Cluster ID</label>
          <input type="number" value={clusterId} onChange={(e) => setClusterId(Number(e.target.value))} />
          <label>Namespace</label>
          <input value={namespace} onChange={(e) => setNamespace(e.target.value)} />
          <label>Name</label>
          <input value={name} onChange={(e) => setName(e.target.value)} />
          <label>Mode</label>
          <select
            value={mode}
            onChange={(e) => {
              const next = e.target.value;
              setMode(next);
              if (next === 'legacy_zookeeper') {
                setKafkaVersion('3.8.1');
                setStrimziVersion('0.45.1');
              } else {
                setKafkaVersion('4.0.0');
                setStrimziVersion('0.46.0');
              }
            }}
          >
            <option value="kraft">kraft</option>
            <option value="legacy_zookeeper">legacy_zookeeper</option>
          </select>
          <label>Kafka Version</label>
          <input value={kafkaVersion} onChange={(e) => setKafkaVersion(e.target.value)} />
          <label>Strimzi Version</label>
          <input value={strimziVersion} onChange={(e) => setStrimziVersion(e.target.value)} />
          <button type="submit">Create Kafka Intent</button>
        </form>
        <pre>{result}</pre>
      </div>
    </section>
  );
}
