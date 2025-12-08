# Django modules
from django.core.exceptions import ValidationError

_RESTRICTED_DOMAINS = (
    "example.com",
    "test.com",
    "gmail.com",
    "mail.ru",
    "kbtu.kz",
    "yandex.ru",
    "yahoo.com",
    "gmail.com",
    "hotmail.com",
    "aol.com",
    "outlook.com",
    "icloud.com",
    "protonmail.com",
    "zoho.com",
    "gmx.com",
    "yahoo.co.uk",
    "live.com",
    "me.com",
    "msn.com",
    "comcast.net",
    "att.net",
    "bellsouth.net",
    "cox.net",
    "verizon.net",
    "earthlink.net",
)


def validate_email_domain(value: str) -> None:
    """
    Validate that the email address belongs to a specific domain.
    """
    domain: str = value.split('@')[-1]
    if domain not in _RESTRICTED_DOMAINS:
        raise ValidationError(
            message=f"Registration using \"{domain}\" is not allowed.",
            code="invalid_domain",
        )


def validate_password(value: str) -> None:
    """
    Validate that the password meets certain criteria.
    """
    min_length: int = 8

    if len(value) < min_length:
        raise ValidationError(
            message=f"Password must be at least {min_length} characters long.",
            code="password_too_short",
        )
    if not any(char.isdigit() for char in value):
        raise ValidationError(
            message="Password must contain at least one digit.",
            code="password_no_digit",
        )
    if not any(char.isupper() for char in value):
        raise ValidationError(
            message="Password must contain at least one uppercase letter.",
            code="password_no_upper",
        )
