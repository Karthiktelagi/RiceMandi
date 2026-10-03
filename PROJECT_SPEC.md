# RiceMandi — APMMC Yard Rice Trading Platform

**Project specification v2.0**
Stack: Django (Python) · PostgreSQL · HTMX · Bootstrap · Django REST Framework
Layout: `backend/` + `frontend/` · Deploy: Render (+ Vercel when needed)

---

## 1. One-paragraph summary

RiceMandi is a bilingual (Kannada/English) web platform for rice and paddy
merchants trading at the APMMC yard. Merchants register and post live lots —
rice variety, price per quintal, quantity, mill source, moisture and breakage —
while buyers browse the day's market rates, watch price trends, receive
notifications when a variety they follow drops in price, and negotiate directly
with merchants over built-in chat. Admins verify merchants, manage the master
data (mills, varieties), and monitor every listing.

It is built as a single Django service where the web UI and the future mobile
API read from the same models and the same permission layer, so building an app
later is additive rather than a rewrite.

---

## 2. Problem being solved

Today the yard runs on phone calls, WhatsApp groups and a chalkboard:

- A buyer arriving at the yard cannot tell today's rate for Sona Masoori
  without walking to five different shops and asking.
- A merchant does not know a competitor undercut them by ₹50 this morning.
- Nobody has historical data, so pricing is memory and rumour.
- Quality disputes (moisture %, breakage %) are verbal, causing trust issues.

RiceMandi turns that into a searchable, timestamped, shared dataset.

---

## 3. Users and roles

| Role | Registration | Capabilities |
|---|---|---|
| **Public visitor** | none | Browse today's market rates, variety detail pages, price charts |
| **Buyer** | self-signup with phone | Everything public + follow varieties, set price-drop alerts, chat with merchants, send enquiries |
| **Merchant** | self-signup, then **admin approval required** | Everything a buyer can do + post/edit/delete own lots, manage inventory, set availability |
| **Admin** | created via `createsuperuser` | Verify merchants, CRUD mills and varieties, feature listings, view all users, moderate chats, see analytics |

A merchant cannot post a lot until an admin sets `is_approved = True`. Until
then the merchant sees a "pending verification" screen.

---

## 4. Tech stack

| Layer | Choice | Reason |
|---|---|---|
| Framework | **Django 5.x** | Python. Built-in auth, admin panel, i18n (Kannada included), ORM |
| Language | Python 3.11+ | |
| Database | **PostgreSQL** (Neon / Supabase / Render) | Postgres in production, SQLite locally, one env var swap |
| Web UI | Django templates + **HTMX** | Server-rendered, no build step, fast to iterate |
| API | **Django REST Framework** | Same models, feeds the future mobile app |
| CSS | **Bootstrap 5** + custom stylesheet | Mobile-first — most yard users are on phones |
| Charts | **Chart.js** | Price trend graphs |
| Images | Pillow | Rice photos, mill photos, profile photos |
| Auth for app | DRF token auth | Standard, simple, sufficient for v1 |
| Deploy | **Render** | Single service to start |

**Why one Django service instead of a separate frontend:** Django's admin panel,
auth, and i18n all depend on templates and the ORM living together. Splitting
into a JSON API plus a React app would multiply the work by 3–4x and discard the
admin panel. The app-readiness goal is met through the `api.py` layer instead —
see section 11.

---

## 5. Directory structure

```
ricemandi/
├── backend/                      ← deploy this to Render
│   ├── manage.py
│   ├── requirements.txt
│   ├── config/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── asgi.py
│   │   └── wsgi.py
│   ├── apps/
│   │   ├── accounts/
│   │   │   ├── models.py         User, profiles, roles
│   │   │   ├── views.py          login, signup, dashboards
│   │   │   ├── forms.py
│   │   │   ├── middleware.py     language switching
│   │   │   └── admin.py
│   │   ├── market/
│   │   │   ├── models.py         Mill, Variety, Lot, PriceRecord, Watch, Enquiry
│   │   │   ├── views.py          HTML pages
│   │   │   ├── api.py            JSON endpoints → mobile app
│   │   │   ├── serializers.py
│   │   │   ├── forms.py
│   │   │   ├── permissions.py    role gates
│   │   │   ├── signals.py        price snapshots, notifications
│   │   │   └── admin.py
│   │   ├── chat/
│   │   │   ├── models.py         Conversation, Message
│   │   │   ├── views.py
│   │   │   ├── api.py
│   │   │   └── admin.py
│   │   ├── notifications/
│   │   │   ├── models.py         Notification
│   │   │   ├── views.py
│   │   │   ├── services.py       creation helpers
│   │   │   └── admin.py
│   │   └── core/                 home page, language switch, shared tags
│   ├── templates/
│   │   ├── base.html
│   │   ├── partials/             nav, footer, lot cards, pagination
│   │   ├── accounts/
│   │   ├── market/
│   │   ├── chat/
│   │   └── registration/
│   ├── static/
│   │   ├── css/site.css
│   │   └── js/site.js
│   └── locale/
│       ├── kn/LC_MESSAGES/django.po
│       └── en/LC_MESSAGES/django.po
├── frontend/                     ← placeholder until the mobile app
│   └── README.md
├── docs/
│   ├── PROJECT_SPEC.md           ← this file
│   └── DEPLOY.md
└── .env                          ← secrets, never committed
```

**What goes where, plainly:**

- `backend/` — all the logic, all the database, all the web pages. **This is
  what gets deployed.** One folder, one service.
- `frontend/` — empty for now, with a README explaining it is where the
  React Native / Flutter app goes. Nothing to maintain until then.

---

## 6. Database models

### 6.1 `accounts.User` (extends `AbstractUser`)

| Field | Type | Notes |
|---|---|---|
| `phone` | CharField(15) | unique; login ID alongside username |
| `role` | CharField | `buyer` / `merchant` / `admin` |
| `is_approved` | BooleanField | merchants only; gates posting |
| `business_name` | CharField | merchants |
| `gst_number` | CharField | merchants, optional |
| `photo` | ImageField | profile photo |
| `preferred_language` | CharField | `kn` or `en` |

### 6.2 `accounts.LanguageMiddleware`

Reads language from session (set by the toggle), falls back to the user's
`preferred_language`, then to `Accept-Language`, then English.

### 6.3 `market.Mill`

| Field | Type | Notes |
|---|---|---|
| `name` | CharField | |
| `location` | CharField | town or district |
| `state` | CharField | |
| `contact_phone` | CharField | |
| `capacity_quintal_per_day` | IntegerField | optional |
| `is_active` | BooleanField | admin toggle |

### 6.4 `market.Variety`

| Field | Type | Notes |
|---|---|---|
| `name` | CharField(120) | e.g. Sona Masoori, Basmati 1121, Joha |
| `category` | CharField | `paddy` / `rice` / `broken` / `bran` |
| `grade` | CharField | Grade 1 / Grade 2 / Common |
| `description` | TextField | |
| `image` | ImageField | |
| `is_active` | BooleanField | admin toggle |
| `created_by` | FK → User, nullable | who added it; null for seeded/admin data |
| `created_at` | DateTime | |

Constraints:

- `name` is unique **case-insensitively**, with surrounding whitespace trimmed, so
  `Basmati 1121`, `basmati 1121` and `Basmati-1121` cannot become three rows.
- A model-level `clean()` raises `ValidationError` on a duplicate and the form
  surfaces a link to the existing variety instead of a dead-end error.

### 6.5 `market.Lot` — the core record

| Field | Type | Notes |
|---|---|---|
| `merchant` | FK → User | who is selling |
| `variety` | FK → Variety | |
| `mill` | FK → Mill | where it came from |
| `price_per_quintal` | Decimal(10,2) | ₹ per 50 kg |
| `quantity_quintal` | Decimal(10,2) | available |
| `arrival_date` | DateField | when stock arrived in the yard |
| `moisture_pct` | Decimal(5,2) | quality marker, e.g. 12.5 |
| `broken_pct` | Decimal(5,2) | e.g. 3.0 |
| `grain_length_mm` | Decimal(5,2) | optional, Basmati grading |
| `milling_pct` | Decimal(5,2) | optional |
| `notes` | TextField | free text |
| `photo` | ImageField | optional |
| `is_available` | BooleanField | merchant toggles sold-out |
| `is_featured` | BooleanField | admin promotes to top |
| `status` | CharField | `active` / `sold` / `withdrawn` |
| `created_at` / `updated_at` | timestamps | |

### 6.6 `market.PriceRecord`

Append-only snapshot of a lot's price, written on every price change. This is
what feeds the charts — history is never overwritten.

| Field | Type | Notes |
|---|---|---|
| `variety` | FK → Variety | |
| `lot` | FK → Lot, nullable | |
| `price_per_quintal` | Decimal | |
| `recorded_at` | DateTime | auto |

### 6.7 `market.Watch` — a buyer following a variety

| Field | Type | Notes |
|---|---|---|
| `user` | FK → User | |
| `variety` | FK → Variety | |
| `target_price` | Decimal, nullable | optional "notify me below ₹X" |
| `created_at` | DateTime | |

Unique together on `(user, variety)`.

### 6.8 `market.Enquiry`

| Field | Type | Notes |
|---|---|---|
| `buyer` | FK → User | |
| `lot` | FK → Lot | |
| `message` | TextField | |
| `quantity_wanted` | Decimal, nullable | |
| `status` | CharField | `open` / `closed` |
| `created_at` | DateTime | |

Creating an enquiry also auto-creates the chat thread.

### 6.9 `chat.Conversation`

| Field | Type | Notes |
|---|---|---|
| `buyer` | FK → User | |
| `merchant` | FK → User | |
| `lot` | FK → Lot, nullable | context |
| `created_at` | DateTime | |
| `last_message_at` | DateTime | for inbox sorting |

Unique together on `(buyer, merchant, lot)` to prevent duplicate threads.

### 6.10 `chat.Message`

| Field | Type | Notes |
|---|---|---|
| `conversation` | FK → Conversation | |
| `sender` | FK → User | |
| `body` | TextField | |
| `read_at` | DateTime, nullable | read receipts |
| `created_at` | DateTime | |

### 6.11 `notifications.Notification`

| Field | Type | Notes |
|---|---|---|
| `recipient` | FK → User | |
| `kind` | CharField | `price_drop` / `new_lot` / `enquiry` / `message` / `approval` / `system` |
| `title` | CharField | rendered in recipient's language at creation |
| `body` | TextField | |
| `url` | CharField | click-through link |
| `is_read` | BooleanField | |
| `created_at` | DateTime | |

---

## 7. Pages and routes

### Public (no login)

| URL | Page | Contents |
|---|---|---|
| `/` | Home | Today's rate board — one row per variety with min/max/average price, "updated 5 min ago", featured lots |
| `/varieties/` | Variety list | filter by category and grade, search |
| `/varieties/manage/` | Variety management | full table of every variety with edit / deactivate actions. Merchants see only their own; admins see all. Also holds the "Add variety" button |
| `/varieties/<id>/` | Variety detail | current lots table, price trend chart, all merchants offering it |
| `/mills/` | Mills list | |
| `/register/` | Signup | choose buyer or merchant; merchant form asks business name, GST |
| `/login/` | Login | |
| `/lang/kn/` `/lang/en/` | Language switch | sets session, redirects back |

### Buyer / Merchant (login required)

| URL | Page |
|---|---|
| `/dashboard/` | Role-aware dashboard |
| `/watch/` | Watched varieties and alert thresholds |
| `/varieties/manage/new/` | Add a new variety |
| `/varieties/manage/<id>/edit/` | Edit a variety |
| `/varieties/manage/<id>/toggle/` | Activate / deactivate a variety |
| `/lots/<id>/` | Lot detail with "Send enquiry" |
| `/enquiries/` | Enquiries, buyer side and merchant side |
| `/inbox/` | Chat list |
| `/inbox/<conversation_id>/` | Chat thread |
| `/notifications/` | Notification list, mark read |
| `/merchant/lots/new/` | Post a lot |
| `/merchant/lots/` | My lots: edit, mark sold, delete |
| `/merchant/profile/` | Edit business profile |

### Admin (staff or `role=admin`)

| URL | Page |
|---|---|
| `/admin/` | **Django admin** — mills, varieties, all lots, all users |
| `/dashboard/admin/pending/` | Merchants awaiting approval, one-click approve/reject |
| `/dashboard/admin/analytics/` | Lots per variety, active merchants, volume, top listings |

---

## 8. Feature specifications

### 8.1 Market rate board — the hook

- Home page shows each active variety with **min, max and average price per
  quintal**, computed from `Lot` rows where `status='active'` and
  `is_available=True`.
- Updates via HTMX polling every 60 seconds. No reload, no refresh button.
- A green/red arrow shows change since the previous day, from `PriceRecord`.
- Clicking a variety opens its detail page.

### 8.2 Posting a lot

- Only merchants with `is_approved=True` see the form; others get a pending notice.
- Validated fields, sensible defaults, image upload with a size limit.
- On create, a `PriceRecord` snapshot is written so history starts immediately.
- Every new lot triggers a `new_lot` notification to users watching that variety.

### 8.3 Price history and charts

- Every price edit writes a `PriceRecord`; the old value is preserved.
- Variety detail renders a Chart.js line graph of average price over time.
- Range selector: 30 days / 90 days / 1 year.
- Useful both ways: buyers see when to buy, merchants see what competitors did.

### 8.4 Watchlist and price-drop alerts

- A buyer watches any variety, optionally with a target price.
- When a lot lands below the target — or below yesterday's average past a
  threshold — a `price_drop` notification goes to every watcher.
- This is the feature that brings buyers back daily.

### 8.5 Enquiry flow

- Buyer clicks "Send enquiry" on a lot → form with quantity wanted and a message.
- Creates an `Enquiry` **and** a `Conversation` in one step.
- Merchant is notified and sees it on their dashboard and enquiries page.

### 8.6 Chat

- One thread per `(buyer, merchant, lot)`.
- Merchant sees buyer name, variety, and last message snippet, sorted by
  `last_message_at` — the same mental model as WhatsApp.
- Unread badge counts unread messages.
- v1 polls every 5 seconds via HTMX. Phase 2 uses WebSockets via Channels + Redis.
- **Phone numbers are masked until an enquiry exists**, to prevent scraping.

### 8.7 Notifications

- Bell icon in the navbar with an unread count badge.
- Kinds: price drop on a watched variety, new lot in a watched variety, enquiry
  received, new chat message, merchant approved or rejected.
- Titles and bodies are generated in the recipient's preferred language at
  creation time, so no live translation is needed at read time.

### 8.8 Bilingual UI — Kannada and English

- `LocaleMiddleware` plus Django i18n.
- Toggle in the navbar sets the session language and remembers per user.
- All user-facing strings marked `{% trans "..." %}`.
- Kannada (`kn`) locale files via `makemessages`.
- **Currency, numbers and dates formatted per locale** — `₹1,850/ಕ್ವಿಂಟಾಲ್` in
  Kannada, `₹1,850/quintal` in English. Price per quintal is the universal unit
  because that is how the yard quotes.

### 8.10 Variety management — the "add a new variety" page

New varieties keep entering the trade, and the platform is useless if a merchant
cannot register one while standing in the yard. This page is built for speed.

**Who can write**

| | Create new | Edit existing | Deactivate |
|---|---|---|---|
| Public / buyer | no | no | no |
| Merchant, unapproved | no | no | no |
| Merchant, approved | **yes** | only varieties they created | only their own |
| Admin | **yes** | **any** | **any** |

Merchants get a read-only public list plus full create rights. Only admins edit
or deactivate a variety anyone else depends on — deactivating a shared variety
would silently hide every merchant's lots for it.

**The management page** — `/varieties/manage/`

A sortable, searchable table:

| Column | Notes |
|---|---|
| Name | links to the public variety page |
| Category | paddy / rice / broken / bran |
| Grade | |
| Live lots | count of active, available lots — shows what is actually trading |
| Added by | merchant business name, or "admin" |
| Status | active / inactive badge |
| Actions | Edit, Deactivate/Activate |

Summary counters at the top: total varieties, active, inactive, and how many
have zero live lots. That last counter is how stale data gets noticed.

**The form** — `/varieties/manage/new/`

Deliberately short, because merchants fill this in on a phone in the yard:

- **Name** — required, trimmed, duplicate-checked
- **Category** — paddy / rice / broken / bran
- **Grade** — Grade 1 / Grade 2 / Common
- **Description** — optional
- **Photo** — optional

**Duplicate handling.** Typing `Basmati 1121` when it already exists does not
save a second row. The form shows:

> "Basmati 1121 already exists. Use the existing variety instead."

with a direct link to it. The check is case-insensitive and ignores surrounding
spaces, so ` basmati 1121 ` also resolves to the existing row.

**Effect of creating one.** The new variety immediately appears in that
merchant's lot-posting dropdown and on the public list. No notification is sent —
watches are created explicitly, so there is nobody to notify yet.

**Deleting is never offered.** A variety is deactivated instead, so existing
lots, price history and chat threads keep their meaning. Hard deletes would
orphan `PriceRecord` rows and silently corrupt the charts.

### 8.11 Roles and permissions

| Action | Public | Buyer | Merchant (approved) | Admin |
|---|---|---|---|---|
| View rates and charts | ✓ | ✓ | ✓ | ✓ |
| Watch varieties | | ✓ | ✓ | ✓ |
| Chat | | ✓ | ✓ | ✓ |
| Post a lot | | | ✓ | ✓ |
| Create a variety | | | ✓ | ✓ |
| Edit a variety | | | own only | any |
| Deactivate a variety | | | own only | any |
| Verify merchants | | | | ✓ |
| Edit mills | | | | ✓ |
| Feature a listing | | | | ✓ |

Enforced three times: a `@login_required` decorator, a `@merchant_required`
mixin, and a model-level check. Template `{% if %}` hides buttons, but that is
never the only defence.

---

## 9. Admin experience

Because Django ships with an admin panel, `/admin/` gives mills, varieties,
users, lots, enquiries and messages as searchable tables with filters — for
free. On top of that, one custom screen:

**Merchant approvals** — pending merchants in a table with GST number and
business name, and Approve / Reject buttons. Approval notifies the merchant and
lets them post immediately.

---

## 10. Deployment

**Local:** SQLite, `python manage.py runserver`

**Production:**

| Service | Free tier | Paid |
|---|---|---|
| Database | Neon Postgres or Supabase | — |
| Web app | Render free web service | Render Starter, $7/mo |
| Static files | Whitenoise, served by Django | |
| Media | Cloudinary free tier or S3 | |
| Redis (phase 2) | Render Redis free | |

`settings.py` switches on `DATABASE_URL`:

```python
if env("DATABASE_URL"):
    DATABASES = {"default": dj_database_url.parse(env("DATABASE_URL"))}
else:
    DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", ...}}
```

**One service to start.** When the mobile app arrives, the same Render service
serves the JSON API at `/api/v1/`. Splitting frontend and backend across two
hosts is only worth doing if someone else is building the app separately.

**Start free, upgrade when business use begins.** Free Render sleeps after
inactivity — fine for testing, but the first request after a cold start can take
~30 seconds, which feels broken to a merchant standing at the yard. Upgrade to
the paid web service before real users arrive.

---

## 11. Mobile app path

The reason for the `api.py` layer. Today the browser calls `views.py`; the app
will call `api.py`. Same models, same permissions, same auth.

```
Today    →  Browser  →  views.py  →  HTML
App day  →  Phone    →  api.py    →  JSON, identical data
```

Steps when the time comes:

| Step | Work |
|---|---|
| 1 | Add `djangorestframework` and token auth |
| 2 | Write `api.py` for the six screens the app needs |
| 3 | Build React Native or Flutter in `frontend/` |
| 4 | Point it at `https://yourapp.onrender.com/api/v1/` |
| 5 | Ship to Play Store |

No changes to models, views or database. That is the whole point of writing the
API layer early — it costs a little now and saves a rewrite later.

Sample endpoint shape:

```python
# backend/apps/market/api.py
@api_view(["GET"])
def variety_list(request):
    lots = Lot.objects.filter(status="active", variety__is_active=True)
    return Response([
        {
            "variety": l.variety.name,
            "price": float(l.price_per_quintal),
            "mill": l.mill.name,
            "moisture": float(l.moisture_pct),
            "broken": float(l.broken_pct),
            "merchant": l.merchant.business_name,
            "phone": mask_phone(l.merchant.phone),  # stays masked
        }
        for l in lots
    ])
```

---

## 12. Build milestones

| # | Milestone | Deliverable |
|---|---|---|
| 1 | Scaffold | Django project, apps, settings, SQLite, base template, navbar, language toggle |
| 2 | Models | All 11 models, migrations, seed data (real Karnataka varieties, sample mills) |
| 3 | Auth | Signup with role choice, login, logout, merchant approval gate |
| 4 | Market board | Home rate board, variety list and detail, mill pages |
| 5 | Lot posting | Merchant forms, edit, mark sold, my-lots page |
| 6 | Price history | `PriceRecord` automation plus Chart.js graphs |
| 7 | Watch and alerts | Watchlist, target prices, notification engine, bell UI |
| 8 | Enquiries and chat | Enquiry form, conversation model, inbox, polling chat |
| 9 | i18n | Kannada and English `.po` files, all strings translated |
| 10 | Admin polish | Approvals screen, analytics, permission polish |
| 11 | API layer | DRF installed, `api.py` per app, token auth, documented endpoints |
| 12 | Deploy | Postgres, Render, env vars, static and media, phone smoke test |

---

## 13. Cost reality

| Item | Free option | Paid option |
|---|---|---|
| Database | Neon / Supabase free | ₹0–400/mo |
| Hosting | Render free (sleeps) | ₹700/mo Render Starter |
| Media | Cloudinary free | ₹0 |
| Domain | — | ₹700/yr |
| **Total** | **₹0 for testing** | **~₹1,000/mo with a domain** |

---

## 14. Future scope

- Paddy versus rice toggle with conversion-based pricing
- Bulk upload — merchant pastes a WhatsApp message, system parses it into lots
- SMS fallback for merchants without smartphones
- Truck and hamali logistics board
- Market fee calculator — commission and hamali charges per lot
- Kannada voice input, given literacy levels among older merchants
- Mobile app, once the web version proves itself
- APMMC official rate feed integration, if the yard publishes one
- Credit and trust scoring for repeat buyers and merchants

---

## 15. Explicit non-goals for v1

- Online payment or escrow — the yard handles payments in person
- Live WebSocket chat — polling is fine initially
- Native mobile apps
- Delivery and logistics tracking
- Ratings and reviews — build trust through the approval process first