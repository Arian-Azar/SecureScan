from django.core import signing
from user_agents import parse as parse_user_agent

EMAIL_VERIFICATION_SALT = 'accounts.email-verification'
EMAIL_VERIFICATION_MAX_AGE = 60 * 60 * 24  # 24 hours


def generate_email_verification_token(user):
    """
    Encodes the user's pk into a signed, self-verifying token. No database
    row is needed to "look up" this token later — signing.loads() below
    both verifies the signature AND checks the 24h expiry in one call.
    """
    return signing.dumps({'user_id': user.pk}, salt=EMAIL_VERIFICATION_SALT)


def read_email_verification_token(token):
    """Returns the encoded user_id, or None if the token is invalid/expired."""
    try:
        data = signing.loads(
            token,
            salt=EMAIL_VERIFICATION_SALT,
            max_age=EMAIL_VERIFICATION_MAX_AGE,
        )
    except signing.BadSignature:
        return None
    return data.get('user_id')


def get_client_ip(request):
    """
    Prefers X-Forwarded-For (set by a reverse proxy / load balancer in
    front of the app — the scenario this project WILL be deployed behind,
    per Phase 7's Nginx/Docker plan) and falls back to REMOTE_ADDR for
    direct connections (e.g. local development).
    """
    forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded_for:
        # X-Forwarded-For can be a comma-separated chain of proxies; the
        # first entry is the original client.
        return forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def parse_client_user_agent(request):
    """Returns (browser, device, os) strings parsed from the request's UA header."""
    ua_string = request.META.get('HTTP_USER_AGENT', '')
    ua = parse_user_agent(ua_string)
    return ua.browser.family, ua.device.family, ua.os.family
