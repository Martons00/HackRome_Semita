from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, Optional

import requests

ESCO_API_BASE_URL = "https://ec.europa.eu/esco/api"


def _label(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        for key in ("literal", "value", "label", "en"):
            item = value.get(key)
            if isinstance(item, str):
                return item
        for item in value.values():
            if isinstance(item, str):
                return item
            if isinstance(item, list) and item and isinstance(item[0], str):
                return item[0]
    if isinstance(value, list) and value:
        return _label(value[0])
    return ""


def _description(value: Any) -> str:
    if isinstance(value, dict):
        for key in ("en", "literal", "value", "description"):
            item = value.get(key)
            if isinstance(item, str):
                return item
    if isinstance(value, str):
        return value
    return ""


def _embedded_items(payload: dict[str, Any]) -> list[dict[str, Any]]:
    embedded = payload.get("_embedded", {})
    if not isinstance(embedded, dict):
        return []

    items: list[dict[str, Any]] = []
    for value in embedded.values():
        if isinstance(value, list):
            items.extend(item for item in value if isinstance(item, dict))
        elif isinstance(value, dict):
            items.append(value)
    return items


def _resource_uri(item: dict[str, Any]) -> str:
    uri = item.get("uri")
    if isinstance(uri, str):
        return uri

    links = item.get("_links", {})
    if isinstance(links, dict):
        self_link = links.get("self", {})
        if isinstance(self_link, dict):
            href = self_link.get("href")
            if isinstance(href, str):
                return href

    return ""


def _resource_title(item: dict[str, Any]) -> str:
    for key in ("title", "preferredLabel", "prefLabel"):
        value = _label(item.get(key))
        if value:
            return value
    return ""


def _skill_relation_items(occupation: dict[str, Any]) -> list[dict[str, Any]]:
    skills: list[dict[str, Any]] = []
    for key, value in occupation.items():
        normalized = key.lower()
        if "skill" not in normalized:
            continue
        if isinstance(value, list):
            skills.extend(item for item in value if isinstance(item, dict))
        elif isinstance(value, dict):
            skills.append(value)
    return skills


@dataclass
class EscoApiClient:
    base_url: str = ESCO_API_BASE_URL
    language: str = "en"
    selected_version: str = "latest"
    timeout_seconds: int = 20

    def search(
        self,
        text: str,
        resource_type: Optional[Literal["occupation", "skill"]] = None,
        limit: int = 5,
        full: bool = True,
    ) -> list[dict[str, Any]]:
        params: dict[str, Any] = {
            "text": text,
            "language": self.language,
            "limit": limit,
            "offset": 0,
            "full": str(full).lower(),
            "selectedVersion": self.selected_version,
            "viewObsolete": "false",
        }
        if resource_type:
            params["type"] = resource_type

        payload = self._get_json("/search", params)
        return _embedded_items(payload)

    def get_occupation(self, uri: str) -> dict[str, Any]:
        return self._get_json(
            "/resource/occupation",
            {
                "uri": uri,
                "language": self.language,
                "selectedVersion": self.selected_version,
            },
        )

    def get_skill(self, uri: str) -> dict[str, Any]:
        return self._get_json(
            "/resource/skill",
            {
                "uri": uri,
                "language": self.language,
                "selectedVersion": self.selected_version,
            },
        )

    def get_concepts_by_scheme(
        self,
        is_in_scheme: str,
        limit: int = 20,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        payload = self._get_json(
            "/resource/concept",
            {
                "isInScheme": is_in_scheme,
                "language": self.language,
                "offset": offset,
                "limit": limit,
                "selectedVersion": self.selected_version,
                "viewObsolete": "false",
            },
        )
        return _embedded_items(payload)

    def _get_json(self, path: str, params: dict[str, Any]) -> dict[str, Any]:
        response = requests.get(
            f"{self.base_url}{path}",
            params=params,
            headers={
                "Accept": "application/json, application/json;charset=UTF-8",
                "Accept-Language": self.language,
            },
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        return response.json()


class EscoRoleSkillRetriever:
    def __init__(
        self,
        client: Optional[EscoApiClient] = None,
        occupation_limit: int = 3,
        skill_limit: int = 8,
    ):
        self.client = client or EscoApiClient()
        self.occupation_limit = occupation_limit
        self.skill_limit = skill_limit

    def __call__(self, query: str) -> list[str]:
        try:
            occupations = self.client.search(
                query,
                resource_type="occupation",
                limit=self.occupation_limit,
                full=True,
            )
            skills = self.client.search(
                query,
                resource_type="skill",
                limit=self.skill_limit,
                full=True,
            )
        except requests.RequestException as exc:
            return [f"ESCO context unavailable: {exc}"]

        context: list[str] = []
        context.extend(self._format_occupation(item) for item in occupations)
        context.extend(self._format_skill(item) for item in skills)
        return [item for item in context if item.strip()]

    def _format_occupation(self, item: dict[str, Any]) -> str:
        uri = _resource_uri(item)
        detail = item
        if uri:
            try:
                detail = self.client.get_occupation(uri)
            except requests.RequestException:
                detail = item

        title = _resource_title(detail) or _resource_title(item)
        description = _description(detail.get("description")) or _description(item.get("description"))
        skill_labels = [
            _resource_title(skill) or _label(skill.get("preferredLabel"))
            for skill in _skill_relation_items(detail)
        ]
        skill_labels = [skill for skill in skill_labels if skill]

        lines = [
            "ESCO occupation",
            f"Title: {title}" if title else "",
            f"URI: {uri}" if uri else "",
            f"Definition: {description}" if description else "",
        ]
        if skill_labels:
            lines.append("Related skills: " + ", ".join(skill_labels[: self.skill_limit]))

        return "\n".join(line for line in lines if line)

    def _format_skill(self, item: dict[str, Any]) -> str:
        uri = _resource_uri(item)
        detail = item
        if uri:
            try:
                detail = self.client.get_skill(uri)
            except requests.RequestException:
                detail = item

        title = _resource_title(detail) or _resource_title(item)
        description = _description(detail.get("description")) or _description(item.get("description"))
        lines = [
            "ESCO skill",
            f"Title: {title}" if title else "",
            f"URI: {uri}" if uri else "",
            f"Definition: {description}" if description else "",
        ]
        return "\n".join(line for line in lines if line)
