from collections.abc import Callable, Sequence
from typing import Any, Optional

from langchain_core.documents import Document
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate

from .prompts import CAREER_PATH_ENGINE_SYSTEM_PROMPT, CAREER_PATH_ENGINE_USER_PROMPT
from .schemas import CareerPathOutput, UserProfile

RetrieverFn = Callable[[str], Sequence[Document] | Sequence[str]]


def _format_retrieved_context(items: Sequence[Document] | Sequence[str]) -> str:
    if not items:
        return "No external context provided."

    chunks: list[str] = []
    for item in items:
        if isinstance(item, Document):
            source = item.metadata.get("source")
            prefix = f"Source: {source}\n" if source else ""
            chunks.append(f"{prefix}{item.page_content}")
        else:
            chunks.append(str(item))

    return "\n\n---\n\n".join(chunks)


def _build_retrieval_query(profile: UserProfile) -> str:
    parts = [
        profile.target_role,
        profile.target_industry or "",
        profile.location or "",
        "required skills courses certifications job descriptions career path",
    ]
    return " ".join(part for part in parts if part).strip()


def build_career_path_chain(llm: BaseChatModel):
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", CAREER_PATH_ENGINE_SYSTEM_PROMPT),
            ("user", CAREER_PATH_ENGINE_USER_PROMPT),
        ]
    )
    return prompt | llm.with_structured_output(CareerPathOutput)


class CareerPathEngine:
    def __init__(self, llm: BaseChatModel, retriever: Optional[RetrieverFn] = None):
        self.chain = build_career_path_chain(llm)
        self.retriever = retriever

    def invoke(self, profile: UserProfile | dict[str, Any]) -> CareerPathOutput:
        user_profile = profile if isinstance(profile, UserProfile) else UserProfile(**profile)
        retrieved_context = "No external context provided."

        if self.retriever is not None:
            query = _build_retrieval_query(user_profile)
            retrieved_context = _format_retrieved_context(self.retriever(query))

        return self.chain.invoke(
            {
                "profile": user_profile.model_dump_json(indent=2),
                "retrieved_context": retrieved_context,
            }
        )
