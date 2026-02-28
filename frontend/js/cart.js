// /* ── CART.JS — Cart display, shipping, confirm & order placement ─────────── */

// let shippingData = {};

// // ── RENDER CART ───────────────────────────────────────────────────────────────
// function renderCart() {
//   const items = cart.items;
//   const listEl = document.getElementById('cart-items-list');
//   const emptyEl = document.getElementById('empty-cart');
//   const contentEl = document.getElementById('cart-content');

//   if (!listEl) return;

//   if (items.length === 0) {
//     emptyEl?.classList.remove('hidden');
//     contentEl?.classList.add('hidden');
//     return;
//   }

//   emptyEl?.classList.add('hidden');
//   contentEl?.classList.remove('hidden');

//   listEl.innerHTML = items.map(item => `
//     <div class="bg-white rounded-2xl p-5 flex gap-4 fade-in product-card" id="cart-item-${item.id}">
//       <a href="product.html?id=${item.id}" class="flex-shrink-0">
//         <img src="${item.image_url || ''}" alt="${item.name}"
//           class="w-24 h-24 object-cover rounded-xl"
//           onerror="this.src='https://images.unsplash.com/photo-1558171813-a08ccd5e6b95?w=200&q=60'" />
//       </a>
//       <div class="flex-1 min-w-0">
//         <div class="flex items-start justify-between gap-2">
//           <div>
//             <p class="text-[10px] font-sans tracking-widest uppercase text-muted mb-0.5">${item.category || 'Vintage'}</p>
//             <h3 class="font-serif text-base text-brown font-semibold leading-tight">${item.name}</h3>
//           </div>
//           <button onclick="removeItem(${item.id})" class="text-muted hover:text-rust transition-colors flex-shrink-0 p-1">
//             <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
//               <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
//             </svg>
//           </button>
//         </div>

//         <div class="flex items-center justify-between mt-3">
//           <!-- Qty Control -->
//           <div class="flex items-center border border-parchment rounded-lg overflow-hidden">
//             <button onclick="changeQty(${item.id}, ${item.qty - 1})"
//               class="px-3 py-1.5 text-brown hover:bg-parchment transition-colors text-base leading-none">−</button>
//             <span class="px-3 text-sm font-semibold text-brown">${item.qty}</span>
//             <button onclick="changeQty(${item.id}, ${item.qty + 1})"
//               class="px-3 py-1.5 text-brown hover:bg-parchment transition-colors text-base leading-none">+</button>
//           </div>
//           <p class="font-serif text-lg text-amber font-semibold">${formatPrice(item.price * item.qty)}</p>
//         </div>
//       </div>
//     </div>
//   `).join('');

//   updateSummary();
// }

// function updateSummary() {
//   const subtotal = cart.total;
//   const tax = subtotal * 0.08;
//   const total = subtotal + tax;

//   const fmt = (n) => formatPrice(n);
//   document.getElementById('summary-subtotal').textContent = fmt(subtotal);
//   document.getElementById('summary-tax').textContent      = fmt(tax);
//   document.getElementById('summary-total').textContent    = fmt(total);
// }

// function removeItem(id) {
//   cart.remove(id);
//   renderCart();
// }

// function changeQty(id, newQty) {
//   if (newQty < 1) { removeItem(id); return; }
//   cart.updateQty(id, newQty);
//   renderCart();
// }

// function applyPromo() {
//   const code = document.getElementById('promo-input')?.value.trim().toUpperCase();
//   if (code === 'VINTIQUE10') {
//     showToast('10% discount applied!');
//   } else {
//     showToast('Invalid promo code.', 'error');
//   }
// }

// // ── STEP NAVIGATION ───────────────────────────────────────────────────────────
// function goToShipping() {
//   if (cart.items.length === 0) { showToast('Your cart is empty!', 'error'); return; }
//   if (!isLoggedIn()) {
//     sessionStorage.setItem('vintique_redirect', 'cart.html');
//     window.location.href = 'login.html';
//     return;
//   }
//   showStep('shipping');
// }

// function backToCart() { showStep('cart'); }

// function goToConfirm() {
//   const form = document.getElementById('shipping-form');
//   if (!form) return;
//   if (!form.reportValidity()) return;

//   const data = new FormData(form);
//   shippingData = Object.fromEntries(data.entries());
//   renderConfirmPage();
//   showStep('confirm');
// }

// function backToShipping() { showStep('shipping'); }

// function renderConfirmPage() {
//   // Items
//   const itemsEl = document.getElementById('confirm-items');
//   if (itemsEl) {
//     itemsEl.innerHTML = cart.items.map(i => `
//       <div class="flex items-center gap-3">
//         <img src="${i.image_url || ''}" class="w-12 h-12 object-cover rounded-lg" onerror="this.src='https://images.unsplash.com/photo-1558171813-a08ccd5e6b95?w=100&q=60'" />
//         <div class="flex-1">
//           <p class="text-sm font-sans font-semibold text-brown">${i.name}</p>
//           <p class="text-xs text-muted">Qty: ${i.qty}</p>
//         </div>
//         <p class="font-sans text-sm font-semibold text-brown">${formatPrice(i.price * i.qty)}</p>
//       </div>
//     `).join('');
//   }

//   // Total
//   const subtotal = cart.total;
//   const total = subtotal * 1.08 + (shippingData.shipping_method === 'express' ? 12.99 : 0);
//   document.getElementById('confirm-total').textContent = formatPrice(total);

//   // Address
//   const addrEl = document.getElementById('confirm-address');
//   if (addrEl && shippingData) {
//     addrEl.innerHTML = `
//       <p>${shippingData.first_name} ${shippingData.last_name}</p>
//       <p>${shippingData.address}</p>
//       <p>${shippingData.city}, ${shippingData.postcode}</p>
//       <p>${shippingData.country}</p>
//       <p class="mt-1">${shippingData.email}</p>
//     `;
//   }
// }

// async function placeOrder() {
//   const btn = document.getElementById('place-order-btn');
//   btn.textContent = 'Placing order…';
//   btn.disabled = true;

//   try {
//     const payload = {
//       items: cart.items.map(i => ({ product_id: i.id, quantity: i.qty, unit_price: i.price })),
//       shipping_address: `${shippingData.address}, ${shippingData.city}, ${shippingData.country}`,
//     };

//     await ordersAPI.checkout(payload);
//     cart.clear();
//     showStep('success');
//   } catch (e) {
//     // Demo: show success anyway for non-connected environments
//     cart.clear();
//     showStep('success');
//   }
// }

// function showStep(step) {
//   ['cart', 'shipping', 'confirm', 'success'].forEach(s => {
//     document.getElementById(`step-${s}`)?.classList.add('hidden');
//   });
//   document.getElementById(`step-${step}`)?.classList.remove('hidden');
//   document.getElementById(`step-${step}`)?.classList.add('fade-in');
//   window.scrollTo({ top: 0, behavior: 'smooth' });

//   // Update step indicators
//   const steps = ['cart', 'shipping', 'confirm'];
//   const activeIdx = steps.indexOf(step);
//   steps.forEach((s, i) => {
//     const circle = document.getElementById(`step${i+1}-circle`);
//     const label  = document.getElementById(`step${i+1}-label`);
//     if (!circle) return;
//     const active = i <= activeIdx;
//     circle.className = `w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${active ? 'bg-amber text-cream' : 'bg-parchment text-muted border border-muted/30'}`;
//     if (label) label.className = `text-sm font-sans ${active ? 'text-brown font-semibold' : 'text-muted'}`;
//   });
// }

// document.addEventListener('DOMContentLoaded', () => {
//   renderCart();
// });
