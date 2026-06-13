from .schemas import CareerPathOutput, UserProfile

DEFAULT_LOCAL_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"
ESCO_API_BASE_URL = "https://ec.europa.eu/esco/api"

__all__ = [
    "DEFAULT_LOCAL_MODEL",
    "ESCO_API_BASE_URL",
    "CareerPathEngine",
    "CareerPathOutput",
    "EscoApiClient",
    "EscoRoleSkillRetriever",
    "LocalHuggingFaceCareerPathEngine",
    "UserProfile",
    "build_career_path_chain",
]


def __getattr__(name):
    if name in {"EscoApiClient", "EscoRoleSkillRetriever"}:
        from .esco import EscoApiClient, EscoRoleSkillRetriever

        exports = {
            "EscoApiClient": EscoApiClient,
            "EscoRoleSkillRetriever": EscoRoleSkillRetriever,
        }
        return exports[name]
    if name in {"CareerPathEngine", "build_career_path_chain"}:
        from .chain import CareerPathEngine, build_career_path_chain

        exports = {
            "CareerPathEngine": CareerPathEngine,
            "build_career_path_chain": build_career_path_chain,
        }
        return exports[name]
    if name == "LocalHuggingFaceCareerPathEngine":
        from .local_hf import LocalHuggingFaceCareerPathEngine

        return LocalHuggingFaceCareerPathEngine
    raise AttributeError(f"module 'career_path_engine' has no attribute {name!r}")
