(function () {
  const CART_KEY = 'cart:v1';
  const badgeEl = document.getElementById('cart-count-badge');
  if (!badgeEl) return;

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

  function renderBadge() {
    const n = getCount();
    badgeEl.textContent = n;
    badgeEl.style.display = n > 0 ? 'inline-block' : 'none';
  }

  renderBadge();

  window.addEventListener('storage', (e) => {
    if (e.key === CART_KEY) renderBadge();
  });

  if (window.CartStore && typeof window.CartStore.save === 'function') {
    const originalSave = window.CartStore.save.bind(window.CartStore);
    window.CartStore.save = function (state) {
      const r = originalSave(state);
      renderBadge();
      return r;
    };
  }

  window.updateCartCountBadge = renderBadge;
})();
