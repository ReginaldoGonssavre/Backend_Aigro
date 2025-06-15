import React, { useState, useRef } from "react";
import "./App.css";

const sleep = ms => new Promise(res => setTimeout(res, ms));

function useInputAnimation() {
  const [focus, setFocus] = useState(false);
  const ref = useRef();
  return [
    ref,
    focus,
    () => setFocus(true),
    () => setFocus(false)
  ];
}

function GlowButton({ children, ...props }) {
  return (
    <button className="glow-btn" {...props}>
      <span>{children}</span>
      <svg className="glow-svg">
        <defs>
          <filter id="glow">
            <feGaussianBlur stdDeviation="3.5" result="coloredBlur"/>
            <feMerge>
              <feMergeNode in="coloredBlur"/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          </filter>
        </defs>
        <rect width="100%" height="100%" filter="url(#glow)" />
      </svg>
    </button>
  );
}

function FloatingLabelInput({
  label,
  type = "text",
  value,
  onChange,
  ...props
}) {
  const [ref, focus, onFocus, onBlur] = useInputAnimation();
  return (
    <div className={`input-float ${focus || value ? "active" : ""}`}>
      <input
        ref={ref}
        type={type}
        value={value}
        onChange={onChange}
        onFocus={onFocus}
        onBlur={onBlur}
        {...props}
      />
      <label>{label}</label>
      <div className="input-underline" />
    </div>
  );
}

function AnimatedCard({ active, children }) {
  return (
    <div className={`anim-card ${active ? "active" : ""}`}>
      {children}
    </div>
  );
}

function Toast({ message, show }) {
  return (
    <div className={`toast ${show ? "show" : ""}`}>
      {message}
    </div>
  );
}

function LoadingCircle({ loading }) {
  return (
    <div className={`loading-circle${loading ? " spin" : ""}`}>
      <svg viewBox="0 0 50 50">
        <circle cx="25" cy="25" r="22" />
      </svg>
    </div>
  );
}

function useFlash() {
  const [flash, setFlash] = useState(false);
  return [
    flash,
    () => {
      setFlash(true);
      setTimeout(() => setFlash(false), 800);
    }
  ];
}

function QuantumSparkle({ trigger }) {
  const [sparks, setSparks] = useState([]);
  React.useEffect(() => {
    if (trigger) {
      let arr = [];
      for (let i = 0; i < 14; i++) {
        arr.push({
          left: Math.random() * 100 + "%",
          top: Math.random() * 100 + "%",
          delay: Math.random() * 0.5
        });
      }
      setSparks(arr);
      setTimeout(() => setSparks([]), 1000);
    }
  }, [trigger]);
  return (
    <div className="quantum-sparkle">
      {sparks.map((s, i) => (
        <span
          key={i}
          style={{
            left: s.left,
            top: s.top,
            animationDelay: `${s.delay}s`
          }}
          className="spark"
        ></span>
      ))}
    </div>
  );
}

function App() {
  const [tab, setTab] = useState("login");
  const [form, setForm] = useState({ username: "", password: "" });
  const [token, setToken] = useState("");
  const [user, setUser] = useState(null);
  const [msg, setMsg] = useState("");
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState("");
  const [showToast, setShowToast] = useState(false);
  const [flash, triggerFlash] = useFlash();
  const [spark, setSpark] = useState(false);
  const [quantumResult, setQuantumResult] = useState(null);

  function showMessage(message) {
    setToast(message);
    setShowToast(true);
    setTimeout(() => setShowToast(false), 2200);
  }

  async function handleAuth(e) {
    e.preventDefault();
    setLoading(true);
    await sleep(500);
    try {
      const res = await fetch(
        tab === "register" ? "/api/register" : "/api/login",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(form)
        }
      );
      const data = await res.json();
      if (res.ok && tab === "register") {
        showMessage("Registrado com sucesso!");
        setTab("login");
        setForm({ username: "", password: "" });
      } else if (res.ok && data.access_token) {
        setToken(data.access_token);
        showMessage("Login efetuado!");
        triggerFlash();
      } else {
        showMessage(data.detail || "Erro!");
      }
    } catch {
      showMessage("Falha ao conectar.");
    }
    setLoading(false);
  }

  async function handleMe() {
    setLoading(true);
    await sleep(400);
    try {
      const res = await fetch("/api/users/me", {
        headers: { Authorization: `Bearer ${token}` }
      });
      setUser(await res.json());
      showMessage("Bem-vindo(a), " + form.username);
      triggerFlash();
    } catch {
      showMessage("Erro ao buscar usuário.");
    }
    setLoading(false);
  }

  async function handleQuantum() {
    setSpark(true);
    setQuantumResult(null);
    setLoading(true);
    await sleep(300);
    try {
      const prompt = window.prompt("Prompt para quantum?", "superposição");
      if (!prompt) return setLoading(false);
      const res = await fetch("/api/ia", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ module: "quantum", prompt })
      });
      const result = await res.json();
      setQuantumResult(result.result || result);
      showMessage("Quantum job executado!");
    } catch {
      showMessage("Erro Quantum!");
    }
    setLoading(false);
    setTimeout(() => setSpark(false), 1200);
  }

  function logout() {
    setToken("");
    setUser(null);
    setQuantumResult(null);
    showMessage("Logout feito.");
  }

  return (
    <div className="app-root">
      <QuantumSparkle trigger={spark || flash} />
      <Toast message={toast} show={showToast} />
      <LoadingCircle loading={loading} />
      <div className="glass-bg">
        <header>
          <h1>
            <span className="logo-q">Q</span>
            <span>AigroQuantumSaaS</span>
          </h1>
        </header>
        <nav>
          <GlowButton onClick={() => setTab("login")} aria-pressed={tab === "login"}>
            Login
          </GlowButton>
          <GlowButton onClick={() => setTab("register")} aria-pressed={tab === "register"}>
            Registrar
          </GlowButton>
        </nav>
        {!token && (
          <AnimatedCard active>
            <form className="auth-form" onSubmit={handleAuth}>
              <FloatingLabelInput
                label="Usuário"
                value={form.username}
                onChange={e =>
                  setForm(f => ({ ...f, username: e.target.value }))
                }
                autoComplete="username"
              />
              <FloatingLabelInput
                label="Senha"
                type="password"
                value={form.password}
                onChange={e =>
                  setForm(f => ({ ...f, password: e.target.value }))
                }
                autoComplete={tab === "login" ? "current-password" : "new-password"}
              />
              <GlowButton type="submit">
                {tab === "login" ? "Entrar" : "Registrar"}
              </GlowButton>
            </form>
          </AnimatedCard>
        )}

        {token && (
          <AnimatedCard active>
            <div className="user-panel">
              <GlowButton onClick={handleMe}>Meus Dados</GlowButton>
              <GlowButton onClick={handleQuantum}>Quantum Job</GlowButton>
              <GlowButton onClick={logout}>Logout</GlowButton>
              {user && (
                <div className={`user-box${flash ? " flash" : ""}`}>
                  <span>Usuário: {user.username}</span>
                  <span>Criado: {new Date(user.created_at).toLocaleString()}</span>
                  <span>Admin: {user.is_admin ? "Sim" : "Não"}</span>
                </div>
              )}
              {quantumResult && (
                <pre className="quantum-result">
                  {JSON.stringify(quantumResult, null, 2)}
                </pre>
              )}
            </div>
          </AnimatedCard>
        )}

        <footer>
          <div>
            <span>
              &copy; {new Date().getFullYear()} AigroQuantumSaaS
            </span>
            <a href="https://github.com/ReggizzAgent" target="_blank" rel="noopener noreferrer">
              GitHub
            </a>
          </div>
        </footer>
      </div>
    </div>
  );
}

export default App;

/*
Linhas: 340 (aprox.)
Recursos:
- Responsivo (ver CSS)
- Floating label input, anim-card, toast, loading, botões glow, quantum sparkles
- UX moderna: feedback visual instantâneo, transições, feedbacks, navegação fluida
- Pronto para mobile/tablet/desktop (CSS no arquivo App.css)
*/