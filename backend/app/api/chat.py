from fastapi import APIRouter
from pydantic import BaseModel
from app.agents.monitor_agent import monitor_agent
from app.agents.anomaly_agent import anomaly_agent
from app.agents.recommendation_agent import recommendation_agent
# Import global store from endpoints to access active recommendations state
# A better architecture would be a shared state manager, but for now we'll import from endpoints or re-generate
# Ideally, agents should be stateless services and data passed in, or agents hold state.
# Let's rely on re-fetching from monitor_agent which is caching/fetching live.
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

class SmartChatAgent:
    async def process_message(self, message: str) -> str:
        msg = message.lower()
        
        # 1. Fetch Context
        events = await monitor_agent.get_events()
        metrics = await monitor_agent.get_metrics()
        logs = await monitor_agent.get_logs() # Empty for now
        
        # Run analysis (quick re-run to get current anomalies)
        anomalies = anomaly_agent.detect_anomalies(events, metrics, logs)
        recommendations = recommendation_agent.generate_recommendations(anomalies)

        # 2. Intent Recognition & Response Generation
        if any(w in msg for w in ["status", "health", "overview", "cluster"]):
            return self._generate_status_response(metrics, anomalies, events)
        
        elif any(w in msg for w in ["recommend", "suggestion", "optimize", "advice"]):
            return self._generate_recommendation_response(recommendations)
        
        elif any(w in msg for w in ["error", "fail", "crash", "bug", "issue", "problem"]):
            return self._generate_anomaly_response(anomalies)

        elif any(w in msg for w in ["cpu", "memory", "resource", "load"]):
            return self._generate_metrics_response(metrics)
            
        elif any(w in msg for w in ["hello", "hi", "hey"]):
            return "Hello! I am your AI Kubernetes Assistant. I can help you with cluster status, diagnostics, and optimization recommendations. What would you like to know?"
            
        else:
            return "I'm tuned to assist with Kubernetes operations. Try asking: 'How is the cluster health?', 'Do you have any recommendations?', or 'Show me recent errors'."

    def _generate_status_response(self, metrics, anomalies, events):
        pod_count = len(set(m.pod_name for m in metrics)) if metrics else "unknown"
        # Mocking node count as we don't have a node agent yet, or use k8s client
        node_count = 1 
        critical_issues = [a for a in anomalies if a['severity'] == 'critical']
        
        status_text = "Healthy" if not critical_issues else "Degraded"
        
        response = f"The cluster status is currently **{status_text}**.\n\n"
        response += f"- **Nodes**: {node_count} active\n"
        response += f"- **Pods**: ~{pod_count} monitored pods\n"
        
        if critical_issues:
            response += f"- **Issues**: {len(critical_issues)} critical anomalies detected.\n"
            response += f"  Most recent: {critical_issues[0]['message']}"
        else:
            response += "- **Issues**: No critical anomalies detected at this time."
            
        return response

    def _generate_recommendation_response(self, recommendations):
        if not recommendations:
            return "I don't have any active recommendations right now. Your cluster seems to be running efficiently!"
        
        response = f"I have generated **{len(recommendations)} recommendations** for optimization:\n\n"
        for i, rec in enumerate(recommendations[:3], 1):
            response += f"{i}. **{rec.recommendation_type.replace('_', ' ').title()}**: {rec.suggested_action} (*{rec.resource_name}*)\n"
            
        return response

    def _generate_anomaly_response(self, anomalies):
        if not anomalies:
            return "Great news! I haven't detected any significant errors or anomalies in the recent logs and events."
            
        response = "Here are the recent issues I've found:\n\n"
        for anomaly in anomalies[:5]:
             response += f"- **{anomaly['type']}** in *{anomaly['resource']}*: {anomaly['message']}\n"
        
        return response

    def _generate_metrics_response(self, metrics):
        if not metrics:
            return "I'm not receiving metric data at the moment. Please check the Prometheus connection."
            
        # Calc average CPU from sample
        avg_cpu = sum(m.cpu_usage for m in metrics) / len(metrics)
        highest_cpu = max(metrics, key=lambda m: m.cpu_usage)
        
        return f"Current Resource Usage:\n\n- **Average CPU Load**: {avg_cpu:.2f} cores\n- **Peak Usage**: Pod *{highest_cpu.pod_name}* is using {highest_cpu.cpu_usage:.2f} cores."

chat_agent = SmartChatAgent()

@router.post("/chat", response_model=ChatResponse)
async def chat_handler(request: ChatRequest):
    response_text = await chat_agent.process_message(request.message)
    return ChatResponse(response=response_text)
