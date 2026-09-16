import re


def detect_work_mode(description: str) -> str | None:
    text = (description or "").lower()

    remote_patterns = [
        r"\bfully remote\b",
        r"\bremote[- ]first\b",
        r"\bremote position\b",
        r"\bwork remotely\b",
        r"\bremote role\b",
        r"\bremote work\b",
    ]

    hybrid_patterns = [
        r"\bhybrid\b",
        r"\bhybrid role\b",
        r"\bhybrid work\b",
        r"\bflexible hybrid\b",
    ]

    onsite_patterns = [
        r"\bon[- ]site\b",
        r"\bonsite\b",
        r"\bin[- ]office\b",
        r"\boffice[- ]based\b",
    ]

    if any(re.search(pattern, text) for pattern in remote_patterns):
        return "remote"

    if any(re.search(pattern, text) for pattern in hybrid_patterns):
        return "hybrid"

    if any(re.search(pattern, text) for pattern in onsite_patterns):
        return "on-site"

    return None
