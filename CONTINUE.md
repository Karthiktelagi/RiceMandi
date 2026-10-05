# RiceMandi — Continue Tomorrow

## Repo
- GitHub: https://github.com/Karthiktelagi/RiceMandi.git (branch `main`)
- Working dir: `C:\Users\pc\ricemandi`
- Venv Python: `C:\Users\pc\ricemandi\venv\Scripts\python.exe`
- Run server: `cd C:\Users\pc\ricemandi\backend; C:\Users\pc\ricemandi\venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000`
- Test creds: admin/admin123, merchant1/pass123

## DONE this session (not yet committed/pushed)
1. Fixed `ImproperlyConfigured` — added `allauth.account.middleware.AccountMiddleware` to `MIDDLEWARE` (backend/config/settings.py).
2. Replaced deprecated allauth settings with `ACCOUNT_LOGIN_METHODS = {"username"}` and `ACCOUNT_SIGNUP_FIELDS = ["username*", "password1*", "password2*"]`.
3. Password visibility eye toggle on login + signup: `togglePassword(fieldId, btn)` JS function added to both `templates/registration/login.html` and `signup.html`; password fields wrapped in `input-group` with eye button.
4. Kannada translations: .po was missing 190 strings actually used in templates. Added all 190 (now 369 total, 0 untranslated), recompiled `locale/kn/LC_MESSAGES/django.mo` with polib. Verified at runtime: `gettext('RiceMandi')` → `ರೈಸ್ ಮಂಡಿ`, `gettext('Home')` → `ಮುಖಪುಟ`.
5. Added `google_login_enabled` context processor (`apps/core/context_processors.py` → `site_settings`), registered in settings TEMPLATES.
6. Signup Google button now hidden when `GOOGLE_CLIENT_ID`/`GOOGLE_CLIENT_SECRET` are empty.
7. Created `backend/.env.example` documenting required env vars.
8. Fixed Google URL name: `{% url 'accounts:google_login' %}` → `{% url 'google_login' %}` (allauth provider URLs are NOT namespaced).
9. Added `allauth.socialaccount` and `allauth.socialaccount.providers.google` to INSTALLED_APPS (were missing — social login URLs didn't exist).
10. Installed `requests` package into venv (required by allauth Google provider).

## IMPORTANT discovery
- `/accounts/login/` serves **allauth's default** template (allauth urls included at `accounts/` BEFORE our app urls). Our custom templates live at root: `/login/`, `/signup/`, `/logout/` (see `apps/accounts/urls.py`). Nav links use `{% url 'accounts:login' %}` which correctly points to `/login/`. This is fine, but if we want `/accounts/login/` to also use our template, create `templates/account/login.html` overrides.
- PowerShell console mangles Kannada/emoji display (`?????`, `??`) — this is a console artifact, NOT a content problem. Actual HTML bytes are correct UTF-8.

## TODO (in order)
1. **Verify URL reversing works now** (after `requests` install):
   `python manage.py shell -c "from django.urls import reverse; print(reverse('google_login'))"`
   Should print `/accounts/google/login/`.
2. **Run migrations** for socialaccount tables: `python manage.py migrate` (socialaccount was just added to INSTALLED_APPS, so new tables exist).
3. **Restart dev server** (background shell `sh_102d56ab70018I64wqrWIR6cWq` timed out — runserver runs forever, that's expected; restart it) and verify:
   - `http://127.0.0.1:8000/` → 200
   - `http://127.0.0.1:8000/login/` → custom template with eye toggle
   - `http://127.0.0.1:8000/signup/` → custom template, Google button hidden (no creds)
   - `http://127.0.0.1:8000/lang/kn/?next=/` → UI in Kannada
4. **Google login**: to actually enable it, create OAuth 2.0 credentials at https://console.cloud.google.com/, then put them in `backend/.env`:
   ```
   GOOGLE_CLIENT_ID=...
   GOOGLE_CLIENT_SECRET=...
   ```
   Button appears automatically once both are set.
5. **Commit and push** everything to GitHub:
   ```
   cd C:\Users\pc\ricemandi
   git add -A
   git commit -m "Fix allauth errors, Kannada translations, password toggle, Google login"
   git push origin main
   ```

## Key files
- `backend/config/settings.py` — MIDDLEWARE, INSTALLED_APPS, allauth, SOCIALACCOUNT_PROVIDERS, LOCALE_PATHS
- `backend/config/urls.py` — URL include order (allauth at `accounts/`, custom apps at root)
- `backend/apps/core/context_processors.py` — unread_notifications + site_settings (google_login_enabled)
- `backend/apps/core/views.py` — set_language toggle, home
- `backend/apps/accounts/urls.py` — custom login/logout/signup at root
- `backend/apps/accounts/middleware.py` — LanguagePreferenceMiddleware
- `backend/templates/registration/login.html`, `signup.html` — password eye toggle
- `backend/locale/kn/LC_MESSAGES/django.po` + `django.mo` — 369 Kannada translations
- `backend/.env.example` — env var template

## Notes
- GNU gettext tools (msgfmt/msguniq) are NOT installed on this Windows machine — use `polib` to compile .po → .mo.
- PowerShell uses `;` not `&&` for command chaining.
- 1 packet = 26 kg (auto-calculated via signals).
