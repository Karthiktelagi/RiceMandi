# RiceMandi — Progress Log

Read this file first in any new session, then `PROJECT_SPEC.md` for the design.

---

## Status: PLANNING COMPLETE, CODE NOT STARTED

Decisions are locked. Nothing is built yet.

---

## Locked decisions

| Decision | Choice | Why |
|---|---|---|
| Framework | Django only (Python) | Built-in auth, admin panel, i18n. No second stack. |
| Database | PostgreSQL in prod, SQLite local | One env var swap |
| UI | Django templates + HTMX + Bootstrap 5 | Mobile-first, no build step |
| API | DRF, `api.py` alongside `views.py` | Makes the future mobile app additive, not a rewrite |
| Layout | `backend/` (deploys) + `frontend/` (placeholder) | Clear separation without splitting the app |
| Languages | Bilingual Kannada + English toggle | Yard merchants need Kannada |
| v1 scope | Core + price history + chat + notifications | Full build |
| Hosting | Free tier first | Upgrade to ~₹1000/mo when real users arrive |
| Variety writing | Approved merchants create; only admin edits others' | Stops one merchant deactivating a shared variety |
| Duplicate handling | Case-insensitive block with link to existing | Prevents "Basmati 1121" vs "basmati-1121" splitting |
| Delete policy | Deactivate only, never hard delete | Hard delete would orphan PriceRecord and corrupt charts |
| Units | ₹ per quintal everywhere | That is how the yard quotes |

---

## Environment

- Python 3.11.9 at `C:\Users\pc\AppData\Local\Programs\Python\Python311`
- Virtualenv created at `C:\Users\pc\ricemandi\venv` — **pip works, Django NOT yet installed**
- The `pip install django pillow` run was interrupted before finishing. Re-run it.
- Working dir: `C:\Users\pc\ricemandi`
- Not a git repo yet — run `git init` once code exists

---

## Done

- Full project spec written (`PROJECT_SPEC.md`, ~20 KB)
- This progress log

## Not started

All 12 milestones. Milestone 1 is next.

---

## Next actions for Milestone 1

```powershell
# 1. finish the venv install
C:\Users\pc\ricemandi\venv\Scripts\python.exe -m pip install django pillow djangorestframework
C:\Users\pc\ricemandi\venv\Scripts\python.exe -m pip install django-filter whitenoise dj-database-url python-decouple

# 2. scaffold
cd C:\Users\pc\ricemandi
django-admin startproject config backend
cd backend
python manage.py startapp accounts
python manage.py startapp market
python manage.py startapp chat
python manage.py startapp notifications
python manage.py startapp core

# 3. settings: apps, templates dir, LocaleMiddleware, kn locale, static
# 4. base.html with navbar + language toggle
# 5. home view stub
```

---

## Open questions still unanswered

1. **Real variety list** — asked the user for it from their father. Default seed
   is Sona Masoori, Joha, Basmati 1121, Basmati 1502, broken, bran. Must be
   confirmed before Milestone 2 seed data.
2. **Enquiry auto-creates chat thread** — proposed, not yet confirmed by user.

---

## Gotchas and notes

- Never rely on memory across sessions. Write decisions into `PROJECT_SPEC.md`
  the moment they are made. That file is the only durable memory.
- `PROJECT_SPEC.md` section numbering shifted when the variety management section
  was inserted — roles/permissions is now **8.11**, not 8.9.
- Keep quantity and price as `Decimal`, never float. Rupee amounts with floats
  will eventually produce a price like ₹1850.0000000002.
- Price per quintal is the canonical unit. Do not convert to kg/kg anywhere.

---

## Resume instructions

New chat, say exactly:

```
Read C:\Users\pc\ricemandi\PROGRESS.md and continue from milestone 1
```