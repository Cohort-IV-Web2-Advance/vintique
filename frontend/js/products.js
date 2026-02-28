// /* ── PRODUCTS.JS — Shop listing page logic ───────────────────────────────── */

// const ALL_MOCK = [
//   { id: 1, name: "Victorian Cameo Brooch", price: 89.99, stock_quantity: 5, description: "Hand-carved 19th-century cameo on gold-filled filigree. Circa 1880s, excellent wearable condition.", image_url: "https://images.unsplash.com/photo-1602751584552-8ba73aad10e1?w=600&q=80", category: "Jewelry" },
//   { id: 2, name: "Art Deco Vanity Mirror", price: 145.00, stock_quantity: 2, description: "Exquisite beveled mirror with original chrome stand. Geometric etched border, 1930s.", image_url: "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=600&q=80", category: "Home Décor" },
//   { id: 3, name: "1950s Leather Satchel", price: 210.00, stock_quantity: 3, description: "Hand-stitched cognac leather. Post-war era. Original brass hardware, rich patina.", image_url: "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=600&q=80", category: "Bags" },
//   { id: 4, name: "Edwardian Tea Service", price: 320.00, stock_quantity: 1, description: "Complete 6-piece bone china with hand-painted roses and gold gilding, circa 1905.", image_url: "https://images.unsplash.com/photo-1563729784474-d77dbb933a9e?w=600&q=80", category: "Kitchenware" },
//   { id: 5, name: "Brass Compass Timepiece", price: 175.00, stock_quantity: 4, description: "Victorian explorer's pocket compass + miniature timepiece. Engraved brass, original leather pouch.", image_url: "https://images.unsplash.com/photo-1585565804112-f201f68c48b4?w=600&q=80", category: "Accessories" },
//   { id: 6, name: "Silk Kimono Robe 1920s", price: 265.00, stock_quantity: 2, description: "Authentic Taisho period silk kimono. Hand-embroidered chrysanthemums in gold and crimson.", image_url: "https://images.unsplash.com/photo-1558171813-a08ccd5e6b95?w=600&q=80", category: "Clothing" },
//   { id: 7, name: "Royal Typewriter 1948", price: 395.00, stock_quantity: 1, description: "Fully restored Royal Quiet De Luxe in forest green. New ribbon, cleaned. Types beautifully.", image_url: "https://images.unsplash.com/photo-1488190211105-8b0e65b80b4e?w=600&q=80", category: "Collectibles" },
//   { id: 8, name: "Amber Bakelite Necklace", price: 72.00, stock_quantity: 6, description: "Honey-amber Bakelite graduated beads, circa 1940s. Genuine Bakelite tested. Secure original clasp.", image_url: "https://images.unsplash.com/photo-1611085583191-a3b181a88401?w=600&q=80", category: "Jewelry" },
//   { id: 9, name: "French Enamel Compact", price: 58.00, stock_quantity: 8, description: "Limoges-style enamel powder compact with painted garden scene. Gilt brass, 1930s Paris.", image_url: "https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=600&q=80", category: "Accessories" },
//   { id: 10, name: "Teak Writing Bureau", price: 540.00, stock_quantity: 1, description: "Scandinavian mid-century teak bureau with original brass handles. Fully restored, 1960s.", image_url: "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=600&q=80", category: "Home Décor" },
//   { id: 11, name: "Beaded Evening Purse", price: 95.00, stock_quantity: 3, description: "1920s flapper-era beaded evening bag with micro-bead floral pattern. Silver-tone frame.", image_url: "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=600&q=80", category: "Bags" },
//   { id: 12, name: "Enamel Pill Box Set", price: 44.00, stock_quantity: 10, description: "Set of three hand-painted enamel pill boxes with floral motifs. Perfect collectible or gift.", image_url: "https://images.unsplash.com/photo-1563729784474-d77dbb933a9e?w=600&q=80", category: "Collectibles" },
// ];

// const CATEGORIES = ["All", "Jewelry", "Home Décor", "Bags", "Kitchenware", "Accessories", "Clothing", "Collectibles"];

// let allProducts = [];
// let activeCategory = 'All';
// let activePriceRange = 'all';
// let activeSearch = '';
// let activeSort = 'newest';
// let inStockOnly = false;

// // ── INIT ──────────────────────────────────────────────────────────────────────
// async function initProducts() {
//   // Read URL params
//   const params = new URLSearchParams(window.location.search);
//   const urlCat = params.get('category');
//   if (urlCat) activeCategory = decodeURIComponent(urlCat);

//   // Load products
//   try {
//     allProducts = await productsAPI.getAll();
//   } catch {
//     allProducts = ALL_MOCK;
//   }

//   buildCategoryFilters();
//   bindEvents();
//   renderProducts();
// }

// function buildCategoryFilters() {
//   const container = document.getElementById('category-filters');
//   if (!container) return;
//   container.innerHTML = CATEGORIES.map(cat => `
//     <label class="flex items-center gap-2 cursor-pointer">
//       <input type="radio" name="category" value="${cat}"
//         ${cat === activeCategory ? 'checked' : ''} class="accent-amber" />
//       <span class="text-sm text-brown hover:text-amber transition-colors">${cat}</span>
//     </label>
//   `).join('');

//   container.querySelectorAll('input[name="category"]').forEach(el => {
//     el.addEventListener('change', (e) => { activeCategory = e.target.value; renderProducts(); });
//   });
// }

// function bindEvents() {
//   document.getElementById('search-input')?.addEventListener('input', e => {
//     activeSearch = e.target.value.toLowerCase();
//     renderProducts();
//   });

//   document.querySelectorAll('input[name="price"]').forEach(el => {
//     el.addEventListener('change', e => { activePriceRange = e.target.value; renderProducts(); });
//   });

//   document.getElementById('sort-select')?.addEventListener('change', e => {
//     activeSort = e.target.value;
//     renderProducts();
//   });

//   document.getElementById('in-stock-filter')?.addEventListener('change', e => {
//     inStockOnly = e.target.checked;
//     renderProducts();
//   });
// }

// function filterAndSort(products) {
//   let list = [...products];

//   // Category
//   if (activeCategory !== 'All') list = list.filter(p => p.category === activeCategory);

//   // Search
//   if (activeSearch) list = list.filter(p =>
//     p.name.toLowerCase().includes(activeSearch) ||
//     (p.description || '').toLowerCase().includes(activeSearch)
//   );

//   // Price
//   if (activePriceRange !== 'all') {
//     const [min, max] = activePriceRange.split('-').map(Number);
//     list = list.filter(p => max ? (p.price >= min && p.price <= max) : p.price >= min);
//   }

//   // Stock
//   if (inStockOnly) list = list.filter(p => p.stock_quantity > 0);

//   // Sort
//   list.sort((a, b) => {
//     if (activeSort === 'price-asc')  return a.price - b.price;
//     if (activeSort === 'price-desc') return b.price - a.price;
//     if (activeSort === 'name-az')    return a.name.localeCompare(b.name);
//     return (b.id || 0) - (a.id || 0); // newest
//   });

//   return list;
// }

// function renderProducts() {
//   const grid = document.getElementById('product-grid');
//   const empty = document.getElementById('empty-state');
//   const count = document.getElementById('result-count');
//   if (!grid) return;

//   const filtered = filterAndSort(allProducts);

//   if (count) count.textContent = `${filtered.length} item${filtered.length !== 1 ? 's' : ''} found`;

//   if (filtered.length === 0) {
//     grid.classList.add('hidden');
//     empty?.classList.remove('hidden');
//     return;
//   }

//   grid.classList.remove('hidden');
//   empty?.classList.add('hidden');

//   grid.innerHTML = '';
//   filtered.forEach((p, i) => {
//     const card = buildProductCard(p, i);
//     // Override href for pages/ directory
//     card.querySelectorAll('[href]').forEach(el => {
//       el.href = el.href.replace('/pages/', '');
//     });
//     grid.appendChild(card);
//   });
// }

// function resetFilters() {
//   activeCategory = 'All';
//   activePriceRange = 'all';
//   activeSearch = '';
//   activeSort = 'newest';
//   inStockOnly = false;
//   document.getElementById('search-input').value = '';
//   document.getElementById('sort-select').value = 'newest';
//   document.getElementById('in-stock-filter').checked = false;
//   document.querySelector('input[name="category"][value="All"]').checked = true;
//   document.querySelector('input[name="price"][value="all"]').checked = true;
//   renderProducts();
// }

// document.addEventListener('DOMContentLoaded', initProducts);
