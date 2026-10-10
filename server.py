"""
Real-Time AI Interview Co-Pilot Server ("The Cyrano Engine")
Provides WebSocket and REST endpoints for sub-second interview defense.
"""

import os
import json
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import uvicorn
from cyber_suite.offensive import MetasploitRPC, ScapyWrapper, EmpireWrapper
from cyber_suite.defensive import NmapWrapper, OpenVASWrapper

from engine import InterviewEngine

app = FastAPI(title="Sovereign Interview Co-Pilot", version="1.0.0")

# Initialize Engine
engine = InterviewEngine()

# Mount static directory
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

class QueryRequest(BaseModel):
    query: str

@app.get("/")
async def get_index():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return JSONResponse({"status": "Interview Co-Pilot backend active", "static_dir": STATIC_DIR})

@app.get("/api/topics")
async def list_topics():
    return engine.get_all_topics_summary()

@app.get("/api/topic/{topic_id}")
async def get_topic(topic_id: str):
    topic = engine.get_topic_by_id(topic_id)
    if topic:
        return topic
    return JSONResponse({"error": "Topic not found"}, status_code=404)

@app.get("/api/profile")
async def get_profile():
    return engine.profile

@app.post("/api/query")
async def execute_query(req: QueryRequest):
    result = engine.match_question(req.query)
    return result

@app.websocket("/ws/transcribe")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    # Send initial greeting & profile
    await websocket.send_json({
        "type": "connected",
        "message": "Sovereign Co-Pilot HUD Connected. Listening...",
        "profile": engine.profile,
        "topics": engine.get_all_topics_summary()
    })
    
    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            action = payload.get("action", "query")
            
            if action == "query" or action == "speech":
                query_text = payload.get("text", "").strip()
                is_final = payload.get("is_final", True)
                if query_text:
                    result = engine.match_question(query_text)
                    await websocket.send_json({
                        "type": "result",
                        "is_final": is_final,
                        "data": result
                    })
            elif action == "select_topic":
                topic_id = payload.get("topic_id")
                topic = engine.get_topic_by_id(topic_id)
                if topic:
                    await websocket.send_json({
                        "type": "result",
                        "is_final": True,
                        "data": {
                            "query": f"Manual selection: {topic['title']}",
                            "matched": True,
                            "confidence": 100.0,
                            "topic": topic,
                            "alternatives": [],
                            "profile": engine.profile
                        }
                    })
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"WebSocket error: {e}")

# New Cyber WebSocket endpoint
@app.websocket("/ws/cyber")
async def cyber_ws(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            msg = await websocket.receive_text()
            payload = json.loads(msg)
            result = handle_cyber_command(payload)
            await websocket.send_json({"type": "cyber_result", "result": result})
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"WebSocket error (cyber): {e}")

def handle_cyber_command(command: dict) -> dict:
    """Dispatch a cyber command to the appropriate toolkit.
    Expected command format:
    {
        "tool": "nmap" | "metasploit" | "scapy" | "openvas",
        "action": "scan" | "execute" | "list_sessions" | ...,
        "params": { ... }
    }
    Returns a dict with result or error.
    """
    tool = command.get("tool")
    action = command.get("action")
    params = command.get("params", {})
    try:
        if tool == "nmap":
            wrapper = NmapWrapper()
            if action == "scan":
                return wrapper.scan(**params)
        elif tool == "metasploit":
            client = MetasploitRPC()
            if action == "execute_module":
                return client.execute_module(**params)
            if action == "list_sessions":
                return client.list_sessions()
        elif tool == "scapy":
            wrapper = ScapyWrapper()
            if action == "arp_scan":
                return wrapper.arp_scan(**params)
        elif tool == "openvas":
            wrapper = OpenVASWrapper()
            if action == "launch_scan":
                return wrapper.launch_scan(**params)
            if action == "get_report":
                return wrapper.get_report(**params)
        return {"error": "Unsupported tool/action"}
    except Exception as e:
        return {"error": str(e)}

def run_server(host="127.0.0.1", port=8888):
    print(f"Starting Sovereign Interview Co-Pilot on http://{host}:{port}")
    uvicorn.run(app, host=host, port=port, log_level="info")

if __name__ == "__main__":
    run_server()
