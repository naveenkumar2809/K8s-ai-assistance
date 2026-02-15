from fastapi import APIRouter
from pydantic import BaseModel
from app.agents.monitor_agent import monitor_agent
from app.agents.anomaly_agent import anomaly_agent
from app.agents.recommendation_agent import recommendation_agent
from app.core.config import settings
import logging
import httpx
import json

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
        logs = await monitor_agent.get_logs()
        
        # Run analysis (quick re-run to get current anomalies)
        anomalies = anomaly_agent.detect_anomalies(events, metrics, logs)
        recommendations = recommendation_agent.generate_recommendations(anomalies)
        
        # 2. Build context for LLM
        context = self._build_cluster_context(metrics, anomalies, recommendations, events, logs)
        
        # 3. Call GPT-5 Nano
        try:
            llm_response = await self._call_gpt5_nano(message, context)
            return llm_response
        except Exception as e:
            logger.error(f"LLM API error: {e}")
            # Fallback to template-based response
            return self._fallback_response(message, metrics, anomalies, recommendations)
    
    def _build_cluster_context(self, metrics, anomalies, recommendations, events, logs):
        """Build a concise context summary for the LLM"""
        pod_count = len(set(m.pod_name for m in metrics)) if metrics else 0
        node_count = 1  # Mock
        critical_issues = [a for a in anomalies if a['severity'] == 'critical']
        
        context = f"""Current Kubernetes Cluster Status:
- Nodes: {node_count} active
- Pods: {pod_count} monitored
- Critical Issues: {len(critical_issues)}
- Active Recommendations: {len(recommendations)}
"""
        
        if metrics:
            avg_cpu = sum(m.cpu_usage for m in metrics) / len(metrics)
            avg_mem = sum(m.memory_usage for m in metrics) / len(metrics)
            context += f"\nResource Usage:\n- Average CPU: {avg_cpu:.2f}%\n- Average Memory: {avg_mem:.2f}%\n"
        
        if anomalies:
            context += f"\nRecent Anomalies:\n"
            for a in anomalies[:3]:
                context += f"- {a['type']}: {a['message']}\n"
        
        if recommendations:
            context += f"\nRecommendations:\n"
            for r in recommendations[:3]:
                context += f"- {r.recommendation_type}: {r.suggested_action}\n"
        
        if logs:
            context += f"\nRecent Logs:\n"
            for log in logs[:3]:
                context += f"- [{log.level}] {log.message}\n"
        
        return context
    
    async def _call_gpt5_nano(self, user_message: str, cluster_context: str) -> str:
        """Call GPT-5 Nano API with cluster context"""
        system_prompt = f"""You are an AI Kubernetes Assistant named K8s Pilot, helping Naveen manage his Kubernetes cluster.

You have access to real-time cluster data:
{cluster_context}

Provide helpful, concise, and actionable responses. Use markdown formatting for better readability.
Be friendly and address the user as Naveen when appropriate."""

        headers = {
            "Authorization": f"Bearer {settings.GPT_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": settings.GPT_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                settings.GPT_API_URL,
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            return data['choices'][0]['message']['content']
    
    def _fallback_response(self, message: str, metrics, anomalies, recommendations):
        """Fallback to template-based response if LLM fails"""
        msg = message.lower()
        
        if any(w in msg for w in ["status", "health", "overview", "cluster"]):
            return self._generate_status_response(metrics, anomalies)
        elif any(w in msg for w in ["recommend", "suggestion", "optimize"]):
            return self._generate_recommendation_response(recommendations)
        elif any(w in msg for w in ["hello", "hi", "hey"]):
            return "Hello Naveen! I am your AI Kubernetes Assistant. I can help you with cluster status, diagnostics, and optimization recommendations. What would you like to know?"
        else:
            return "I'm here to help with your Kubernetes cluster. Try asking about cluster health, recommendations, or resource usage."
    
    def _generate_status_response(self, metrics, anomalies):
        pod_count = len(set(m.pod_name for m in metrics)) if metrics else "unknown"
        critical_issues = [a for a in anomalies if a['severity'] == 'critical']
        status_text = "Healthy" if not critical_issues else "Degraded"
        
        response = f"The cluster status is currently **{status_text}**.\n\n"
        response += f"- **Pods**: ~{pod_count} monitored pods\n"
        
        if critical_issues:
            response += f"- **Issues**: {len(critical_issues)} critical anomalies detected.\n"
        else:
            response += "- **Issues**: No critical anomalies detected."
        
        return response
    
    def _generate_recommendation_response(self, recommendations):
        if not recommendations:
            return "I don't have any active recommendations right now. Your cluster seems to be running efficiently!"
        
        response = f"I have **{len(recommendations)} recommendations** for optimization:\n\n"
        for i, rec in enumerate(recommendations[:3], 1):
            response += f"{i}. **{rec.recommendation_type.replace('_', ' ').title()}**: {rec.suggested_action}\n"
        
        return response

chat_agent = SmartChatAgent()

@router.post("/chat", response_model=ChatResponse)
async def chat_handler(request: ChatRequest):
    response_text = await chat_agent.process_message(request.message)
    return ChatResponse(response=response_text)
