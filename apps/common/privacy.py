AGENT_ROLES = {"agente", "supervisor", "admin"}


def request_is_agent(request) -> bool:
    user = getattr(request, "user", None)
    return bool(
        user
        and getattr(user, "is_authenticated", False)
        and getattr(user, "rol", None) in AGENT_ROLES
    )


def mask_identifier(value: str) -> str:
    raw = (value or "").strip()
    if len(raw) <= 4:
        return "****"
    return f"{'*' * (len(raw) - 4)}{raw[-4:]}"


def mask_email(value: str) -> str:
    raw = (value or "").strip()
    local, sep, domain = raw.partition("@")
    if not sep or not domain:
        return "***"
    keep = local[:1] if local else "*"
    return f"{keep}***@{domain}"


def mask_phone(value: str) -> str:
    raw = (value or "").strip()
    if not raw:
        return ""
    if len(raw) <= 2:
        return "*" * len(raw)
    return f"{'*' * (len(raw) - 2)}{raw[-2:]}"
