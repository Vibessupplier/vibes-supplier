"""Stable internal keys for Streamlit bidirectional components."""

import hashlib
import re
from typing import Any


def safe_component_key(prefix: str, *identity_parts: Any) -> str:
    """Return a deterministic component key without Streamlit's reserved `__`."""
    safe_prefix = re.sub(r"[^a-zA-Z0-9-]+", "-", str(prefix)).strip("-")
    if not safe_prefix:
        safe_prefix = "component"
    identity = "\x1f".join(str(part) for part in identity_parts)
    digest = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:20]
    return f"{safe_prefix}-{digest}"
