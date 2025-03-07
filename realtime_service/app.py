#!/usr/bin/env python3
from fastapi import FastAPI, WebSocket
from pydantic import BaseModel
import asyncio

app = FastAPI()
connections = {}  # {user_id: WebSocket}

# Pydantic schema
class NotifyRequest(BaseModel):
    user_id: int
    message: str

# WebSocket endpoint
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await websocket.accept()
    connections[user_id] = websocket
    try:
        while True:
            await websocket.receive_text()  # Keep connection alive
    except:
        del connections[user_id]

# HTTP endpoint for other services
@app.post("/notify")
async def notify(request: NotifyRequest):
    if request.user_id in connections:
        await connections[request.user_id].send_text(request.message)
    return {"message": "Sent"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)