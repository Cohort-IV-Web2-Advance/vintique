/* ── ADMIN.JS — Admin panel: products, orders, users, inventory ───────────── */

const STATUS_COLORS = {
  pending: "bg-amber/10 text-amber",
  processing: "bg-blue-50 text-blue-600",
  shipped: "bg-sage/10 text-sage",
  delivered: "bg-green-50 text-green-600",
  cancelled: "bg-rust/10 text-rust",
};

let pendingDeleteId = null;
let activeTab = "overview";

// ── TAB NAVIGATION ────────────────────────────────────────────────────────────
function showTab(tab) {
  // Close sidebar on mobile after nav tap
  if (window.innerWidth < 1024) closeSidebar();
  activeTab = tab;

  document
    .querySelectorAll('[id^="tab-"]')
    .forEach((el) => el.classList.add("hidden"));
  document.getElementById(`tab-${tab}`)?.classList.remove("hidden");
  document.getElementById(`tab-${tab}`)?.classList.add("fade-in");

  document.querySelectorAll(".admin-nav").forEach((btn) => {
    btn.className =
      "admin-nav flex items-center gap-3 w-full text-left px-4 py-2.5 rounded-lg text-sm font-sans transition-colors text-cream/60 hover:bg-cream/5 hover:text-cream";
  });

  document.querySelectorAll(".admin-nav").forEach((btn) => {
    if (btn.getAttribute("onclick")?.includes(`'${tab}'`)) {
      btn.className =
        "admin-nav flex items-center gap-3 w-full text-left px-4 py-2.5 rounded-lg text-sm font-sans transition-colors bg-cream/10 text-cream";
    }
  });

  const titles = {
    overview: "Overview",
    products: "Products",
    orders: "Orders",
    users: "Users",
    "add-product": "Add Product",
  };
  document.getElementById("page-title").textContent = titles[tab] || tab;

  if (tab === "overview") loadOverview();
  if (tab === "products") loadProducts();
  if (tab === "orders") loadOrders();
  if (tab === "users") loadUsers();
}

// ── DATA LOADERS ──────────────────────────────────────────────────────────────

async function loadOverview() {
  const set = (id, val) => {
    const el = document.getElementById(id);
    if (el) el.textContent = val;
  };

  set("stat-revenue", "…");
  set("stat-orders", "…");
  set("stat-products", "…");
  set("stat-users", "…");

  let orders, products, users;

  try {
    orders = await adminAPI.getOrders();
  } catch {
    orders = MOCK_ADMIN_ORDERS;
  }

  try {
    products = await adminAPI.getProducts();
  } catch {
    products = MOCK_ADMIN_PRODUCTS;
  }

  try {
    users = await adminAPI.getUsers();
  } catch {
    users = MOCK_ADMIN_USERS;
  }

  const totalRevenue = orders
    .filter((o) => o.order_status !== "cancelled")
    .reduce((sum, o) => sum + parseFloat(o.amount || 0), 0);

  const totalOrders = orders.length;
  const totalProducts = products.length;
  const lowStockCount = products.filter(
    (p) => p.stock_quantity > 0 && p.stock_quantity <= 5,
  ).length;
  const outOfStockCount = products.filter((p) => p.stock_quantity === 0).length;
  const totalUsers = users.length;

  const oneWeekAgo = new Date();
  oneWeekAgo.setDate(oneWeekAgo.getDate() - 7);
  const ordersThisWeek = orders.filter(
    (o) => new Date(o.created_at) >= oneWeekAgo,
  ).length;
  const usersThisWeek = users.filter(
    (u) => new Date(u.created_at) >= oneWeekAgo,
  ).length;

  set("stat-revenue", formatPrice(totalRevenue));
  set("stat-revenue-change", "↑ Revenue from non-cancelled orders");
  set("stat-orders", totalOrders.toLocaleString());
  set(
    "stat-orders-change",
    ordersThisWeek > 0
      ? `↑ ${ordersThisWeek} this week`
      : "No new orders this week",
  );
  set("stat-products", totalProducts.toLocaleString());
  set(
    "stat-low-stock",
    outOfStockCount > 0
      ? `${lowStockCount} low stock · ${outOfStockCount} out of stock`
      : lowStockCount > 0
        ? `${lowStockCount} low stock`
        : "All products in stock",
  );
  set("stat-users", totalUsers.toLocaleString());
  set(
    "stat-users-change",
    usersThisWeek > 0
      ? `↑ ${usersThisWeek} this week`
      : "No new users this week",
  );

  // Build product lookup for recent orders table
  const productMap = Object.fromEntries(products.map((p) => [p.id, p]));

  const tbody = document.getElementById("dashboard-orders");
  if (!tbody) return;

  if (orders.length === 0) {
    tbody.innerHTML = `<tr><td colspan="4" class="py-4 text-center text-muted text-xs">No orders yet.</td></tr>`;
    return;
  }

  tbody.innerHTML = orders
    .slice(0, 6)
    .map((o) => {
      const productName =
        productMap[o.product_id]?.name || `Product #${o.product_id}`;
      return `
    <tr class="hover:bg-parchment/20 transition-colors">
      <td class="py-3 font-mono text-xs text-muted">#${o.id}</td>
      <td class="py-3 text-sm text-brown">${productName}</td>
      <td class="py-3 text-amber font-semibold">${formatPrice(o.amount)}</td>
      <td class="py-3">
        <span class="px-2.5 py-1 rounded-full text-xs font-semibold capitalize ${STATUS_COLORS[o.order_status] || STATUS_COLORS.pending}">
          ${o.order_status}
        </span>
      </td>
    </tr>
  `;
    })
    .join("");
}

async function loadProducts() {
  let products;
  try {
    products = await adminAPI.getProducts();
  } catch {
    products = MOCK_ADMIN_PRODUCTS;
  }

  const tbody = document.getElementById("admin-products");
  if (!tbody) return;
  tbody.innerHTML = products
    .map(
      (p) => `
    <tr class="hover:bg-parchment/20 transition-colors">
      <td class="px-5 py-3">
        <div class="flex items-center gap-3">
          <img src="${p.image_url}" class="w-10 h-10 rounded-lg object-cover shrink-0"
            onerror="this.src='https://images.unsplash.com/photo-1558171813-a08ccd5e6b95?w=80&q=60'" />
          <span class="font-sans text-sm font-semibold text-brown">${p.name}</span>
        </div>
      </td>
      <td class="px-5 py-3 text-amber font-semibold">${formatPrice(p.price)}</td>
      <td class="px-5 py-3">
        <span class="text-sm ${p.stock_quantity === 0 ? "text-rust font-semibold" : p.stock_quantity <= 3 ? "text-amber" : "text-sage"}">
          ${p.stock_quantity === 0 ? "Out of Stock" : p.stock_quantity <= 3 ? `Only ${p.stock_quantity}` : p.stock_quantity}
        </span>
      </td>
      <td class="px-5 py-3">
        <div class="flex items-center gap-2">
          <button onclick="editProduct(${p.id})" class="text-xs px-3 py-1.5 border border-parchment text-muted hover:border-amber hover:text-amber rounded-lg transition-colors">Edit</button>
          <button onclick="promptDelete(${p.id})" class="text-xs px-3 py-1.5 border border-rust/20 text-rust hover:bg-rust hover:text-cream rounded-lg transition-colors">Delete</button>
        </div>
      </td>
    </tr>
  `,
    )
    .join("");
}

async function loadOrders() {
  let orders, users, products;

  try {
    orders = await adminAPI.getOrders();
  } catch {
    orders = MOCK_ADMIN_ORDERS;
  }

  try {
    users = await adminAPI.getUsers();
  } catch {
    users = MOCK_ADMIN_USERS;
  }

  try {
    products = await adminAPI.getProducts();
  } catch {
    products = MOCK_ADMIN_PRODUCTS;
  }

  // Build lookup maps by ID for fast cross-referencing
  const userMap = Object.fromEntries(users.map((u) => [u.id, u]));
  const productMap = Object.fromEntries(products.map((p) => [p.id, p]));

  const tbody = document.getElementById("admin-orders");
  if (!tbody) return;

  tbody.innerHTML = orders
    .map((o) => {
      const username =
        userMap[o.user_id]?.username ||
        userMap[o.user_id]?.email ||
        `User #${o.user_id}`;
      const productName =
        productMap[o.product_id]?.name || `Product #${o.product_id}`;

      return `
    <tr class="hover:bg-parchment/20 transition-colors">
      <td class="px-5 py-3 font-mono text-xs text-muted">#${o.id}</td>
      <td class="px-5 py-3 text-sm text-brown">${username}</td>
      <td class="px-5 py-3 text-sm text-brown">${productName}</td>
      <td class="px-5 py-3 text-amber font-semibold">${formatPrice(o.amount)}</td>
      <td class="px-5 py-3">
        <select onchange="updateOrderStatus(${o.id}, this.value)"
          class="text-xs border border-parchment rounded-lg px-2 py-1 focus:outline-none focus:border-amber transition-colors capitalize">
          ${["pending", "processing", "shipped", "delivered", "cancelled"]
            .map(
              (s) => `
            <option value="${s}" ${o.order_status === s ? "selected" : ""}>${s}</option>
          `,
            )
            .join("")}
        </select>
      </td>
      <td class="px-5 py-3 text-xs text-muted">${formatDate(o.created_at)}</td>
    </tr>
  `;
    })
    .join("");
}

async function loadUsers() {
  let users;
  try {
    users = await adminAPI.getUsers();
  } catch {
    users = MOCK_ADMIN_USERS;
  }

  const tbody = document.getElementById("admin-users");
  if (!tbody) return;
  tbody.innerHTML = users
    .map(
      (u) => `
    <tr class="hover:bg-parchment/20 transition-colors">
      <td class="px-5 py-3">
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 rounded-full bg-amber/20 flex items-center justify-center text-amber font-serif font-bold text-sm">
            ${(u.username || u.email || "?")[0].toUpperCase()}
          </div>
          <span class="font-sans text-sm font-semibold text-brown">${u.username}</span>
        </div>
      </td>
      <td class="px-5 py-3 text-sm text-muted">${u.email}</td>
      <td class="px-5 py-3">
        <span class="px-2.5 py-1 rounded-full text-xs font-semibold ${u.is_admin ? "bg-amber/10 text-amber" : "bg-parchment text-muted"}">
          ${u.is_admin ? "Admin" : "Customer"}
        </span>
      </td>
      <td class="px-5 py-3 text-xs text-muted">${formatDate(u.created_at)}</td>
      <td class="px-5 py-3">
        ${
          !u.is_admin
            ? `
          <button onclick="handleMakeAdmin(${u.id})"
            class="text-xs bg-amber/10 hover:bg-amber text-amber hover:text-cream font-semibold px-3 py-1.5 rounded-lg transition-colors">
            Make Admin
          </button>
        `
            : "—"
        }
      </td>
    </tr>
  `,
    )
    .join("");
}

async function handleMakeAdmin(userId) {
  try {
    await adminAPI.makeUserAdmin(userId);
    showToast("User promoted to admin!");
    loadUsers();
  } catch (err) {
    showToast(err.message, "error");
  }
}

// ── PRODUCT MANAGEMENT ────────────────────────────────────────────────────────
function previewImage(input) {
  const file = input.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = (e) => {
    const preview = document.getElementById("image-preview");
    const placeholder = document.getElementById("upload-placeholder");
    preview.src = e.target.result;
    preview.classList.remove("hidden");
    placeholder.classList.add("hidden");
  };
  reader.readAsDataURL(file);
}

function handleDrop(event) {
  event.preventDefault();
  event.currentTarget.classList.remove("border-amber");
  const file = event.dataTransfer.files[0];
  if (!file) return;
  const input = document.getElementById("image-input");
  const dt = new DataTransfer();
  dt.items.add(file);
  input.files = dt.files;
  previewImage(input);
}

async function submitProduct(e) {
  e.preventDefault();
  const btn = document.getElementById("submit-btn");
  const errEl = document.getElementById("product-error");
  const succEl = document.getElementById("product-success");
  const form = e.target;

  btn.textContent = "Uploading…";
  btn.disabled = true;
  errEl.classList.add("hidden");
  succEl.classList.add("hidden");

  const formData = new FormData(form);

  try {
    await adminAPI.createProduct(formData);
    succEl.textContent = "✓ Product published successfully!";
    succEl.classList.remove("hidden");
    form.reset();
    document.getElementById("image-preview").classList.add("hidden");
    document.getElementById("upload-placeholder").classList.remove("hidden");
  } catch (err) {
    errEl.textContent = `✗ Failed to publish: ${err.message}`;
    errEl.classList.remove("hidden");
  } finally {
    btn.textContent = "Upload & Publish Product";
    btn.disabled = false;
  }
}

function editProduct(id) {
  showTab("add-product");
  showToast(
    `Edit form for product #${id} — wire to PUT /inventory/product/${id}`,
  );
}

function promptDelete(id) {
  pendingDeleteId = id;
  const modal = document.getElementById("delete-modal");
  modal.classList.remove("opacity-0", "pointer-events-none");
}

function cancelDelete() {
  pendingDeleteId = null;
  const modal = document.getElementById("delete-modal");
  modal.classList.add("opacity-0", "pointer-events-none");
}

async function confirmDelete() {
  if (!pendingDeleteId) return;
  try {
    await adminAPI.deleteProduct(pendingDeleteId);
    showToast("Product deleted successfully.");
    loadProducts();
  } catch (err) {
    console.error("Delete failed — server response:", err);
    showToast(`Delete failed: ${err.message}`);
  } finally {
    cancelDelete();
  }
}

function updateOrderStatus(orderId, status) {
  showToast(`Order #${orderId} marked as "${status}"`);
  // Wire: PATCH /admin/orders/{orderId}/status
}

// ── INIT ──────────────────────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  if (!isLoggedIn()) {
    window.location.href = "./login.html";
    return;
  }
  // if (!isAdmin()) { window.location.href = '../index.html'; return; }

  const user = getUser();
  if (user)
    document.getElementById("admin-name").textContent =
      `@${user.username || user.email}`;

  showTab("overview");
});

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("product-form");
  if (!form) return;

  form.querySelector('[name="name"]').addEventListener("input", (e) => {
    document.getElementById("preview-name").textContent =
      e.target.value || "Product Name";
  });

  form.querySelector('[name="description"]').addEventListener("input", (e) => {
    document.getElementById("preview-description").textContent =
      e.target.value || "Description will appear here…";
  });

  form.querySelector('[name="price"]').addEventListener("input", (e) => {
    const val = parseFloat(e.target.value) || 0;
    document.getElementById("preview-price").textContent = formatPrice(val);
  });

  form
    .querySelector('[name="stock_quantity"]')
    .addEventListener("input", (e) => {
      const qty = parseInt(e.target.value) || 0;
      const el = document.getElementById("preview-stock");
      el.textContent =
        qty === 0 ? "Out of stock" : qty <= 3 ? `Only ${qty} left` : "In stock";
      el.className = `text-xs ${qty === 0 ? "text-rust" : qty <= 3 ? "text-amber" : "text-sage"}`;
    });
});

function updatePreviewImage(src) {
  const wrap = document.getElementById("preview-img-wrap");
  wrap.innerHTML = `<img src="${src}" class="w-full h-full object-cover" />`;
}
function previewImage(input) {
  const file = input.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = (e) => {
    const preview = document.getElementById("image-preview");
    const placeholder = document.getElementById("upload-placeholder");
    preview.src = e.target.result;
    preview.classList.remove("hidden");
    placeholder.classList.add("hidden");
    updatePreviewImage(e.target.result); // ← add this line
  };
  reader.readAsDataURL(file);
}
