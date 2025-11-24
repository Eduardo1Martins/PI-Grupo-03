(function () {
  const CART_KEY = 'cart:v1';
  const badgeEl = document.getElementById('cart-count-badge');
  if (!badgeEl) return;

  /**
   * Retorna a quantidade total de itens no carrinho (somando as quantidades).
   */
  function getCount() {
    try {
      const state = JSON.parse(localStorage.getItem(CART_KEY) || '{"items":[]}');
      return (state.items || []).reduce(
        (sum, it) => sum + (parseInt(it.qty, 10) || 0),
        0
      );
    } catch {
      return 0;
    }
  }

  /**
   * Atualiza o texto e exibição da badge com base no total do carrinho.
   */
  function renderBadge() {
    const n = getCount();
    badgeEl.textContent = n;
    badgeEl.style.display = n > 0 ? 'inline-block' : 'none';
  }

  // Renderiza na carga inicial
  renderBadge();

  // Atualiza automaticamente se outro tab/janela alterar o carrinho
  window.addEventListener('storage', (e) => {
    if (e.key === CART_KEY) renderBadge();
  });

  // Expõe função global opcional para que outras partes do JS
  // possam forçar a atualização da badge (ex: após salvar carrinho)
  window.updateCartCountBadge = renderBadge;
})();