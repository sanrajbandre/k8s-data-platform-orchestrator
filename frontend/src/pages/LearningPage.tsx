import { useQuery } from '@tanstack/react-query';
import { apiFetch } from '../api-client/http';

type LearningItem = {
  phase: string;
  title: string;
  goal: string;
  deliverables: string[];
};

type OSSItem = {
  name: string;
  repository: string;
  license: string;
  usage: string;
};

export function LearningPage() {
  const query = useQuery({
    queryKey: ['platform-learning'],
    queryFn: async () => {
      const [about, oss, learning] = await Promise.all([
        apiFetch('/platform/about'),
        apiFetch('/platform/oss-repositories'),
        apiFetch('/platform/learning-path'),
      ]);
      return { about, oss, learning };
    },
  });

  if (query.isLoading) return <div className="card">Loading learning workspace...</div>;
  if (query.error) return <div className="card">Failed to load: {String(query.error)}</div>;

  const about = query.data?.about;
  const ossItems: OSSItem[] = query.data?.oss?.items ?? [];
  const learningItems: LearningItem[] = query.data?.learning?.items ?? [];

  return (
    <section>
      <div className="card">
        <h2>Learning + Development Workspace</h2>
        <p>
          Product: <strong>{about?.product?.name ?? 'N/A'}</strong>
        </p>
        <p>Policy: {about?.product?.implementation_policy?.rule ?? 'N/A'}</p>
      </div>

      <div className="card">
        <h3>Open Source Repositories Used</h3>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr>
              <th align="left">Project</th>
              <th align="left">License</th>
              <th align="left">Usage</th>
            </tr>
          </thead>
          <tbody>
            {ossItems.map((item) => (
              <tr key={item.name}>
                <td>
                  <a href={item.repository} target="_blank" rel="noreferrer">
                    {item.name}
                  </a>
                </td>
                <td>{item.license}</td>
                <td>{item.usage}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="card">
        <h3>Learning Path</h3>
        {learningItems.map((item) => (
          <div key={item.phase} style={{ marginBottom: 16 }}>
            <strong>
              {item.phase}: {item.title}
            </strong>
            <p>{item.goal}</p>
            <ul>
              {item.deliverables.map((d) => (
                <li key={`${item.phase}-${d}`}>{d}</li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </section>
  );
}
