from kubernetes import client, config
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class K8sClient:
    def __init__(self):
        try:
            # Load the kube config from default location or KUBECONFIG env var
            config.load_kube_config(context=settings.K8S_CONTEXT)
            self.v1 = client.CoreV1Api()
            self.apps_v1 = client.AppsV1Api()
            logger.info(f"Connected to Kubernetes cluster with context: {settings.K8S_CONTEXT}")
        except config.ConfigException:
            logger.warning("Could not load kube config. Running in offline mode?")
            self.v1 = None
            self.apps_v1 = None
        except Exception as e:
            logger.error(f"Error initializing Kubernetes client: {e}")
            self.v1 = None
            self.apps_v1 = None

    def get_core_client(self):
        return self.v1

    def get_apps_client(self):
        return self.apps_v1

k8s = K8sClient()
