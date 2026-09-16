from urllib.parse import urlparse


def company_base_url(source_url: str | None) -> str | None:
    if not source_url:
        return None

    parsed = urlparse(source_url)

    if parsed.scheme not in {"http", "https"}:
        return None

    if not parsed.netloc:
        return None

    return f"{parsed.scheme}://{parsed.netloc}"
