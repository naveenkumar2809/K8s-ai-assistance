import os

class Settings:
    PROJECT_NAME: str = "K8s AI Assistant"
    K8S_CONTEXT: str = os.getenv("K8S_CONTEXT", "docker-desktop")
    PROMETHEUS_URL: str = os.getenv("PROMETHEUS_URL", "http://localhost:9080")
    PROMETHEUS_USER: str = os.getenv("PROMETHEUS_USER", "admin")
    PROMETHEUS_PASSWORD: str = os.getenv("PROMETHEUS_PASSWORD", "1dO5v6LTpOxCj1fJAtnGbc0KoeiN3A8HbQgpde4c")
    ELASTICSEARCH_URL: str = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")
    # In a real app, we might want to check connectivity on startup

settings = Settings()
