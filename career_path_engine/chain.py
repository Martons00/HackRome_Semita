from typing import Any, Optional

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate

from .prompts import CAREER_PATH_ENGINE_SYSTEM_PROMPT, CAREER_PATH_ENGINE_USER_PROMPT
from .retrieval import RetrieverFn, build_retrieval_query, format_retrieved_context
from .schemas import CareerPathOutput, UserProfile


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
            query = build_retrieval_query(user_profile)
            retrieved_context = format_retrieved_context(self.retriever(query))

        return self.chain.invoke(
            {
                "profile": user_profile.model_dump_json(indent=2),
                "retrieved_context": retrieved_context,
            }
        )
