# RiceMandi

**Live rice and paddy rates at the APMC yard.** A B2B marketplace for rice merchants and buyers with live rates, first-come-first-serve queue booking, in-app negotiation, and packet pricing.

Built with Django 5.2 + Bootstrap 5 + HTMX.

---

## Features

- **Rate Board** — Live min/max/avg prices per variety
- **Variety Management** — CRUD for rice varieties (admin + approved merchants)
- **Lot Posting** — Merchants post lots with price, quantity, moisture, broken %, and photos
- **Packet Pricing** — Auto-calculated (1 packet = 26 kg)
- **First-Come-First-Serve Queue** — Buyers join a booking queue for each lot
- **Price Negotiation** — Buyers and merchants counter-offer in-app
- **Price Alerts** — Users set target prices, get notified when market drops
- **Watchlist** — Track favorite varieties
- **Trader Ratings** — 1-5 star rating system for completed bookings
- **Trend Charts** — 30-day price history with Chart.js
- **Chat** — Direct buyer-merchant messaging
- **Notifications** — Price drops, new lots, enquiries, messages
- **Kannada + English** — Full language toggle
- **REST API** — DRF endpoints at `/api/v1/`

---

## Quick Start

### Prerequisites

- Python 3.11+
- pip

### Setup

```bash
# Clone the repo
git clone https://github.com/Karthiktelagi/RiceMandi.git
cd RiceMandi/backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run dev server
python manage.py runserver
```

Open http://127.0.0.1:8000

### Test Credentials

| Role | Username | Password |
|---|---|---|
| Admin | `admin` | `admin123` |
| Merchant | `merchant1` | `pass123` |
| Buyer | Sign up at `/signup/` | — |

---

## Project Structure

```
backend/
├── config/          # Django settings, root URLs
├── apps/
│   ├── core/        # Home (rate board), language toggle
│   ├── accounts/    # Auth, signup, merchant approval
│   ├── market/      # Varieties, lots, booking, negotiation, ratings
│   ├── chat/        # Buyer-merchant messaging
│   └── notifications/ # Price alerts, notification bell
├── templates/       # Django templates
├── static/          # CSS, JS
└── locale/          # i18n translations (kn, en)
```

---

## API

Base URL: `/api/v1/`

| Endpoint | Description |
|---|---|
| `/api/v1/varieties/` | List all active varieties |
| `/api/v1/lots/` | List all active, available lots |

---

## Management Commands

```bash
# Check price alerts and send notifications
python manage.py check_price_alerts
```

---

## Tech Stack

- **Backend:** Django 5.2, Django REST Framework
- **Frontend:** Bootstrap 5, HTMX, Chart.js
- **Database:** SQLite (dev), PostgreSQL (production)
- **Auth:** Django auth + DRF Token auth
- **i18n:** Django translations (Kannada, English)

---

## License

Proprietary — All rights reserved.
