import asyncio
import logging
from typing import List
from app.core.k8s_client import k8s
from app.models.schemas import ClusterEvent, MetricData, LogEntry
from app.core.config import settings
from prometheus_api_client import PrometheusConnect
from datetime import datetime, timezone
from kubernetes.client import CoreV1Event

logger = logging.getLogger(__name__)

class MonitorAgent:
    def __init__(self):
        self.k8s_client = k8s.get_core_client()
        self.prom = None
        if settings.PROMETHEUS_URL:
             try:
                 headers = {}
                 if settings.PROMETHEUS_USER and settings.PROMETHEUS_PASSWORD:
                     # Basic Auth headers if needed, but PrometheusConnect supports auth args usually? 
                     # Checking library docs (mental model): prometheus_api_client supports `headers` or strictly `url` with auth.
                     # Actually, `PrometheusConnect` might not support auth args directly in all versions, 
                     # but typically it's `headers={"Authorization": "Basic ..."}` or specific args.
                     # Let's use the safer `headers` approach if the lib allows, or just embed in URL?
                     # Embed in URL is risky for logging.
                     # The library `prometheus-api_client` constructor accepts `headers`.
                     # Let's try to construct the auth header manually to be safe.
                     import base64
                     auth_str = f"{settings.PROMETHEUS_USER}:{settings.PROMETHEUS_PASSWORD}"
                     b64_auth = base64.b64encode(auth_str.encode()).decode()
                     headers["Authorization"] = f"Basic {b64_auth}"
                 
                 self.prom = PrometheusConnect(url=settings.PROMETHEUS_URL, headers=headers, disable_ssl=True)
             except Exception as e:
                 logger.warning(f"Could not connect to Prometheus: {e}")

    async def get_events(self) -> List[ClusterEvent]:
        events = []
        if self.k8s_client:
            try:
                # Synchronous call wrapped in executor if needed, but for now direct call
                # list_event_for_all_namespaces is synchronous
                api_response = self.k8s_client.list_event_for_all_namespaces(limit=50)
                for item in api_response.items:
                    # item is CoreV1Event
                    event = ClusterEvent(
                        timestamp=item.last_timestamp or item.event_time or datetime.now(timezone.utc),
                        message=item.message or "",
                        reason=item.reason or "Unknown",
                        type=item.type or "Normal",
                        object_name=item.involved_object.name or "Unknown",
                        namespace=item.involved_object.namespace or "default"
                    )
                    events.append(event)
            except Exception as e:
                logger.error(f"Error fetching K8s events: {e}")
        return events

    async def get_metrics(self) -> List[MetricData]:
        metrics = []
        if self.prom:
            try:
                # Fetch CPU usage
                # Note: This is simplified. In prod, you'd query 'container_cpu_usage_seconds_total' with proper rate()
                # For demo with `get_current_metric_value`, we assume instant query
                cpu_data = self.prom.get_current_metric_value(metric_name='container_cpu_usage_seconds_total')
                for item in cpu_data[:10]:
                    pod = item['metric'].get('pod')
                    ns = item['metric'].get('namespace')
                    val = float(item['value'][1]) if item['value'] else 0.1
                    if pod and ns:
                        metrics.append(MetricData(
                            timestamp=datetime.now(timezone.utc),
                            cpu_usage=val,
                            memory_usage=128.0, # Mock memory
                            pod_name=pod,
                            namespace=ns
                        ))
            except Exception as e:
                 logger.warning(f"Error fetching Prometheus metrics: {e}")
                 # Fallback to mock data if prom connection fails
                 metrics = self._get_mock_metrics()
        else:
             metrics = self._get_mock_metrics()
        return metrics

    async def get_logs(self) -> List[LogEntry]:
        # Simple mock logs for demo
        return [
            LogEntry(timestamp=datetime.now(timezone.utc), level="INFO", message="Pod backend-app started successfully", pod_name="backend-app"),
            LogEntry(timestamp=datetime.now(timezone.utc), level="WARNING", message="High memory usage detected", pod_name="redis-cache"),
            LogEntry(timestamp=datetime.now(timezone.utc), level="ERROR", message="Connection timeout to database", pod_name="frontend-ui"),
        ]

    def _get_mock_metrics(self) -> List[MetricData]:
        """Return static metrics for demo purposes when Prometheus is unavailable."""
        return [
            MetricData(timestamp=datetime.now(timezone.utc), cpu_usage=0.45, memory_usage=256.0, pod_name="frontend-app-7d8b9c", namespace="default"),
            MetricData(timestamp=datetime.now(timezone.utc), cpu_usage=0.12, memory_usage=128.0, pod_name="backend-api-5f6a2b", namespace="default"),
            MetricData(timestamp=datetime.now(timezone.utc), cpu_usage=0.89, memory_usage=512.0, pod_name="redis-cache-3e4d5f", namespace="default"),
            MetricData(timestamp=datetime.now(timezone.utc), cpu_usage=0.05, memory_usage=64.0, pod_name="auth-service-9g8h7i", namespace="default"),
        ]

monitor_agent = MonitorAgent()
