/**
 * Recupera o token JWT do localStorage.
 * Mesma lógica da conta.html.
 */
function getToken() {
  const keys = ["access", "token", "token2"];
  for (const k of keys) {
    const v = localStorage.getItem(k);
    if (v) return String(v).replace(/^"|"$/g, "");
  }
  return null;
}

/**
 * Redireciona para a tela de login.
 */
function redirectToLogin() {
  window.location.href = "login.html";
}

/**
 * Garante que o usuário esteja autenticado.
 * - Se não houver token: redireciona.
 * - Se checkServer = true: faz uma chamada rápida à API para validar o token.
 */
async function ensureAuthenticated(options) {
  const opts = options || {};
  const checkServer = !!opts.checkServer;
  const redirectTo = opts.redirectTo || "login.html";

  const token = getToken();
  if (!token) {
    window.location.href = redirectTo;
    return null;
  }

  if (!checkServer) {
    return token;
  }

  try {
    const res = await fetch(`${API_BASE}/usuarios/me/`, {
      method: "GET",
      headers: {
        Accept: "application/json",
        Authorization: `Bearer ${token}`,
      },
    });

    if (res.status === 401) {
      // token expirado/inválido
      window.location.href = redirectTo;
      return null;
    }
  } catch (err) {
    console.warn("Erro ao validar sessão no servidor:", err);
    // aqui você decide: mantém na página ou manda pro login
    // se quiser ser mais rígido:
    // window.location.href = redirectTo;
  }

  return token;
}

// expõe no escopo global para uso nos outros scripts
window.Auth = {
  getToken,
  ensureAuthenticated,
  redirectToLogin,
};
