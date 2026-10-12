# FoodieHub — Online Food Ordering & Delivery System

FoodieHub is an original Django web application for discovering local restaurants, browsing menus, building a cart, placing orders and tracking order status. It includes a separate restaurant-manager workspace and Django Admin. The project is suitable for learning, a college demonstration and a GitHub portfolio. It is not deployed or connected to a live restaurant service.

## Implemented features

- Customer registration, sign-in/sign-out, profile and delivery address management.
- Public home page, restaurant discovery, restaurant menu, food details, text search, category/price/diet/availability filters, sorting and pagination.
- Session cart with server-calculated prices, quantity validation and a one-restaurant-at-a-time rule.
- Authenticated checkout with address selection, transactional order creation, duplicate-checkout token, historical item/price snapshots, Cash on Delivery and order cancellation rules.
- Customer order history and status-based tracking. This is **not live GPS tracking**.
- Restaurant manager dashboard scoped to a manager's assigned restaurant; menu/category/restaurant profile maintenance; order status transitions; aggregate sales chart.
- Django Admin for user roles, restaurants, menu, orders and payments.
- Optional Razorpay hosted Checkout in test mode, using environment credentials and server-side signature verification. Without test credentials, Cash on Delivery continues to work and no fake payment-success state is shown.
- Custom error pages, CSRF-protected state changes, database-backed permissions, automated tests and sample data command.

## Technology and architecture

Django 5.2 uses MVT: `config/urls.py` routes requests to app views; views validate input and query models through Django ORM; templates render HTML; static CSS/JavaScript handle presentation and small interactions. SQLite is the default for local development. MySQL can be enabled with the optional driver requirements. Bootstrap 5 and Bootstrap Icons are loaded from CDN. Sample photos are local files under `static/images/`; see [IMAGE-CREDITS.md](IMAGE-CREDITS.md).

```text
FoodieHub/
├── accounts/       # Custom User, addresses, registration/profile views
├── cart/           # Session-cart services and POST operations
├── config/         # Project settings and top-level URL routing
├── core/           # Homepage, public pages, shared context, common tests
├── dashboard/      # Restaurant manager analytics and scoped management
├── menu/           # Category and FoodItem models, filters, seed command
├── orders/         # Order and snapshot models, checkout, lifecycle rules
├── payments/       # Payment record, Razorpay adapter and callback verification
├── restaurants/    # Restaurant model, public discovery, manager profile form
├── templates/      # Shared base and per-feature Django templates
├── static/         # CSS, JavaScript and local example images
├── media/          # Uploaded menu/restaurant images (local development only)
├── manage.py
├── requirements.txt
├── requirements-mysql.txt
└── .env.example
```

### Main data relationships

`User` is FoodieHub's custom `AbstractUser` with a role. A manager owns one or more `Restaurant` rows. Each restaurant has `Category` and `FoodItem` rows. A customer owns `Address` rows and `Order` rows. Orders reference one restaurant and contain `OrderItem` snapshots; historical names and unit prices remain intact if menu data changes. `Payment` is one-to-one with an order. Cart data lives in the Django session and always reads current prices from the database; checkout copies those prices into order items inside an atomic transaction.

## Run locally on Windows / VS Code

Install Python 3.11 or 3.12, VS Code with the Python extension, and (for GitHub) Git. Extract this ZIP or clone the repository, then open the `FoodieHub` folder in VS Code. In a PowerShell terminal at that folder:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
# If activation is blocked, allow local scripts for this user once:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate
python manage.py check
python manage.py seed_foodiehub
python manage.py createsuperuser
python manage.py runserver
```

Open `http://127.0.0.1:8000/`. Admin is at `/admin/`. In VS Code use **Ctrl+Shift+P → Python: Select Interpreter** and select `.venv\Scripts\python.exe`.

This project does not automatically load `.env`; `.env.example` is a reference file. Set optional values in the active PowerShell terminal with `$env:NAME = "value"` before starting the server.

To sign into the seeded restaurant manager, create the superuser first. Then run `python manage.py changepassword demo_manager` and choose a local password. The seed account has an unusable password by design; never reuse a demo password in production. Admin can also assign the `restaurant_manager` role and associate a restaurant with a manager. Customer accounts are created from the public registration page.

Uploaded images are stored under `media/` locally. Empty image fields show a styled fallback instead. Add food through **Manager → Menu** or **Admin → Menu → Food items**. The sample-data command is repeatable and does not reset or erase records.

## MySQL option

SQLite is the simplest starting point and the default. To use MySQL, create a database with `utf8mb4`, install the driver, then set the environment variables in the PowerShell session before starting Django:

```powershell
pip install -r requirements-mysql.txt
$env:DB_ENGINE = "mysql"
$env:MYSQL_DATABASE = "foodiehub"
$env:MYSQL_USER = "foodiehub_user"
$env:MYSQL_PASSWORD = "your-local-db-password"
$env:MYSQL_HOST = "127.0.0.1"
$env:MYSQL_PORT = "3306"
python manage.py migrate
```

Create the database and a least-privilege local user in MySQL first. Do not commit the password. For a fresh setup, run migrations only after the environment points at the intended database.

## Optional Razorpay test mode

Cash on Delivery works without Razorpay. To enable online test checkout, install `requirements.txt`, create test-mode API keys in your Razorpay account, and set them only in your local process environment:

```powershell
$env:RAZORPAY_KEY_ID = "rzp_test_..."
$env:RAZORPAY_KEY_SECRET = "..."
python manage.py runserver
```

With both test keys present, checkout exposes the Razorpay option, creates a gateway order, opens Razorpay Checkout and posts the returned signature to Django for verification. The server uses the Razorpay SDK; browser success alone is not trusted. The app never stores card numbers or CVVs. Test with Razorpay's current sandbox test instruments from its official documentation. No live credentials are provided or included. Refund initiation is not implemented; an admin can review payment records, but do not treat a cancellation as a processed refund.

## Tests and verification

Run:

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```

Tests cover homepage/menu queries, registration, cart price handling and restaurant mixing, unavailable items, checkout totals and snapshots, duplicate checkout, user order ownership, manager scoping and status-transition rules. Payment-signature tests require configured test keys and are not run as a live transaction.

## Screenshots

After you run the app locally, capture the home page, filtered menu, customer checkout, order tracking and manager dashboard. Store only demo data in screenshots and add the images under `screenshots/` before inserting them here.

## Security and production notes

The Django ORM is used for queries. State-changing forms use POST and CSRF tokens. Customer addresses and orders are filtered by owner; manager endpoints first resolve the restaurant owned by the signed-in manager. Prices and totals are computed on the server. Uploaded image validation relies on Django/Pillow; production deployments should also enforce size/type limits and use managed media storage.

Before deploying, set a random `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=false`, `DJANGO_ALLOWED_HOSTS` to the exact hostnames, and `CSRF_TRUSTED_ORIGINS`/HTTPS settings appropriate to the hosting platform. Serve static assets with `collectstatic`; use persistent/managed storage for media and a managed database for production. Configure secure cookies, HTTPS redirection, logging, backups and email. Do not deploy the development SQLite database or local media directory as a production data strategy. This repository has **not** been deployed; hosting, domain, database and media configuration remain your responsibility.

## GitHub upload

Create a new empty GitHub repository, then from the project folder:

```powershell
git init
git add .
git status
git commit -m "Build FoodieHub Django ordering app"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/FoodieHub.git
git push -u origin main
```

Check `git status` before pushing. `.gitignore` excludes `.env`, virtual environments, local database and uploads. Commit `.env.example`, never a real `.env` or secret. Add your own screenshots under `screenshots/` and update the README screenshots section after you run the app.

## Troubleshooting

- **`py` not found:** reinstall Python and enable “Add Python to PATH”; use `python` if it points to Python 3.11/3.12.
- **PowerShell activation blocked:** run the user-scoped `Set-ExecutionPolicy` command above, or use `.venv\Scripts\python.exe` directly.
- **`No module named django` / Pillow:** activate `.venv`, then run `pip install -r requirements.txt`.
- **MySQL driver errors:** make sure `requirements-mysql.txt` was installed and that server credentials/database name match the environment.
- **No restaurants appear:** run `python manage.py seed_foodiehub` or add a restaurant and menu through Admin.
- **Manager gets 404:** assign a restaurant to the signed-in account and set its role to Restaurant Manager in Admin.
- **Razorpay option is missing:** it is intentionally hidden unless both `RAZORPAY_KEY_ID` and `RAZORPAY_KEY_SECRET` are set in the current server terminal.
- **Images missing in production:** configure a persistent media storage provider; Django's local media serving is enabled only for development.
- **Migration mismatch:** run `python manage.py makemigrations` and inspect the generated migration before `python manage.py migrate`. Do not delete a database that contains data you need.

## Future improvements

Add email verification/password reset delivery, a customer support inbox, discount/promo rules, delivery-partner accounts, live location tracking, refunds/webhooks, image moderation, rate limiting, and production-grade object storage. Keep the app honest about status-based tracking unless GPS updates are actually integrated.
