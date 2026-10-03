from django.utils import translation


class LanguagePreferenceMiddleware:
    """Honour the signed-in user's stored language preference.

    Django's own ``LocaleMiddleware`` reads ``LANGUAGE_CODE``, the session and
    ``Accept-Language``, in that order. A merchant who set Kannada once should
    not have to pick it again on every device, so once authentication has run we
    force the language stored on the user record.

    Ordering matters: this must come *after* ``AuthenticationMiddleware``,
    otherwise ``request.user`` is still anonymous and there is no preference to
    find. The ``/lang/<code>/`` toggle writes the session, which LocaleMiddleware
    reads first, so a manual toggle still wins for the rest of that session.
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

        return self.get_response(request)
