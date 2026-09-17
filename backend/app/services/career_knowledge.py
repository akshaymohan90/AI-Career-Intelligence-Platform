from app.services.vector_store import add_document


CAREER_KNOWLEDGE = [
    {
        "id": "docker_1",
        "text": """
        Docker is an important skill for backend and machine learning
        engineers. Beginners should learn containers, Dockerfiles,
        images, containers, volumes, networking and Docker Compose.
        A practical project should containerize a FastAPI application
        with PostgreSQL.
        """,
        "skill": "docker"
    },
    {
        "id": "fastapi_1",
        "text": """
        FastAPI is a Python framework for building APIs.
        Important topics include routing, dependency injection,
        Pydantic schemas, authentication, database integration,
        middleware and API testing.
        A practical project should build a production-style REST API.
        """,
        "skill": "fastapi"
    },
    {
        "id": "python_1",
        "text": """
        Python is widely used in backend development, automation,
        data science and machine learning. Important areas include
        functions, classes, modules, error handling, virtual
        environments, testing and package management.
        """,
        "skill": "python"
    },
    {
        "id": "machine_learning_1",
        "text": """
        Machine learning fundamentals include supervised learning,
        unsupervised learning, feature engineering, model evaluation,
        classification, regression and model deployment.
        """,
        "skill": "machine learning"
    },
    {
        "id": "sql_1",
        "text": """
        SQL skills include SELECT queries, joins, aggregation,
        subqueries, indexes, transactions and database design.
        PostgreSQL is a useful database for practical backend projects.
        """,
        "skill": "sql"
    }
]


def load_career_knowledge():

    for item in CAREER_KNOWLEDGE:

        add_document(
            document_id=item["id"],
            text=item["text"],
            metadata={
                "skill": item["skill"]
            }
        )