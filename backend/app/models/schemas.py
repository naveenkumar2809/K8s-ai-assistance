from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum

class Severity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

class ResourceType(str, Enum):
    POD = "Pod"
    NODE = "Node"
    DEPLOYMENT = "Deployment"
    SERVICE = "Service"
    OTHER = "Other"

class ClusterEvent(BaseModel):
    timestamp: datetime
    message: str
    reason: str
    type: str  # Normal, Warning
    object_name: str
    namespace: str

class MetricData(BaseModel):
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    pod_name: str
    namespace: str

class LogEntry(BaseModel):
    timestamp: datetime
    message: str
    level: str
    pod_name: str

class RecommendationType(str, Enum):
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    RESTART_POD = "restart_pod"
    INCREASE_LIMITS = "increase_limits"
    OPTIMIZE_IMAGES = "optimize_images"

class Recommendation(BaseModel):
    id: str
    timestamp: datetime
    resource_name: str
    resource_type: ResourceType
    namespace: str
    severity: Severity
    message: str
    recommendation_type: RecommendationType
    suggested_action: str
    status: str = "pending"  # pending, applied, discarded

class ActionRequest(BaseModel):
    recommendation_id: str
    approve: bool

class ClusterStatus(BaseModel):
    node_count: int
    pod_count: int
    unhealthy_pods: int
    cpu_total_usage: float
    memory_total_usage: float
    events: List[ClusterEvent] = []
    active_recommendations: List[Recommendation] = []
