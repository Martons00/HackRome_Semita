import json
import re
from collections.abc import Sequence
from typing import Any, Optional

import torch
from pydantic import ValidationError
from transformers import AutoModelForCausalLM, AutoTokenizer

from .prompts import CAREER_PATH_ENGINE_SYSTEM_PROMPT
from .retrieval import RetrieverFn, build_retrieval_query, format_retrieved_context
from .schemas import CareerPathOutput, UserProfile

DEFAULT_LOCAL_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"


def _select_device() -> str:
    if torch.backends.mps.is_available():
        return "mps"
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"


def _extract_json_object(text: str) -> str:
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)

    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError(f"Model did not return a JSON object:\n{cleaned}")

    return cleaned[start : end + 1]


class LocalHuggingFaceCareerPathEngine:
    def __init__(
        self,
        model_id: str = DEFAULT_LOCAL_MODEL,
        retriever: Optional[RetrieverFn] = None,
        max_new_tokens: int = 1800,
        device: Optional[str] = None,
    ):
        self.model_id = model_id
        self.retriever = retriever
        self.max_new_tokens = max_new_tokens
        self.device = device or _select_device()

        dtype = torch.float16 if self.device in {"mps", "cuda"} else torch.float32
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_id,
            torch_dtype=dtype,
            low_cpu_mem_usage=True,
        )
        self.model.to(self.device)
        self.model.eval()

    def invoke(self, profile: UserProfile | dict[str, Any]) -> CareerPathOutput:
        user_profile = profile if isinstance(profile, UserProfile) else UserProfile(**profile)
        retrieved_context = "No external context provided."

        if self.retriever is not None:
            query = build_retrieval_query(user_profile)
            retrieved_context = format_retrieved_context(self.retriever(query))

        prompt = self._build_prompt(user_profile, retrieved_context)
        raw_output = self._generate(prompt)
        json_text = _extract_json_object(raw_output)

        try:
            return CareerPathOutput.model_validate_json(json_text)
        except ValidationError as exc:
            parsed = json.loads(json_text)
            raise ValueError(f"Model JSON did not match CareerPathOutput schema: {exc}") from exc

    def _build_prompt(self, profile: UserProfile, retrieved_context: str) -> str:
        schema = CareerPathOutput.model_json_schema()
        user_message = f"""
UserProfile:
{profile.model_dump_json(indent=2)}

Retrieved context:
{retrieved_context}

Return ONLY one valid JSON object matching this JSON Schema:
{json.dumps(schema, indent=2)}

Required fit_breakdown keys:
- fit_psychometric
- fit_skills
- fit_market
- fit_constraints
"""
        messages: Sequence[dict[str, str]] = [
            {"role": "system", "content": CAREER_PATH_ENGINE_SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ]

        if self.tokenizer.chat_template:
            return self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
            )

        return (
            f"System:\n{CAREER_PATH_ENGINE_SYSTEM_PROMPT}\n\n"
            f"User:\n{user_message}\n\nAssistant:\n"
        )

    def _generate(self, prompt: str) -> str:
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        prompt_tokens = inputs["input_ids"].shape[-1]

        with torch.no_grad():
            output_ids = self.model.generate(
                **inputs,
                max_new_tokens=self.max_new_tokens,
                do_sample=False,
                pad_token_id=self.tokenizer.eos_token_id,
            )

        generated_ids = output_ids[0][prompt_tokens:]
        return self.tokenizer.decode(generated_ids, skip_special_tokens=True)
