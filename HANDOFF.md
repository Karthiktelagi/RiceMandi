# RiceMandi — Session Handoff

**Date:** 2026-10-02  
**Status:** Core features built, language toggle fixed, server running

---

## What's Working

- Django 5.2.17 project at `C:\Users\pc\ricemandi\backend`
- All models created and migrated (accounts, market, chat, notifications)
- Auth: signup (buyer/merchant), login, logout, merchant approval flow
- Market: variety CRUD, lot posting, rate board, watchlist
- Queue: first-come-first-serve booking system
- Negotiation: buyer/merchant counter-offer system
- Packet pricing: 1 packet = 26 kg, auto-calculated
- Admin: Django admin + custom merchant approvals screen
- API: basic DRF endpoints at `/api/v1/`
- Language toggle: Kannada/English (FIXED — was `LANGUAGE_SESSION_KEY` bug)
- UI: Bootstrap 5 + HTMX, dark green navbar, responsive

---

## Test Credentials

| Role | Username | Password |
|---|---|---|
| Admin | `admin` | `admin123` |
| Merchant | `merchant1` | `pass123` |
| Buyer | sign up at `/signup/` | — |

---

## How to Run

```powershell
cd C:\Users\pc\ricemandi\backend
C:\Users\pc\ricemandi\venv\Scripts\python.exe manage.py runserver
# Open http://127.0.0.1:8000
```

---

## Models (apps/market/models.py)

- `Mill` — rice mills
- `Variety` — rice varieties (case-insensitive unique name)
- `Lot` — merchant lots with price/quantity/packets/demand/available
- `PriceRecord` — append-only price history (auto-created on lot save)
- `Watch` — buyer watching a variety
- `Enquiry` — buyer enquiry on a lot
- `Booking` — first-come-first-serve queue (unique together: lot+buyer)
- `Negotiation` — price negotiation (buyer_price, merchant_price, status)
- `PriceAlert` — price drop alerts (target_price, triggered flag)
- `TraderRating` — 1-5 star rating system
- `MarketTrend` — daily avg/min/max/volume per variety

---

## Key Files

| File | Purpose |
|---|---|
| `apps/core/views.py` | Home (rate board), language toggle |
| `apps/market/views.py` | All market views (varieties, lots, booking, negotiation) |
| `apps/market/models.py` | All market models |
| `apps/market/forms.py` | VarietyForm, LotForm, MillForm |
| `apps/market/signals.py` | Auto PriceRecord + packet calculation |
| `apps/market/permissions.py` | Role-based decorators |
| `apps/accounts/views.py` | Signup, dashboard, merchant approve/reject |
| `apps/accounts/middleware.py` | Language preference middleware |
| `config/urls.py` | Root URL config |
| `config/settings.py` | Django settings |

---

## Bugs Fixed This Session

1. **Language toggle crash** — `translation.LANGUAGE_SESSION_KEY` removed in Django 5.x
   - Fix: use literal `"django_language"` string in `core/views.py` and `accounts/middleware.py`
2. **Models file truncated** — rewrote full file with all models
3. **Signals import error** — changed to `from apps.market import models` pattern

---

## Next Steps (Priority Order)

### High Priority
1. **Price alert engine** — management command/cron that checks lot prices against `PriceAlert` targets and creates `Notification` when triggered
2. **Rating UI** — star rating widget on completed bookings, show avg rating on merchant profile
3. **Trend charts** — Chart.js line graph on variety detail page using `MarketTrend` data
4. **Kannada translations** — `makemessages -l kn`, translate all strings, `compilemessages`

### Medium Priority
5. **Merchant verification badge** — show verified badge next to approved merchants
6. **Booking management for merchants** — confirm/cancel bookings, mark completed
7. **Notification bell** — unread count in navbar, notification list page
8. **Enquiry auto-creates chat thread** — when enquiry submitted, create Conversation

### Low Priority
9. **API expansion** — full DRF endpoints for all models (Milestone 11)
10. **Deploy prep** — Render config, Postgres, env vars (Milestone 12)
11. **Tests** — unit tests for models, views, permissions

---

## Competitor Analysis (Key Takeaways)

| Platform | What They Do | RiceMandi's Edge |
|---|---|---|
| Rice Route | Rice B2B matching | We have live rates + queue + negotiation |
| APMC Connect | Trader catalog | We are transactional |
| Bijak Mandi | Agri trading app | We are rice-only + yard-specific |
| agriSATHI | APMC management | We are merchant-first |
| Kisan Setra | Mandi prices | We have queue + negotiation |
| commodityonline | Agri B2B | We are hyper-local |

**Our moat:** Live rates + first-come-first-serve queue + in-app negotiation + packet pricing + Kannada-first. No competitor has all five.

---

## Open Questions

1. **Real variety list** — need actual Karnataka rice varieties from user's father
2. **Enquiry → chat thread** — auto-create conversation on enquiry? (proposed, not confirmed)
3. **Packet size** — is 1 packet = 26 kg correct for all varieties? (user specified 26 kg)
4. **Queue expiry** — should bookings expire after X hours if not confirmed?
5. **Negotiation timeout** — should offers expire after X hours?

---

## Reminder for Tomorrow

- [ ] Check if user confirmed variety list
- [ ] Implement price alert engine
- [ ] Add rating UI
- [ ] Add trend charts
- [ ] Start Kannada translations
- [ ] Add notification bell
- [ ] Merchant booking management
- [ ] Write tests

---

**Resume command:** `Read C:\Users\pc\ricemandi\HANDOFF.md and continue building`
