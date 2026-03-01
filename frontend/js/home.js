/* ── HOME.JS — Landing page featured products ────────────────────────────── */
async function loadAllProducts() {
  const container = document.getElementById('featured-products'); // or 'products-container'
  if (!container) return;

  try {
    // Fetch all products from API
    const products = await productsAPI.getAll(); // no params => get everything

    container.innerHTML = ''; // clear container

    if (!products || products.length === 0) {
      container.innerHTML = '<p class="col-span-4 text-center text-muted py-12">No products available.</p>';
      return;
    }

    // Build product cards
    products.forEach((p, i) => {
      container.appendChild(buildProductCard(p, i));
    });

  } catch (e) {
    console.error("Failed to load products:", e);
    container.innerHTML = '<p class="col-span-4 text-center text-muted py-12">Could not load products.</p>';
  }
}

// Run on DOM ready
document.addEventListener('DOMContentLoaded', loadAllProducts);