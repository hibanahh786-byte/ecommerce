# Ecommerce Store - Mini E-Commerce Management System

A complete, modern, responsive full-stack Mini E-Commerce Web Application built with **Django**, **Django REST Framework (DRF)**, **Simple JWT**, **MySQL**, and a responsive **Bootstrap 5** frontend.

---

## Features

### Role-Based Access Control
* **Admin Role**:
  * Comprehensive dashboard overview (Total Products, Categories, Orders, Users, Completed Revenue in ₹).
  * Category CRUD with instant live search.
  * Product CRUD with image upload, preview, and real-time inventory management.
  * Order management: view customer information, unit price, quantity, and update status from `Placed` to `Completed`.
  * User roster: view all registered customers and order histories.
* **User (Customer) Role**:
  * User registration and JWT authentication.
  * Product catalog with dynamic category filtering and live search.
  * Product detail page with image preview and quantity selector bounded to real-time stock.
  * Instant checkout / order placement.
  * Order confirmation modal and personal order history (`My Orders`) with itemized receipts.
  * Profile management (update name, email, and password).

### Core Business Logic & Security
* **Server-Side Total Calculation**: Prices and totals are computed strictly on the backend using database rates—never trusting client payloads.
* **Atomic Stock Validation & Reduction**: Powered by Django's `transaction.atomic()` and `select_for_update()` row-level database locking to prevent overselling during simultaneous checkouts.
* **JWT Security**: Access tokens and refresh tokens with token blacklisting on logout.
* **Image Uploads**: Validated image file sizes and formats stored in Django `MEDIA_ROOT`.

---

## Project Structure

```
ecommerce_project/
│
├── backend/
│   ├── manage.py
│   ├── config/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   ├── accounts/          # User auth, JWT, profile & roles
│   ├── categories/        # Categories CRUD & search
│   ├── products/          # Products CRUD, stock & image upload
│   ├── orders/            # Order placement, atomic reduction & status
│   ├── media/             # Uploaded product images
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── index.html         # Store homepage with hero & featured items
│   ├── login.html         # JWT login with one-click demo credentials
│   ├── register.html      # Customer registration
│   ├── products.html      # Product catalog with live search & filters
│   ├── product-details.html # Product detail & stock purchase
│   ├── my-orders.html     # User order history
│   ├── profile.html       # Profile management
│   ├── admin/
│   │   ├── dashboard.html # Overview metrics & recent orders
│   │   ├── categories.html# Category management
│   │   ├── products.html  # Product catalog management
│   │   ├── orders.html    # Customer order processing
│   │   └── users.html     # Registered customer roster
│   ├── css/
│   │   ├── style.css      # Customer store styling
│   │   └── admin.css      # Admin sidebar dashboard layout
│   ├── js/
│   │   ├── api.js         # Fetch client, auth interceptor & toasts
│   │   ├── auth.js        # Session, JWT tokens & guards
│   │   └── admin.js       # Admin layout & sidebar
│   └── assets/
│
├── README.md
└── .gitignore
```

---

## Getting Started

### 1. Prerequisites
* **Python 3.10+** (Python 3.12 / 3.14 compatible)
* **MySQL Server** (e.g. MySQL 8.x, MariaDB, or XAMPP)
* **Git**

---

### 2. Setup Virtual Environment & Dependencies

```bash
# Navigate to the backend directory
cd ecommerce_project/backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# macOS / Linux:
source venv/bin/activate

# Install required dependencies
pip install -r requirements.txt
```

---

### 3. Configure Database & Environment Variables

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` and verify your MySQL connection details:
   ```ini
   SECRET_KEY=django-secure-ecommerce-project-secret-key-2026
   DEBUG=True
   DB_ENGINE=mysql
   DB_NAME=ecommerce_db
   DB_USER=root
   DB_PASSWORD=your_mysql_password
   DB_HOST=127.0.0.1
   DB_PORT=3306
   ```
> **Note**: If MySQL server is not detected on your host, the backend automatically logs a notice and seamlessly runs with SQLite for local development so you can run and test right away without manual database server configuration.

---

### 4. Run Migrations & Seed Demo Data

```bash
# Run database migrations
python manage.py migrate

# Seed initial admin, sample customer, categories, and products
python manage.py seed_data
```

This sets up two pre-configured accounts:
* **Admin Account**:
  * Username: `admin`
  * Password: `AdminPassword123`
* **Customer Account**:
  * Username: `john_doe`
  * Password: `UserPassword123`

You can also create a new custom superuser at any time:
```bash
python manage.py createsuperuser
```

---

### 5. Start the Django Server

```bash
python manage.py runserver 8000
```
The backend API and server will run at: `http://127.0.0.1:8000/`

---

### 6. Open Frontend

You have two convenient options:

* **Option A (Direct via Django)**:
  Open `http://127.0.0.1:8000/index.html` or `http://127.0.0.1:8000/admin/dashboard.html` in your browser.
* **Option B (Separate Static Server / VS Code Live Server)**:
  Open `frontend/index.html` in VS Code with **Live Server** or double click to open in any web browser. CORS is fully configured.

---

## REST API Reference

### Authentication
* `POST /api/auth/register/` - Register new user (Default role: `USER`)
* `POST /api/auth/login/` - Login with username or email, returns JWT `access` and `refresh`
* `POST /api/auth/token/refresh/` - Refresh expired access token
* `POST /api/auth/logout/` - Blacklists refresh token

### Categories
* `GET /api/categories/` - List categories (supports `?search=`)
* `POST /api/categories/` - Create category (*Admin only*)
* `PUT /api/categories/{id}/` - Update category (*Admin only*)
* `DELETE /api/categories/{id}/` - Delete category (*Admin only*)

### Products
* `GET /api/products/` - List products (supports `?category=`, `?search=`, `?in_stock=true`)
* `GET /api/products/{id}/` - Retrieve single product
* `POST /api/products/` - Create product with multipart image upload (*Admin only*)
* `PUT /api/products/{id}/` - Update product & stock (*Admin only*)
* `DELETE /api/products/{id}/` - Delete product (*Admin only*)

### Orders
* `POST /api/orders/` - Place order (Atomic transaction, validates & decrements stock)
* `GET /api/orders/` - List orders (Customer sees own orders; Admin sees all)
* `GET /api/orders/{id}/` - View order details
* `PATCH /api/orders/{id}/status/` - Update order status to `Completed` (*Admin only*)
* `GET /api/orders/dashboard-stats/` - Aggregated stats & completed revenue (*Admin only*)

### Users
* `GET /api/users/` - List all registered customers (*Admin only*)
* `GET /api/users/profile/` - View current user profile
* `PUT /api/users/profile/` - Update current user profile

---

## Running Unit Tests

Run the full automated test suite covering all 17 critical test cases:

```bash
python manage.py test
```

---

## License
MIT License. Built for technical interviews and production reference.
