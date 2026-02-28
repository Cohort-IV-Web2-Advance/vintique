# Vintique Frontend

A production-quality vintage e-commerce frontend built with **HTML + Tailwind CSS + Vanilla JS**.

## Project Structure

```
vintique/
├── index.html              ← Landing page
├── products.html       ← Shop listing
├── product.html        ← Product detail
├── cart.html           ← Cart + Checkout (3-step)
├── login.html          ← Sign In
├── register.html       ← Register
├── orders.html         ← Order history (protected)
└── admin.html          ← Admin dashboard (admin only)
├── src/
│   └── style.css           ← Custom animations, utilities
├── js/
│   ├── app.js              ← Core: API layer, cart, auth, toast, helpers
│   ├── home.js             ← Featured products loader
│   ├── products.js         ← Shop listing: filter, sort, search
│   ├── product.js          ← Product detail page
│   ├── cart.js             ← Cart display + 3-step checkout
│   └── admin.js            ← Admin panel: products, orders, users
```

## Pages

| Page | Route | Auth |
|------|-------|------|
| Landing | `index.html` | Public |
| Shop | `pages/products.html` | Public |
| Product Detail | `pages/product.html?id=X` | Public |
| Cart & Checkout | `pages/cart.html` | Public (checkout requires auth) |
| Login | `pages/login.html` | Guest only |
| Register | `pages/register.html` | Guest only |
| My Orders | `pages/orders.html` | Protected |
| Admin | `pages/admin.html` | Admin only |

## API Connection

Edit `js/app.js` and set your backend URL:

```js
const API_BASE = 'http://localhost:8000';  // Your Vintique FastAPI server
```

The frontend auto-calls your API endpoints:
- `POST /auth/login` → JWT login
- `POST /auth/register` → Registration
- `GET /auth/me` → Current user
- `GET /products` → Product list
- `GET /products/:id` → Product detail
- `POST /cart/add` → Add to cart
- `PATCH /cart/update-qty` → Update quantity
- `POST /checkout` → Place order
- `GET /orders/history` → Order history
- `GET /admin/orders` → Admin: all orders
- `GET /admin/users` → Admin: all users
- `GET /admin/products` → Admin: all products
- `POST /inventory/product` → Create product (multipart with image)
- `PUT /inventory/product/:id` → Update product
- `DELETE /inventory/product/:id` → Delete product

## Features

- **Vintage & Warm** design system (cream, parchment, amber, brown)
- Playfair Display serif + Lato sans fonts
- Sticky navbar with cart badge + auth state
- Product filtering by category, price range, search, stock
- 3-step checkout flow (Cart → Shipping → Confirm → Success)
- Admin dashboard with stats, product CRUD, order management
- Cloudinary image upload in admin
- Cart persisted in localStorage + synced to API
- JWT token in localStorage, protected routes redirect to login
- Skeleton loaders, toast notifications, fade-in animations
- Fully responsive (mobile-first)

## Customization

Colors are defined in each `<script>tailwind.config = {...}</script>` block. Update `app.js` `API_BASE` constant for deployment.
