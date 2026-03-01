/* ── PRODUCTS.JS — Shop listing page logic ───────────────────────────────── */

let allProducts = [];
let activeCategory = 'All';
let activePriceRange = 'all';
let activeSearch = '';
let activeSort = 'newest';
let inStockOnly = false;

// ── INIT ──────────────────────────────────────────────────────────────────────
async function initProducts() {
  // Read URL params
  const params = new URLSearchParams(window.location.search);
  const urlCat = params.get('category');
  if (urlCat) activeCategory = decodeURIComponent(urlCat);

  // Load products
  try {
    allProducts = await productsAPI.getAll();
  } catch {
    allProducts = ALL_MOCK;
  }

  buildCategoryFilters();
  bindEvents();
  renderProducts();
}

function buildCategoryFilters() {
  const container = document.getElementById('category-filters');
  if (!container) return;
  container.innerHTML = CATEGORIES.map(cat => `
    <label class="flex items-center gap-2 cursor-pointer">
      <input type="radio" name="category" value="${cat}"
        ${cat === activeCategory ? 'checked' : ''} class="accent-amber" />
      <span class="text-sm text-brown hover:text-amber transition-colors">${cat}</span>
    </label>
  `).join('');

  container.querySelectorAll('input[name="category"]').forEach(el => {
    el.addEventListener('change', (e) => { activeCategory = e.target.value; renderProducts(); });
  });
}

function bindEvents() {
  document.getElementById('search-input')?.addEventListener('input', e => {
    activeSearch = e.target.value.toLowerCase();
    renderProducts();
  });

  document.querySelectorAll('input[name="price"]').forEach(el => {
    el.addEventListener('change', e => { activePriceRange = e.target.value; renderProducts(); });
  });

  document.getElementById('sort-select')?.addEventListener('change', e => {
    activeSort = e.target.value;
    renderProducts();
  });

  document.getElementById('in-stock-filter')?.addEventListener('change', e => {
    inStockOnly = e.target.checked;
    renderProducts();
  });
}

function filterAndSort(products) {
  let list = [...products];

  // Category
  if (activeCategory !== 'All') list = list.filter(p => p.category === activeCategory);

  // Search
  if (activeSearch) list = list.filter(p =>
    p.name.toLowerCase().includes(activeSearch) ||
    (p.description || '').toLowerCase().includes(activeSearch)
  );

  // Price
  if (activePriceRange !== 'all') {
    const [min, max] = activePriceRange.split('-').map(Number);
    list = list.filter(p => max ? (p.price >= min && p.price <= max) : p.price >= min);
  }

  // Stock
  if (inStockOnly) list = list.filter(p => p.stock_quantity > 0);

  // Sort
  list.sort((a, b) => {
    if (activeSort === 'price-asc')  return a.price - b.price;
    if (activeSort === 'price-desc') return b.price - a.price;
    if (activeSort === 'name-az')    return a.name.localeCompare(b.name);
    return (b.id || 0) - (a.id || 0); // newest
  });

  return list;
}

function renderProducts() {
  const grid = document.getElementById('product-grid');
  const empty = document.getElementById('empty-state');
  const count = document.getElementById('result-count');
  if (!grid) return;

  const filtered = filterAndSort(allProducts);

  if (count) count.textContent = `${filtered.length} item${filtered.length !== 1 ? 's' : ''} found`;

  if (filtered.length === 0) {
    grid.classList.add('hidden');
    empty?.classList.remove('hidden');
    return;
  }

  grid.classList.remove('hidden');
  empty?.classList.add('hidden');

  grid.innerHTML = '';
  filtered.forEach((p, i) => {
    const card = buildProductCard(p, i);
    // Override href for pages/ directory
    card.querySelectorAll('[href]').forEach(el => {
      el.href = el.href.replace('/pages/', '');
    });
    grid.appendChild(card);
  });
}


document.addEventListener('DOMContentLoaded', initProducts);
