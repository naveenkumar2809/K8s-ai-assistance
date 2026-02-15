from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List
from app.models.schemas import ClusterStatus, Recommendation, ActionRequest
from app.agents.monitor_agent import monitor_agent
from app.agents.anomaly_agent import anomaly_agent
from app.agents.recommendation_agent import recommendation_agent
from app.agents.action_agent import action_agent
import asyncio

router = APIRouter()

# In-memory store for demo purposes
current_recommendations: List[Recommendation] = []
history: List[Recommendation] = []

@router.get("/status", response_model=ClusterStatus)
async def get_status():
    # Gather data
    events = await monitor_agent.get_events()
    metrics = await monitor_agent.get_metrics()
    logs = await monitor_agent.get_logs()
    
    # Run analysis pipeline (for demo, running on every request or scheduled)
    anomalies = anomaly_agent.detect_anomalies(events, metrics, logs)
    
    # Generate recommendations
    new_recs = recommendation_agent.generate_recommendations(anomalies)
    
    # Deduplicate logic would go here (omitted for brevity)
    # For now, just add new ones if not exists
    global current_recommendations
    for rec in new_recs:
        # Simple check by resource and type to avoid spam
        exists = any(r.resource_name == rec.resource_name and r.recommendation_type == rec.recommendation_type and r.status == 'pending' for r in current_recommendations)
        if not exists:
            current_recommendations.append(rec)

    return ClusterStatus(
        node_count=1, # Mock
        pod_count=10, # Mock
        unhealthy_pods=len([a for a in anomalies if a['severity'] == 'critical']),
        cpu_total_usage=sum([m.cpu_usage for m in metrics]) if metrics else 0.0,
        memory_total_usage=0.0,
        events=events[-10:], # Last 10
        active_recommendations=[r for r in current_recommendations if r.status == 'pending']
    )

@router.post("/recommendations/action")
async def take_action(request: ActionRequest):
    global current_recommendations
    
    # Find recommendation
    rec = next((r for r in current_recommendations if r.id == request.recommendation_id), None)
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    if request.approve:
        success = await action_agent.execute_action(rec)
        if success:
            rec.status = "applied"
            return {"status": "success", "message": "Action applied"}
        else:
            return {"status": "error", "message": "Failed to apply action"}
    else:
        rec.status = "discarded"
        return {"status": "success", "message": "Recommendation discarded"}

@router.get("/recommendations", response_model=List[Recommendation])
async def get_recommendations():
    return current_recommendations

from fastapi import WebSocket, WebSocketDisconnect
import json
import asyncio

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Re-use the get_status logic to fetch latest state
            # In a real app, this should be event-driven or cached
            # For this demo, we poll and push
            status = await get_status()
            # Convert Pydantic model to dict, handling datetime serialization
            await websocket.send_json(status.model_dump(mode='json'))
            await asyncio.sleep(2) # Push updates every 2 seconds
    except WebSocketDisconnect:
        print("Client disconnected")
