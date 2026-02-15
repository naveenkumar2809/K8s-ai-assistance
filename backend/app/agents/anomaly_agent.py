from typing import List
from app.models.schemas import ClusterEvent, MetricData, LogEntry
import logging

logger = logging.getLogger(__name__)

class AnomalyAgent:
    def detect_anomalies(self, events: List[ClusterEvent], metrics: List[MetricData], logs: List[LogEntry]) -> List[dict]:
        anomalies = []
        
        # 1. Event Anomalies
        for event in events:
            if event.type == "Warning":
                anomalies.append({
                    "type": "event_warning",
                    "resource": event.object_name,
                    "namespace": event.namespace,
                    "message": event.message,
                    "severity": "warning"
                })

        # 2. Metric Anomalies (Simple Threshold)
        for metric in metrics:
            if metric.cpu_usage > 0.8: # Example: 80% CPU is "high" in this mock logic (normalized 0-1 or cores?)
                # Prometheus usually returns cpu seconds. We need rate. 
                # Assuming the query in monitor_agent returns something meaningful or we interpret it here.
                # For this demo, let's assume raw value > threshold is bad just to show flow.
                anomalies.append({
                    "type": "high_cpu",
                    "resource": metric.pod_name,
                    "namespace": metric.namespace,
                    "message": f"High CPU usage: {metric.cpu_usage}",
                    "severity": "critical"
                })

        return anomalies

anomaly_agent = AnomalyAgent()
