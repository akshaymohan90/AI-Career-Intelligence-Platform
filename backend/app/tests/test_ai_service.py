from app.services import ai_service


def test_generate_career_advice_returns_string():
    advice = ai_service.generate_career_advice(["python", "fastapi"], ["python", "sql", "api"])

    assert isinstance(advice, str)
    assert len(advice) > 0


def test_generate_career_advice_uses_groq_when_key_is_set(monkeypatch):
    class DummyMessage:
        def __init__(self, content: str):
            self.content = content

    class DummyChoice:
        def __init__(self, content: str):
            self.message = DummyMessage(content)

    class DummyResponse:
        def __init__(self, content: str):
            self.choices = [DummyChoice(content)]

    class DummyChat:
        def __init__(self):
            self.completions = self

        def create(self, **kwargs):
            return DummyResponse("Real Groq advice")

    class DummyGroq:
        def __init__(self, api_key):
            self.api_key = api_key
            self.chat = DummyChat()

    monkeypatch.setattr(ai_service, "GROQ_API_KEY", "test-key", raising=False)
    monkeypatch.setattr(ai_service, "Groq", DummyGroq, raising=False)

    advice = ai_service.generate_career_advice(["python"], ["python", "sql"])

    assert advice == "Real Groq advice"
