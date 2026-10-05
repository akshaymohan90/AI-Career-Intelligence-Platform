import re

# name -> (aliases, estimated weeks to reach job-ready proficiency)
SKILL_TAXONOMY: dict[str, tuple[list[str], int]] = {
    "Python": (["python3", "python 3"], 6),
    "Java": ([], 8),
    "Go": (["golang"], 6),
    "JavaScript": (["js", "es6", "ecmascript"], 6),
    "TypeScript": (["ts"], 3),
    "C++": (["cpp"], 12),
    "Rust": ([], 12),
    "SQL": (["mysql", "sql server", "t-sql"], 4),
    "PostgreSQL": (["postgres"], 3),
    "MongoDB": (["mongo"], 2),
    "Redis": ([], 2),
    "Elasticsearch": (["elastic search"], 3),
    "Kafka": (["apache kafka"], 4),
    "RabbitMQ": (["rabbit mq"], 2),
    "Celery": ([], 2),
    "FastAPI": (["fast api"], 2),
    "Django": ([], 3),
    "Flask": ([], 2),
    "Spring Boot": (["spring", "springboot"], 6),
    "Node.js": (["node", "nodejs", "node js"], 3),
    "React": (["reactjs", "react.js"], 4),
    "Next.js": (["nextjs", "next js"], 2),
    "Angular": ([], 6),
    "Vue": (["vue.js", "vuejs"], 4),
    "REST APIs": (["rest api", "restful"], 2),
    "GraphQL": ([], 3),
    "gRPC": ([], 3),
    "Docker": ([], 2),
    "Kubernetes": (["k8s"], 8),
    "Terraform": ([], 4),
    "AWS": (["amazon web services"], 6),
    "Azure": ([], 6),
    "GCP": (["google cloud"], 6),
    "CI/CD": (["cicd", "github actions", "jenkins", "gitlab ci"], 2),
    "Linux": ([], 3),
    "Git": ([], 1),
    "Microservices": (["microservice"], 4),
    "System Design": (["distributed systems", "system architecture"], 12),
    "Data Structures & Algorithms": (["dsa", "data structures", "algorithms"], 12),
    "Machine Learning": (["ml", "machine-learning"], 12),
    "Deep Learning": (["dl"], 10),
    "PyTorch": ([], 4),
    "TensorFlow": ([], 4),
    "Scikit-learn": (["sklearn", "scikit learn"], 3),
    "Pandas": ([], 2),
    "NumPy": ([], 1),
    "Spark": (["apache spark", "pyspark"], 6),
    "Airflow": (["apache airflow"], 3),
    "LLMs": (["llm", "large language model"], 3),
    "RAG": (["retrieval augmented", "retrieval-augmented"], 2),
    "LangChain": ([], 2),
    "Pytest": (["unit testing", "unit tests"], 1),
    "Snowflake": ([], 3),
    "Tableau": ([], 2),
    "Power BI": (["powerbi"], 2),
}


def _pattern(term: str) -> re.Pattern:
    return re.compile(
        rf"(?<![A-Za-z0-9]){re.escape(term)}(?![A-Za-z0-9])",
        re.IGNORECASE,
    )


_COMPILED = {
    name: [_pattern(term) for term in [name, *aliases]]
    for name, (aliases, _) in SKILL_TAXONOMY.items()
}


def extract_taxonomy_skills(text: str) -> set[str]:
    return {
        name
        for name, patterns in _COMPILED.items()
        if any(p.search(text) for p in patterns)
    }


def estimated_weeks(skill: str) -> int:
    return SKILL_TAXONOMY[skill][1]
