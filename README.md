# The Aromatic Breeze – Django E-Commerce Platform

## 🚀 Setup Instructions

### Step 1 – Create Virtual Environment
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### Step 2 – Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3 – Configure Environment
```bash
cp .env.example .env
# Edit .env with your settings (SECRET_KEY, DB, EMAIL etc.)
```

### Step 4 – Run Migrations
```bash
python manage.py migrate
```

### Step 5 – Create Superuser
```bash
python manage.py createsuperuser
```

### Step 6 – Run Development Server
```bash
python manage.py runserver
```

Open http://127.0.0.1:8000 in your browser.
Admin panel: http://127.0.0.1:8000/control-panel/

---

## 📦 ZIP Delivery Plan

| ZIP | Contents |
|-----|----------|
| **ZIP 1 (this file)** | Project foundation + Accounts app (models, admin, views, urls, forms, signals) |
| **ZIP 2** | Shop app – Product, Category, Variation, Banner models + admin + views |
| **ZIP 3** | Orders app – Order, OrderItem, Cart, Checkout models + admin + views |
| **ZIP 4** | Blog app – Blog, Category, Tag, Comment, FAQ models + admin + views |
| **ZIP 5** | Pages app – Homepage, About, Contact, SiteSettings + context processors |
| **ZIP 6** | Reviews, Newsletter, Coupons apps + complete admin dashboard |
| **ZIP 7** | All HTML templates (base, home, shop, product detail, cart, checkout) |
| **ZIP 8** | All remaining templates (blog, accounts, contact, about, dashboard) |
| **ZIP 9** | Static files – CSS (luxury design), JavaScript (cart, wishlist, search) |
| **ZIP 10** | Final – Migrations, fixtures (sample data), deployment configs |

---

## 🗂️ Project Structure
```
aromatic_breeze/
├── config/
│   ├── settings/
│   │   ├── base.py         # Shared settings
│   │   ├── development.py  # Dev settings
│   │   └── production.py   # Prod settings
│   ├── urls.py
│   ├── wsgi.py
│   └── celery.py
├── apps/
│   ├── accounts/           # Users, Profiles, Addresses, Wishlist
│   ├── shop/               # Products, Categories, Cart (ZIP 2)
│   ├── orders/             # Orders, Checkout (ZIP 3)
│   ├── blog/               # Blog, Comments, FAQs (ZIP 4)
│   ├── pages/              # Static pages, Site Settings (ZIP 5)
│   ├── reviews/            # Product Reviews (ZIP 6)
│   ├── newsletter/         # Subscribers (ZIP 6)
│   └── coupons/            # Discount Coupons (ZIP 6)
├── templates/              # HTML templates (ZIP 7 & 8)
├── static/                 # CSS, JS, Images (ZIP 9)
├── media/                  # User uploads (auto-created)
├── manage.py
├── requirements.txt
└── .env.example
```
