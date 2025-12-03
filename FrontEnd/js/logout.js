(function () {
  // Se quiser preservar algo, tire daqui.
  const KEYS_TO_KEEP = []; // por enquanto não preservamos nada

  function clearStorageComSeguranca() {
    try {
      // Se quiser ser fino e limpar só algumas chaves, comente o clear()
      // e use removeItem nas chaves específicas.
      const backup = {};
      KEYS_TO_KEEP.forEach((k) => {
        const v = localStorage.getItem(k);
        if (v !== null) backup[k] = v;
      });

      // mata TUDO da sessão no browser (tokens, carrinho, etc.)
      localStorage.clear();

      // regrava o que você quiser manter
      Object.entries(backup).forEach(([k, v]) => {
        localStorage.setItem(k, v);
      });
    } catch (e) {
      console.error("Erro limpando storage no logout:", e);
    }
  }

  function doLogout(redirectTo) {
    clearStorageComSeguranca();

    // rota padrão pós-logout
    const target = redirectTo || "login.html";
    window.location.href = target;
  }

  function bindLogout(selector, redirectTo) {
    const els = document.querySelectorAll(selector);
    els.forEach((el) => {
      el.addEventListener("click", function (ev) {
        ev.preventDefault();
        ev.stopPropagation();

        const customTarget =
          redirectTo ||
          el.getAttribute("data-logout-target") ||
          el.getAttribute("href") ||
          "login.html";

        doLogout(customTarget);
      });
    });
  }

  // expõe um helper global caso você queira chamar manualmente
  window.AppLogout = {
    logout: doLogout,
    bind: bindLogout,
  };

  document.addEventListener("DOMContentLoaded", () => {
    // 1) qualquer coisa com data-logout
    bindLogout('[data-logout="true"]');

    // 2) compatibilidade com o seu id atual
    bindLogout("#menu-logout");
  });
})();
