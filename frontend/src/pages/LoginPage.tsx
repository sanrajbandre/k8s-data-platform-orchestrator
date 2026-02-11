import { FormEvent, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../auth/store';
import { apiFetch } from '../api-client/http';

export function LoginPage() {
  const navigate = useNavigate();
  const setTokens = useAuthStore((s) => s.setTokens);
  const setPermissions = useAuthStore((s) => s.setPermissions);
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('admin123!');
  const [error, setError] = useState('');

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    try {
      const data = await apiFetch('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ username, password }),
      });
      setTokens(data.access_token, data.refresh_token);
      const me = await apiFetch('/auth/me');
      setPermissions(me.permissions ?? []);
      navigate('/');
    } catch (err) {
      setError(String(err));
    }
  };

  return (
    <main className="main" style={{ maxWidth: 480, margin: '80px auto' }}>
      <div className="card">
        <h2>Login</h2>
        <form onSubmit={onSubmit}>
          <label>Username</label>
          <input value={username} onChange={(e) => setUsername(e.target.value)} />
          <label>Password</label>
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
          <button type="submit">Sign in</button>
          {error && <p>{error}</p>}
        </form>
      </div>
    </main>
  );
}
