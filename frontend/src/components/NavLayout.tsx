import { NavLink, Outlet } from 'react-router-dom';

export function NavLayout() {
  return (
    <div className="layout">
      <aside className="sidebar">
        <h1>K8s Orchestrator</h1>
        <nav>
          <NavLink to="/">Cluster</NavLink>
          <NavLink to="/namespaces">Namespaces</NavLink>
          <NavLink to="/workloads">Workloads</NavLink>
          <NavLink to="/spark">Spark</NavLink>
          <NavLink to="/kafka">Kafka</NavLink>
          <NavLink to="/alerts">Alerts</NavLink>
          <NavLink to="/ai">AI Insights</NavLink>
          <NavLink to="/admin">Admin</NavLink>
        </nav>
      </aside>
      <main className="main">
        <Outlet />
      </main>
    </div>
  );
}
