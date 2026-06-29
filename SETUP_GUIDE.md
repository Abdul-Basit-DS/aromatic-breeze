# The Aromatic Breeze – Complete Setup Guide

## Project Structure (All 7 ZIPs Combined)

```
aromatic_breeze/
├── config/
│   ├── settings/
│   │   ├── base.py          # Shared settings
│   │   ├── development.py   # Dev (DEBUG=True, SQLite)
│   │   └── production.py    # Prod (PostgreSQL, Redis, HTTPS)
│   ├── urls.py              # Main URL routing
│   ├── wsgi.py
│   └── celery.py
├── apps/
│   ├── accounts/            # Users, Profiles, Addresses, Wishlist, ActivityLog
│   ├── shop/                # Products, Categories, Cart, Banners, Inventory
│   ├── orders/              # Orders, Checkout, Shipping, Returns, Invoice
│   ├── blog/                # BlogPost, Category, Tag, Comment, FAQ
│   ├── pages/               # SiteSettings, About, Contact, Policy pages
│   ├── reviews/             # Product Reviews
│   ├── newsletter/          # Email subscribers
│   ├── coupons/             # Discount coupons
│   └── contact/             # (stub – merged into pages)
├── templates/
│   ├── base.html            # Main layout (header, footer, nav)
│   ├── account/             # Login, Signup, Password Reset (allauth)
│   ├── shop/                # Home, Shop listing, Product detail, Cart
│   ├── orders/              # Checkout, Order success, Tracking, Invoice PDF
│   ├── accounts/            # Dashboard, My Orders, Profile, Wishlist
│   ├── blog/                # Blog listing, Post detail
│   ├── pages/               # About, Contact, Policy pages
│   └── partials/            # Reusable product card
├── static/
│   ├── css/main.css         # Complete luxury CSS
│   └── js/main.js           # All JavaScript (cart, search, wishlist)
├── fixtures/
│   └── initial_data.json    # Sample data (settings, shipping, coupons)
├── deployment/
│   ├── gunicorn.conf.py
│   ├── nginx.conf
│   └── aromatic_breeze.service
├── manage.py
├── requirements.txt
└── .env.example
```

---

## STEP-BY-STEP SETUP

### Step 1 – Extract All ZIPs

Extract all 7 ZIP files into the **same folder** in this order:
1. ZIP 1 → Foundation + Accounts
2. ZIP 2 → Shop App
3. ZIP 3 → Orders + Coupons
4. ZIP 4 → Blog + Pages + Newsletter
5. ZIP 5 → Core Templates + CSS/JS
6. ZIP 6 → Remaining Templates
7. ZIP 7 → Final (this file)

Each ZIP extracts into `aromatic_breeze/` – files will merge automatically.

---

### Step 2 – Create Virtual Environment

```bash
cd aromatic_breeze
python -m venv venv

# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate
```

---

### Step 3 – Install Dependencies

```bash
pip install -r requirements.txt
```

If you face issues with `psycopg2-binary` on Windows, use SQLite (default) for development.

---

### Step 4 – Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and set at minimum:
```
SECRET_KEY=your-random-secret-key-here
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
ADMIN_EMAIL=admin@example.com
DEFAULT_FROM_EMAIL=The Aromatic Breeze <noreply@example.com>
```

Generate a secret key:
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

### Step 5 – Run Migrations

```bash
python manage.py makemigrations accounts shop orders blog pages reviews newsletter coupons contact
python manage.py migrate
```

---

### Step 6 – Load Sample Data

```bash
python manage.py loaddata fixtures/initial_data.json
```

This loads:
- Site settings (name, contact info, announcement bar)
- 4 Trust Features
- 8 Fragrance Families (Fresh, Woody, Floral, Oud, Citrus etc.)
- 3 Shipping Zones (Lahore, Karachi, Rest of Pakistan)
- 2 Sample Coupons (WELCOME10, FREESHIP)
- 5 Blog Categories + 5 Blog Tags
- 4 FAQs for Contact page
- 4 Statistics for About page

---

### Step 7 – Create Superuser

```bash
python manage.py createsuperuser
```

Enter email, first name, and password when prompted.

---

### Step 8 – Collect Static Files

```bash
python manage.py collectstatic
```

---

### Step 9 – Run Development Server

```bash
python manage.py runserver
```

Open your browser:
- **Website:** http://127.0.0.1:8000
- **Admin Panel:** http://127.0.0.1:8000/control-panel/

---

## FIRST STEPS IN ADMIN PANEL

### 1. Upload Logo & Configure Site
Admin → Pages → Site Settings → Edit → Upload logo, set phone/WhatsApp/address

### 2. Add Hero Banners
Admin → Shop → Banners → Add Banner
- Type: Hero Slider
- Upload desktop image (1920×800 recommended)
- Set title, subtitle, button text

### 3. Create Product Categories
Admin → Shop → Categories → Add Category
Examples: Men, Women, Unisex, Gift Sets, Luxury Collection, New Arrivals

### 4. Add Products
Admin → Shop → Products → Add Product
- Upload up to 5 images
- Set inspired_by (e.g. "Dior Sauvage")
- Add variations (30ml, 50ml, 100ml) with individual prices
- Mark as Featured/New Arrival/Best Seller

### 5. Configure About Page
Admin → Pages → About Page → Edit

### 6. Add Blog Posts
Admin → Blog → Blog Posts → Add Post
- Upload featured image
- Write content with CKEditor (rich text)
- Mark one post as Featured for the large card

---

## ADMIN PANEL URL

The admin panel is at: `/control-panel/` (not `/admin/` for security)

---

## FEATURES CHECKLIST

| Feature | Status |
|---------|--------|
| Custom User with email login | ✅ |
| Role-based access (RBAC) | ✅ |
| Product catalog with variations | ✅ |
| Live search | ✅ |
| Shopping cart (guest + logged-in) | ✅ |
| Wishlist | ✅ |
| Quick View modal | ✅ |
| Checkout with COD/Bank/JazzCash | ✅ |
| Order management with status history | ✅ |
| Invoice PDF generation | ✅ |
| Order tracking (public + private) | ✅ |
| Coupon system | ✅ |
| City-wise shipping charges | ✅ |
| Return requests | ✅ |
| Product reviews with approval | ✅ |
| Blog with categories/tags/comments | ✅ |
| Reading progress bar | ✅ |
| Blog FAQ accordion | ✅ |
| Newsletter subscription | ✅ |
| Contact form with admin inbox | ✅ |
| About page (fully dynamic) | ✅ |
| Animated statistics counters | ✅ |
| Brand timeline | ✅ |
| Hero slider with countdown | ✅ |
| Site settings (singleton) | ✅ |
| Privacy/Terms/Shipping/Return policies | ✅ |
| Activity logs (audit trail) | ✅ |
| Inventory logs | ✅ |
| Email notifications | ✅ |
| CSV/Excel export | ✅ |
| Duplicate product | ✅ |
| Bulk status updates | ✅ |
| Responsive design (mobile/tablet/desktop) | ✅ |
| Lazy loading images | ✅ |
| SEO fields (meta, OG, Twitter Card) | ✅ |
| 404 & 500 error pages | ✅ |

---

## PRODUCTION DEPLOYMENT

### Environment Variables for Production
```
DEBUG=False
SECRET_KEY=your-production-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgres://user:password@localhost:5432/aromatic_breeze
REDIS_URL=redis://127.0.0.1:6379/0
CELERY_BROKER_URL=redis://127.0.0.1:6379/0
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### Deploy Commands
```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn --config deployment/gunicorn.conf.py config.wsgi:application
```

### Nginx + Systemd
```bash
# Copy nginx config
sudo cp deployment/nginx.conf /etc/nginx/sites-available/aromatic_breeze
sudo ln -s /etc/nginx/sites-available/aromatic_breeze /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# Install systemd service
sudo cp deployment/aromatic_breeze.service /etc/systemd/system/
sudo systemctl enable aromatic_breeze
sudo systemctl start aromatic_breeze
```

---

## TROUBLESHOOTING

**Q: `ModuleNotFoundError: No module named 'apps'`**
Run from the `aromatic_breeze/` directory that contains `manage.py`.

**Q: Migration errors**
Run `python manage.py makemigrations` first, then `migrate`.

**Q: Static files not loading**
Run `python manage.py collectstatic` and ensure `DEBUG=True` in development.

**Q: Images not uploading**
Make sure the `media/` folder exists and is writable.

**Q: Email not sending**
In development, use `EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend` — emails print to terminal.

---

## SUPPORT

Built for: The Aromatic Breeze Premium Perfume E-Commerce
Stack: Django 4.2 · Python 3.11+ · Bootstrap 5.3 · Swiper.js

Add products, configure settings, and your store is ready! 🎉
