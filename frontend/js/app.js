/* ── VINTIQUE APP.JS — Core utilities, cart, auth, API layer ─────────────── */

'use strict';

// ── API BASE ────────────────────────────────────────────────────────────────
const API_BASE = "https://vintique.onrender.com";

// ── API HELPER ──────────────────────────────────────────────────────────────
async function apiFetch(endpoint, options = {}) {
  const token = getToken();
  const headers = { 'Content-Type': 'application/json', ...options.headers };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  try {
    const res = await fetch(`${API_BASE}${endpoint}`, { ...options, headers });
    if (res.status === 401) { clearAuth(); window.location.href = 'login.html'; return null; }
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `HTTP ${res.status}`);
    }
    return res.status === 204 ? null : res.json();
  } catch (e) {
    console.error(`API error [${endpoint}]:`, e.message);
    throw e;
  }
}

// ── AUTH ────────────────────────────────────────────────────────────────────
function getToken() {
  const token = localStorage.getItem('vintique_token');
  return token && token !== 'undefined' ? token : null;
}
function getUser(){ try { return JSON.parse(localStorage.getItem('vintique_user')); } catch { return null; } }
function isLoggedIn(){ return !!getToken(); }
function isAdmin(){ const u = getUser(); return u?.is_admin === true; }

function setAuth(token, user) {
  localStorage.setItem('vintique_token', token);
  localStorage.setItem('vintique_user', JSON.stringify(user));
}

function clearAuth() {
  localStorage.removeItem('vintique_token');
  localStorage.removeItem('vintique_user');
}

async function register(userData) {
  const res = await fetch(`${API_BASE}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(userData)
  });

  const data = await res.json();

  if (!res.ok) throw new Error(data.message || "Registration failed");

  if (data.access_token) {
    setAuth(data.access_token, data.user || {});
  }

  return data;
}

async function login(email, password) {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      email: email,
      password: password
    })
  });

  const data = await res.json();
  // console.log("LOGIN RESPONSE:", data);

  if (!res.ok) throw new Error(data.detail || "Login failed");

  const token = data.access_token || data.token;

  if (!token) throw new Error("No token returned");
  const user = data.user || { email }
  setAuth(token, user);

  return data;
}

function logout() {
  clearAuth();
  cart.clear();
  window.location.href = 'login.html';
}

// ── CART (localStorage + API sync) ─────────────────────────────────────────
const cart = {
  _key: 'vintique_cart',

  get items() {
    try {
      return JSON.parse(localStorage.getItem(this._key)) || [];
    } catch {
      return [];
    }
  },

  _save(items) {
    localStorage.setItem(this._key, JSON.stringify(items));
    this._updateUI();
  },

  async add(product, qty = 1) {
    const items = this.items;

    const idx = items.findIndex(i => i.id === product.id);

    if (idx > -1) {
      items[idx].qty = Math.min(items[idx].qty + qty, product.stock_quantity || 99);
    } else {
      items.push({
        id: product.id,
        name: product.name,
        price: product.price,
        image_url: product.image_url,
        qty
      });
    }

    this._save(items);
    showToast(`"${product.name}" added to cart`);

    if (isLoggedIn()) {
      try {
        await apiFetch('/cart/add', {
          method: 'POST',
          body: JSON.stringify({
            product_id: product.id,
            quantity: qty
          })
        });
      } catch (e) {
        console.error("Cart add failed:", e.message);
      }
    }
  },

  async remove(productId) {
    const items = this.items.filter(i => i.id !== productId);
    this._save(items);

    if (isLoggedIn()) {
      try {
        await apiFetch('/cart/remove', {
          method: 'POST',
          body: JSON.stringify({ product_id: productId })
        });
      } catch (e) {
        console.error("Remove failed:", e.message);
      }
    }
  },

  async updateQty(productId, qty) {
    const items = this.items.map(i =>
      i.id === productId ? { ...i, qty: Math.max(1, qty) } : i
    );

    this._save(items);

    if (isLoggedIn()) {
      try {
        await apiFetch('/cart/update-qty', {
          method: 'PATCH',
          body: JSON.stringify({
            product_id: productId,
            quantity: qty
          })
        });
      } catch (e) {
        console.error("Update qty failed:", e.message);
      }
    }
  },

  async clear() {
    localStorage.removeItem(this._key);
    this._updateUI();

    if (isLoggedIn()) {
      try {
        await apiFetch('/cart/clear', { method: 'POST' });
      } catch (e) {
        console.error("Clear failed:", e.message);
      }
    }
  },

  get total() {
    return this.items.reduce((sum, item) => sum + item.price * item.qty, 0);
  },

  get count() {
    return this.items.reduce((sum, item) => sum + item.qty, 0);
  },

  _updateUI() {
    const badge = document.getElementById("cart-count");
    if (!badge) return;

    const count = this.count;

    badge.textContent = count;
    badge.classList.toggle("hidden", count === 0);
  },

  async fetchServerCart() {
    if (!isLoggedIn()) return;

    try {
      const serverItems = await apiFetch('/cart');
      const items = serverItems.map(i => ({
        id: i.product_id,
        name: i.product.name,
        price: i.product.price,
        image_url: i.product.image_url,
        qty: i.quantity
      }));

      this._save(items);
    } catch (e) {
      console.error("Fetch cart failed:", e.message);
    }
  }
};

// ── PRODUCTS API ─────────────────────────────────────────────────────────
const productsAPI = {
  getAll(params = {}) {
    const q = new URLSearchParams(params).toString();
    return apiFetch(`/products${q ? '?' + q : ''}`);
  },
  getOne(id) { return apiFetch(`/products/${id}`); },
};

// ── ORDERS API ───────────────────────────────────────────────────────────────
const ordersAPI = {
  checkout(payload) { return apiFetch('/orders/checkout', { method: 'POST', body: JSON.stringify(payload) }); },
  history(){ return apiFetch('/orders/history'); },
};

// ── ADMIN API ─────────────────────────────────────────────────────────────────
const adminAPI = {
  getOrders()   { return apiFetch('/admin/orders'); },
  getUsers()    { return apiFetch('/admin/users'); },
  getProducts() { return apiFetch('/admin/products'); },

  createProduct(formData) {
    return fetch(`${API_BASE}/inventory/product`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${getToken()}` },
      body: formData
    }).then(r => r.json());
  },

  updateProduct(id, formData) {
    return fetch(`${API_BASE}/inventory/product/${id}`, {
      method: 'PUT',
      headers: { Authorization: `Bearer ${getToken()}` },
      body: formData
    }).then(r => r.json());
  },

  deleteProduct(id) { return apiFetch(`/inventory/product/${id}`, { method: 'DELETE' }); },
};

// ── TOAST ──────
let _toastTimer;
function showToast(msg, type = 'success') {
  const el = document.getElementById('toast');
  const msgEl = document.getElementById('toast-msg');
  if (!el || !msgEl) return;

  msgEl.textContent = msg;
  el.classList.remove('hidden');
  el.firstElementChild.classList.add('toast-enter');
  el.firstElementChild.style.backgroundColor = type === 'error' ? '#B55330' : '#5C3D2E';

  clearTimeout(_toastTimer);
  _toastTimer = setTimeout(() => el.classList.add('hidden'), 3000);
}

// ── NAVBAR AUTH STATE ─────────────────────────────────────────────────────────

function getUserSafe() {
  const token = getToken();
  const user = getUser();
  return token && user && Object.keys(user).length ? user : null;
}

function updateNavAuth() {
  const link = document.getElementById('auth-link');
  if (!link) return;

  if (isLoggedIn()) {
    link.textContent = 'Orders';
    link.href = 'orders.html';
  } else {
    link.textContent = 'Sign In';
    link.href = 'login.html';
  }
}

function updateMobileAuthLink() {
  const mobileAuthLink = document.getElementById('mobile-auth');
  if (!mobileAuthLink) return;

  if (isLoggedIn()) {
    mobileAuthLink.textContent = 'Orders';
    mobileAuthLink.href = 'orders.html';
  } else {
    mobileAuthLink.textContent = 'Sign In';
    mobileAuthLink.href = 'login.html';
  }
}

// ── NEWSLETTER ───────────────────────────────────────────────────────────────
function handleNewsletter(e) {
  e.preventDefault();
  document.getElementById('newsletter-msg')?.classList.remove('hidden');
  e.target.reset();
}

// ── FORMAT HELPERS ────────────────────────────────────────────────────────────
function formatPrice(n) { return `₦${Number(n).toFixed(2)}`; }
function formatDate(s)  { return new Date(s).toLocaleDateString('en-GB', { year: 'numeric', month: 'short', day: 'numeric' }); }

// ── PRODUCT CARD BUILDER ──────────────────────────────────────────────────────
function buildProductCard(p, delay = 0) {
  const card = document.createElement('div');
  card.className = 'product-card bg-white rounded-xl overflow-hidden fade-in';
  card.style.animationDelay = `${delay * 0.07}s`;
  card.innerHTML = `
    <a href="product.html?id=${p.id}" class="img-zoom block aspect-4/3">
      <img src="${p.image_url || 'https://images.unsplash.com/photo-1558171813-a08ccd5e6b95?w=600&q=80'}"
        alt="${p.name}" class="w-full h-full object-cover" loading="lazy"
        onerror="this.src='https://images.unsplash.com/photo-1558171813-a08ccd5e6b95?w=400&q=60'" />
    </a>
    <div class="p-4">
      <p class="text-muted text-[11px] font-sans tracking-widest uppercase mb-1">${p.category || 'Vintique'}</p>
      <h3 class="font-serif text-base text-brown font-semibold leading-tight line-clamp-2 mb-1">
        <a href="product.html?id=${p.id}" class="hover:text-amber transition-colors">${p.name}</a>
      </h3>
      <p class="text-muted text-xs line-clamp-2 mb-3">${p.description || ''}</p>
      <div class="flex items-center justify-between">
        <p class="text-lg text-amber font-semibold">${formatPrice(p.price)}</p>
        <button onclick="cart.add(${JSON.stringify(p).replace(/"/g, '&quot;')}, 1)"
          class="${p.stock_quantity > 0 ? 'bg-brown hover:bg-amber' : 'bg-muted cursor-not-allowed'} text-cream text-xs font-sans font-semibold px-3 py-2 rounded-lg transition-colors"
          ${p.stock_quantity <= 0 ? 'disabled' : ''}>
          ${p.stock_quantity > 0 ? 'Add to Cart' : 'Sold Out'}
        </button>
      </div>
      ${p.stock_quantity <= 3 && p.stock_quantity > 0 ? `<p class="text-rust text-[11px] font-sans mt-2">Only ${p.stock_quantity} left!</p>` : ''}
    </div>
  `;
  return card;
}

// ── INIT ──────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  cart._updateUI();

  if (isLoggedIn()) {
    cart.fetchServerCart();
  }

  updateNavAuth();
  updateMobileAuthLink();

  // Navbar scroll effect
  window.addEventListener('scroll', () => {
    const nav = document.getElementById('navbar');
    if (nav) nav.classList.toggle('shadow-md', window.scrollY > 30);
  });
  
});