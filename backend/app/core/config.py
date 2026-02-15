import os

class Settings:
    PROJECT_NAME: str = "K8s AI Assistant"
    K8S_CONTEXT: str = os.getenv("K8S_CONTEXT", "docker-desktop")
    PROMETHEUS_URL: str = os.getenv("PROMETHEUS_URL", "http://localhost:9080")
    PROMETHEUS_USER: str = os.getenv("PROMETHEUS_USER", "admin")
    PROMETHEUS_PASSWORD: str = os.getenv("PROMETHEUS_PASSWORD", "1dO5v6LTpOxCj1fJAtnGbc0KoeiN3A8HbQgpde4c")
    ELASTICSEARCH_URL: str = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")
    
    # GPT-5 Nano LLM Configuration
    GPT_API_KEY: str = os.getenv("GPT_API_KEY", "euri-94cdcc6563a978b4319b0ba3d4c6582edf5394006ce71c2b88545920bc699f2c")
    GPT_MODEL: str = os.getenv("GPT_MODEL", "gpt-5-nano")
    GPT_API_URL: str = os.getenv("GPT_API_URL", "https://api.openai.com/v1/chat/completions")
    # In a real app, we might want to check connectivity on startup

settings = Settings()
