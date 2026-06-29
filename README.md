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
