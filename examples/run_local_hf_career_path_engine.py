import json
import os

from career_path_engine import (
    DEFAULT_LOCAL_MODEL,
    EscoApiClient,
    EscoRoleSkillRetriever,
    LocalHuggingFaceCareerPathEngine,
    UserProfile,
)


example_user = UserProfile(
    cv_text="""
Junior AI/ML engineer and researcher based in Rome.
Completed a bachelor's degree in Environmental Engineering in 2024 and is finishing a master's in Computer Engineering / AI & Data Analytics.
Has research experience in medical imaging and 3D organoid classification at INRIA.
Strong Python and PyTorch background, familiar with computer vision, data analysis, Linux, Git, and technical writing.
Also has SDR experience at Factorial, so communication and business exposure are strong.
""",
    skills=[
        "Python",
        "PyTorch",
        "Computer Vision",
        "Data Analysis",
        "Linux",
        "Git",
        "SQL",
        "Technical Writing",
        "Research",
        "Communication",
    ],
    experience_years=1.5,
    education_level="Master's student",
    target_role="Junior Computer Vision Engineer",
    target_industry="Healthcare / Medical AI",
    location="Rome, Italy",
    remote_ok=True,
    relocation="EU_only",
    budget_eur=1500,
    hours_per_week=10,
    psychometric_profile={
        "RIASEC_I": 0.92,
        "RIASEC_A": 0.78,
        "RIASEC_S": 0.55,
        "RIASEC_R": 0.30,
        "RIASEC_E": 0.40,
        "RIASEC_C": 0.70,
        "value_achievement": 0.88,
        "value_independence": 0.84,
        "value_relationships": 0.60,
        "workstyle_analytical_thinking": 0.93,
        "workstyle_stress_tolerance": 0.72,
        "personality_openness": 0.89,
        "personality_conscientiousness": 0.76,
    },
)


def main():
    model_id = os.getenv("HF_MODEL_ID", DEFAULT_LOCAL_MODEL)
    esco_language = os.getenv("ESCO_LANGUAGE", "en")
    retriever = EscoRoleSkillRetriever(
        client=EscoApiClient(language=esco_language),
        occupation_limit=3,
        skill_limit=8,
    )
    engine = LocalHuggingFaceCareerPathEngine(
        model_id=model_id,
        retriever=retriever,
        max_new_tokens=1800,
    )
    output = engine.invoke(example_user)
    print(json.dumps(output.model_dump(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
