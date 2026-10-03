from urllib.parse import urlparse


def safe_redirect(target, fallback):
    """Return ``target`` if it is a safe in-site path, else ``fallback``.

    Guards the ``?next=`` parameter used by the language toggle and the login
    page against open-redirect attacks. Only site-relative paths are allowed.

    Rejected: absolute URLs (``https://evil.example``), protocol-relative URLs
    (``//evil.example``) and backslash tricks (``/\\evil.example``), which some
    browsers normalise into ``//evil.example``.
    """
    if not target:
        return fallback

    if "\\" in target:
        return fallback

    # A single leading slash means "same site". Two means "some other host".
    if not target.startswith("/") or target.startswith("//"):
        return fallback

    # Belt and braces: reject anything that still parses with a host or scheme.
    parsed = urlparse(target)
    if parsed.scheme or parsed.netloc:
        return fallback

    return target
