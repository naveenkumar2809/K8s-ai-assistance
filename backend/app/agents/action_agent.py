import logging
from app.models.schemas import Recommendation, RecommendationType, ResourceType
from app.core.k8s_client import k8s
from kubernetes.client.rest import ApiException

logger = logging.getLogger(__name__)

class ActionAgent:
    def __init__(self):
        self.k8s_apps = k8s.get_apps_client()
        self.k8s_core = k8s.get_core_client()

    async def execute_action(self, recommendation: Recommendation) -> bool:
        logger.info(f"Executing action for recommendation: {recommendation.id} - {recommendation.recommendation_type}")
        
        try:
            if recommendation.recommendation_type == RecommendationType.SCALE_UP:
                return await self._scale_deployment(recommendation.namespace, recommendation.resource_name, 1) # Increment by 1
            elif recommendation.recommendation_type == RecommendationType.SCALE_DOWN:
                return await self._scale_deployment(recommendation.namespace, recommendation.resource_name, -1)
            elif recommendation.recommendation_type == RecommendationType.RESTART_POD:
                return await self._delete_pod(recommendation.namespace, recommendation.resource_name)
            else:
                logger.warning(f"Unsupported action type: {recommendation.recommendation_type}")
                return False
        except Exception as e:
            logger.error(f"Failed to execute action: {e}")
            return False

    async def _scale_deployment(self, namespace: str, name: str, replica_change: int) -> bool:
        if not self.k8s_apps:
            logger.error("K8s Apps Client not available")
            return False

        try:
            # Get current scale
            scale = self.k8s_apps.read_namespaced_deployment_scale(name, namespace)
            current_replicas = scale.spec.replicas
            new_replicas = current_replicas + replica_change
            
            # Simple patch
            patch = {"spec": {"replicas": new_replicas}}
            self.k8s_apps.patch_namespaced_deployment_scale(name, namespace, patch)
            logger.info(f"Scaled deployment {name} in {namespace} to {new_replicas}")
            return True
        except ApiException as e:
            logger.error(f"K8s API Error scaling deployment: {e}")
            return False

    async def _delete_pod(self, namespace: str, name: str) -> bool:
        if not self.k8s_core:
            logger.error("K8s Core Client not available")
            return False
        
        try:
            self.k8s_core.delete_namespaced_pod(name, namespace)
            logger.info(f"Deleted pod {name} in {namespace} (triggers restart if controlled)")
            return True
        except ApiException as e:
             logger.error(f"K8s API Error deleting pod: {e}")
             return False

action_agent = ActionAgent()
