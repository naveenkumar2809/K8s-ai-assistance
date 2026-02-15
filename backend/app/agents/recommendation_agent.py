from typing import List
from app.models.schemas import Recommendation, RecommendationType, Severity, ResourceType
from datetime import datetime
import uuid

class RecommendationAgent:
    def generate_recommendations(self, anomalies: List[dict]) -> List[Recommendation]:
        recommendations = []
        for anomaly in anomalies:
            rec_id = str(uuid.uuid4())
            if anomaly["type"] == "high_cpu":
                rec = Recommendation(
                    id=rec_id,
                    timestamp=datetime.now(),
                    resource_name=anomaly["resource"],
                    resource_type=ResourceType.POD,
                    namespace=anomaly["namespace"],
                    severity=Severity.CRITICAL,
                    message=f"Pod {anomaly['resource']} is experiencing high CPU usage.",
                    recommendation_type=RecommendationType.SCALE_UP,
                    suggested_action=f"Scale up deployment for pod {anomaly['resource']} or increase CPU limits.",
                    status="pending"
                )
                recommendations.append(rec)
            elif anomaly["type"] == "event_warning":
                rec = Recommendation(
                    id=rec_id,
                    timestamp=datetime.now(),
                    resource_name=anomaly["resource"],
                    resource_type=ResourceType.POD, # Assumption
                    namespace=anomaly["namespace"],
                    severity=Severity.WARNING,
                    message=f"Warning event: {anomaly['message']}",
                    recommendation_type=RecommendationType.RESTART_POD, # Generic suggestion
                    suggested_action=f"Check logs for {anomaly['resource']} and consider restarting.",
                    status="pending"
                )
                recommendations.append(rec)
        return recommendations

recommendation_agent = RecommendationAgent()
