import React, { useState } from 'react';

function App() {
  const [token, setToken] = useState('');
  const [msg, setMsg] = useState('');
  const [user, setUser] = useState(null);

  async function register(e) {
    e.preventDefault();
    const username = e.target.username.value;
    const password = e.target.password.value;
    const res = await fetch('/api/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    setMsg((await res.json()).msg || 'Erro');
  }

  async function login(e) {
    e.preventDefault();
    const username = e.target.username.value;
    const password = e.target.password.value;
    const res = await fetch('/api/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    const data = await res.json();
    if (data.access_token) {
      setToken(data.access_token);
      setMsg('Login ok');
    } else {
      setMsg('Erro login');
    }
  }

  async function getMe() {
    const res = await fetch('/api/users/me', {
      headers: { Authorization: `Bearer ${token}` }
    });
    setUser(await res.json());
  }

  async function quantum() {
    const prompt = window.prompt("Prompt para quantum (ex: superposição)?", "superposição");
    const res = await fetch('/api/ia', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({ module: 'quantum', prompt })
    });
    setMsg(JSON.stringify(await res.json(), null, 2));
  }

  return (
    <div>
      <h1>AigroQuantumSaaS Frontend</h1>
      <form onSubmit={register}>
        <h2>Registrar</h2>
        <input name="username" placeholder="Usuário" />
        <input name="password" type="password" placeholder="Senha" />
        <button type="submit">Registrar</button>
      </form>
      <form onSubmit={login}>
        <h2>Login</h2>
        <input name="username" placeholder="Usuário" />
        <input name="password" type="password" placeholder="Senha" />
        <button type="submit">Entrar</button>
      </form>
      <button onClick={getMe} disabled={!token}>Meus Dados</button>
      <button onClick={quantum} disabled={!token}>Quantum Job</button>
      <pre>{msg}</pre>
      {user && <pre>{JSON.stringify(user, null, 2)}</pre>}
    </div>
  );
}

export default App;