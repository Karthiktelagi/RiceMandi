from django.utils import translation


class LanguagePreferenceMiddleware:
    """Honour the signed-in user's stored language preference.

    Django's own ``LocaleMiddleware`` reads the language from the URL path,
    a cookie, and the ``Accept-Language`` header — but **not** from the
    session. Our ``/lang/<code>/`` toggle writes to the session, so without
    this middleware the choice would be lost on the next request.

    For authenticated users we read ``preferred_language`` from the user
    record. For anonymous users we read ``django_language`` from the session
    (set by the language toggle). A merchant who set Kannada once should not
    have to pick it again on every device.

    Ordering matters: this must come *after* ``AuthenticationMiddleware``,
    otherwise ``request.user`` is still anonymous and there is no preference to
    find.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)
        preferred = getattr(user, "preferred_language", "") or ""

        if preferred and preferred in ("kn", "en"):
            translation.activate(preferred)
            request.session["django_language"] = preferred
            request.LANGUAGE_CODE = preferred
        else:
            # Anonymous user — check the session for a language toggle choice
            session_lang = request.session.get("django_language", "")
            if session_lang in ("kn", "en"):
                translation.activate(session_lang)
                request.LANGUAGE_CODE = session_lang

        return self.get_response(request)
