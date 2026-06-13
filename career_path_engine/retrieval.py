from collections.abc import Callable, Sequence
from typing import Any

from .schemas import UserProfile

RetrieverFn = Callable[[str], Sequence[Any]]


def format_retrieved_context(items: Sequence[Any]) -> str:
    if not items:
        return "No external context provided."

    chunks: list[str] = []
    for item in items:
        page_content = getattr(item, "page_content", None)
        metadata = getattr(item, "metadata", {})
        if isinstance(page_content, str):
            source = metadata.get("source") if isinstance(metadata, dict) else None
            prefix = f"Source: {source}\n" if source else ""
            chunks.append(f"{prefix}{page_content}")
        else:
            chunks.append(str(item))

    return "\n\n---\n\n".join(chunks)


def build_retrieval_query(profile: UserProfile) -> str:
    parts = [
        profile.target_role,
        profile.target_industry or "",
        profile.location or "",
        "required skills courses certifications job descriptions career path",
    ]
    return " ".join(part for part in parts if part).strip()
