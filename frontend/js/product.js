// /* ── PRODUCT.JS — Single product detail page ─────────────────────────────── */

// const MOCK = [
//   { id: 1, name: "Victorian Cameo Brooch", price: 89.99, stock_quantity: 5, description: "A stunning 19th-century hand-carved cameo brooch set in gold-filled filigree. Features a delicate profile portrait on genuine shell. Circa 1880s, in excellent wearable condition. Comes with a velvet presentation box and authenticity certificate.", image_url: "https://images.unsplash.com/photo-1602751584552-8ba73aad10e1?w=800&q=80", category: "Jewelry" },
//   { id: 2, name: "Art Deco Vanity Mirror", price: 145.00, stock_quantity: 2, description: "Exquisite Art Deco beveled mirror with original chrome stand and geometric etched border. A rare piece from the 1930s in stunning original condition.", image_url: "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=800&q=80", category: "Home Décor" },
//   { id: 3, name: "1950s Leather Satchel", price: 210.00, stock_quantity: 3, description: "Genuine hand-stitched leather satchel from the post-war era. Rich cognac patina developed over decades of loving use. Original brass hardware.", image_url: "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=800&q=80", category: "Bags" },
//   { id: 4, name: "Edwardian Tea Service", price: 320.00, stock_quantity: 1, description: "Complete 6-piece Edwardian porcelain tea service with hand-painted rose motifs and gold gilding. Bone china, circa 1905. All pieces intact.", image_url: "https://images.unsplash.com/photo-1563729784474-d77dbb933a9e?w=800&q=80", category: "Kitchenware" },
//   { id: 5, name: "Brass Compass Timepiece", price: 175.00, stock_quantity: 4, description: "Victorian-era explorer's pocket compass combined with a miniature timepiece. Engraved brass case with original leather pouch. Fully functional.", image_url: "https://images.unsplash.com/photo-1585565804112-f201f68c48b4?w=800&q=80", category: "Accessories" },
//   { id: 6, name: "Silk Kimono Robe 1920s", price: 265.00, stock_quantity: 2, description: "Authentic Japanese silk kimono robe from the Taisho period, featuring hand-embroidered chrysanthemums in vivid gold and crimson thread.", image_url: "https://images.unsplash.com/photo-1558171813-a08ccd5e6b95?w=800&q=80", category: "Clothing" },
//   { id: 7, name: "Royal Typewriter 1948", price: 395.00, stock_quantity: 1, description: "Fully restored Royal Quiet De Luxe typewriter in glossy forest green. New ribbon, cleaned and oiled. Types beautifully. A writer's dream.", image_url: "https://images.unsplash.com/photo-1488190211105-8b0e65b80b4e?w=800&q=80", category: "Collectibles" },
//   { id: 8, name: "Amber Bakelite Necklace", price: 72.00, stock_quantity: 6, description: "Warm honey-amber Bakelite graduated bead necklace, circa 1940s. Tests genuine Bakelite. Clasp original and secure.", image_url: "https://images.unsplash.com/photo-1611085583191-a3b181a88401?w=800&q=80", category: "Jewelry" },
// ];

// let currentProduct = null;
// let selectedQty = 1;

// async function initProductDetail() {
//   const id = parseInt(new URLSearchParams(window.location.search).get('id'));
//   if (!id) { window.location.href = 'products.html'; return; }

//   try {
//     currentProduct = await productsAPI.getOne(id);
//   } catch {
//     currentProduct = MOCK.find(p => p.id === id) || MOCK[0];
//   }

//   renderDetail(currentProduct);
//   renderRelated(currentProduct);
// }

// function renderDetail(p) {
//   document.title = `${p.name} — Vintique`;
//   document.getElementById('breadcrumb-name').textContent = p.name;

//   const container = document.getElementById('product-detail');
//   const inStock = p.stock_quantity > 0;

//   container.innerHTML = `
//     <!-- Image Column -->
//     <div class="fade-in">
//       <div class="relative rounded-2xl overflow-hidden bg-parchment/50 aspect-square">
//         <img id="main-img" src="${p.image_url || ''}" alt="${p.name}"
//           class="w-full h-full object-cover"
//           onerror="this.src='https://images.unsplash.com/photo-1558171813-a08ccd5e6b95?w=800&q=60'" />
//         ${!inStock ? '<div class="absolute inset-0 bg-darkbrown/50 flex items-center justify-center"><span class="bg-rust text-cream font-serif text-xl px-6 py-2 rounded-xl -rotate-6">Sold</span></div>' : ''}
//       </div>

//       <!-- Trust Badges -->
//       <div class="mt-5 grid grid-cols-3 gap-3">
//         <div class="bg-parchment/60 rounded-xl p-3 text-center">
//           <p class="text-amber text-xl mb-1">✓</p>
//           <p class="text-xs font-sans text-muted leading-tight">Authenticated</p>
//         </div>
//         <div class="bg-parchment/60 rounded-xl p-3 text-center">
//           <p class="text-amber text-xl mb-1">📦</p>
//           <p class="text-xs font-sans text-muted leading-tight">Secure Shipping</p>
//         </div>
//         <div class="bg-parchment/60 rounded-xl p-3 text-center">
//           <p class="text-amber text-xl mb-1">↩</p>
//           <p class="text-xs font-sans text-muted leading-tight">14-Day Returns</p>
//         </div>
//       </div>
//     </div>

//     <!-- Info Column -->
//     <div class="fade-in" style="animation-delay:0.1s">
//       <p class="text-amber text-xs tracking-[0.25em] uppercase font-sans mb-3">${p.category || 'Vintage'}</p>
//       <h1 class="font-serif text-4xl lg:text-5xl text-brown leading-tight mb-4">${p.name}</h1>

//       <!-- Price & Stock -->
//       <div class="flex items-baseline gap-4 mb-5">
//         <p class="font-serif text-3xl text-amber font-semibold">${formatPrice(p.price)}</p>
//         <span class="text-xs font-sans px-3 py-1 rounded-full ${inStock ? 'bg-sage/20 text-sage' : 'bg-rust/10 text-rust'}">
//           ${inStock ? `${p.stock_quantity} in stock` : 'Out of Stock'}
//         </span>
//       </div>

//       <!-- Divider -->
//       <div class="h-px bg-parchment my-5"></div>

//       <!-- Description -->
//       <p class="text-muted leading-relaxed text-sm mb-6">${p.description || 'No description available.'}</p>

//       <!-- Details -->
//       <div class="bg-parchment/50 rounded-xl p-4 mb-6 space-y-2">
//         <div class="flex justify-between text-sm">
//           <span class="text-muted font-sans">Condition</span>
//           <span class="text-brown font-semibold">Excellent</span>
//         </div>
//         <div class="flex justify-between text-sm">
//           <span class="text-muted font-sans">Era</span>
//           <span class="text-brown font-semibold">Authenticated Vintage</span>
//         </div>
//         <div class="flex justify-between text-sm">
//           <span class="text-muted font-sans">SKU</span>
//           <span class="text-brown font-mono text-xs">VTQ-${String(p.id).padStart(5,'0')}</span>
//         </div>
//       </div>

//       <!-- Quantity + Add to Cart -->
//       ${inStock ? `
//       <div class="flex items-stretch gap-3 mb-4">
//         <!-- Qty -->
//         <div class="flex items-center border border-parchment rounded-xl overflow-hidden bg-white">
//           <button onclick="adjustQty(-1)" class="px-4 py-3 text-brown hover:bg-parchment transition-colors font-semibold text-lg leading-none">−</button>
//           <span id="qty-display" class="px-5 text-sm font-sans font-semibold text-brown select-none">1</span>
//           <button onclick="adjustQty(1)" class="px-4 py-3 text-brown hover:bg-parchment transition-colors font-semibold text-lg leading-none">+</button>
//         </div>
//         <!-- Add -->
//         <button onclick="addToCart()"
//           class="flex-1 bg-brown hover:bg-amber text-cream font-sans font-semibold text-sm py-3 px-6 rounded-xl transition-all duration-300 hover:shadow-lg hover:-translate-y-0.5">
//           Add to Cart — ${formatPrice(p.price)}
//         </button>
//       </div>

//       <!-- Buy Now -->
//       <a href="cart.html" onclick="cart.add(${JSON.stringify(p).replace(/"/g, '&quot;')}, selectedQty)"
//         class="w-full block text-center border-2 border-brown text-brown hover:bg-brown hover:text-cream font-sans font-semibold text-sm py-3 rounded-xl transition-all duration-300">
//         Buy Now
//       </a>
//       ` : `
//       <div class="bg-parchment/60 text-muted text-center py-4 rounded-xl font-sans text-sm">
//         This item is currently sold out. <a href="products.html" class="text-amber hover:underline">Browse similar pieces</a>.
//       </div>
//       `}

//       <!-- Wishlist & Share -->
//       <div class="flex items-center justify-between mt-5 pt-5 border-t border-parchment">
//         <button class="flex items-center gap-2 text-xs font-sans text-muted hover:text-rust transition-colors">
//           <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8"><path stroke-linecap="round" stroke-linejoin="round" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"/></svg>
//           Save to Wishlist
//         </button>
//         <button onclick="shareProduct()" class="flex items-center gap-2 text-xs font-sans text-muted hover:text-amber transition-colors">
//           <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8"><path stroke-linecap="round" stroke-linejoin="round" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z"/></svg>
//           Share
//         </button>
//       </div>
//     </div>
//   `;
// }

// function adjustQty(delta) {
//   if (!currentProduct) return;
//   selectedQty = Math.max(1, Math.min(selectedQty + delta, currentProduct.stock_quantity));
//   document.getElementById('qty-display').textContent = selectedQty;
// }

// function addToCart() {
//   if (!currentProduct) return;
//   cart.add(currentProduct, selectedQty);
// }

// async function renderRelated(p) {
//   const grid = document.getElementById('related-grid');
//   if (!grid) return;
//   try {
//     let products = await productsAPI.getAll();
//     products = products.filter(x => x.id !== p.id && x.category === p.category).slice(0, 4);
//     if (products.length < 2) products = MOCK.filter(x => x.id !== p.id).slice(0, 4);
//     grid.innerHTML = '';
//     products.forEach((item, i) => {
//       const card = buildProductCard(item, i);
//       card.querySelectorAll('a[href]').forEach(el => {
//         el.href = el.getAttribute('href');
//       });
//       grid.appendChild(card);
//     });
//   } catch {
//     grid.innerHTML = '';
//     MOCK.filter(x => x.id !== p.id).slice(0, 4).forEach((item, i) => {
//       grid.appendChild(buildProductCard(item, i));
//     });
//   }
// }

// function shareProduct() {
//   if (navigator.share) {
//     navigator.share({ title: currentProduct?.name, url: window.location.href });
//   } else {
//     navigator.clipboard?.writeText(window.location.href);
//     showToast('Link copied to clipboard!');
//   }
// }

// document.addEventListener('DOMContentLoaded', initProductDetail);
