// /* ── HOME.JS — Landing page featured products ────────────────────────────── */

// // Mock data (replace with live API calls in production)
// const MOCK_PRODUCTS = [
//   { id: 1, name: "Victorian Cameo Brooch", price: 89.99, stock_quantity: 5, description: "Hand-carved 19th-century cameo on gold-filled filigree. Circa 1880s.", image_url: "https://images.unsplash.com/photo-1602751584552-8ba73aad10e1?w=600&q=80", category: "Jewelry" },
//   { id: 2, name: "Art Deco Vanity Mirror", price: 145.00, stock_quantity: 2, description: "Beveled mirror with original chrome stand. Geometric etched border, 1930s.", image_url: "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=600&q=80", category: "Home Décor" },
//   { id: 3, name: "1950s Leather Satchel", price: 210.00, stock_quantity: 3, description: "Hand-stitched cognac leather with post-war patina. Original brass hardware.", image_url: "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=600&q=80", category: "Bags" },
//   { id: 4, name: "Edwardian Tea Service", price: 320.00, stock_quantity: 1, description: "6-piece bone china with hand-painted roses and gold gilding, circa 1905.", image_url: "https://images.unsplash.com/photo-1563729784474-d77dbb933a9e?w=600&q=80", category: "Kitchenware" },
// ];

// async function loadFeaturedProducts() {
//   const container = document.getElementById('featured-products');
//   if (!container) return;

//   try {
//     // Try live API first
//     let products;
//     try {
//       products = await productsAPI.getAll({ limit: 4 });
//       products = products?.slice(0, 4);
//     } catch {
//       products = MOCK_PRODUCTS;
//     }

//     container.innerHTML = '';
//     products.forEach((p, i) => {
//       container.appendChild(buildProductCard(p, i));
//     });
//   } catch (e) {
//     container.innerHTML = '<p class="col-span-4 text-center text-muted py-12">Could not load products.</p>';
//   }
// }

// document.addEventListener('DOMContentLoaded', loadFeaturedProducts);
