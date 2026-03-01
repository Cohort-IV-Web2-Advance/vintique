/* ── HOME.JS — Landing page featured products ────────────────────────────── */

async function loadFeaturedProducts() {
  const container = document.getElementById('featured-products');
  if (!container) return;

  try {
    // Try live API first
    let products;
    try {
      products = await productsAPI.getAll({ limit: 4 });
      products = products?.slice(0, 4);
    } catch {
      products = MOCK_PRODUCTS;
    }

    container.innerHTML = '';
    products.forEach((p, i) => {
      container.appendChild(buildProductCard(p, i));
    });
  } catch (e) {
    container.innerHTML = '<p class="col-span-4 text-center text-muted py-12">Could not load products.</p>';
  }
}

document.addEventListener('DOMContentLoaded', loadFeaturedProducts);
