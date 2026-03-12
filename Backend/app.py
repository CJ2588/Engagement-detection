# app.py
from fastapi import FastAPI, WebSocket
import threading
import asyncio

from pipeline import run_pipeline
from shared_state import latest_frame_data

app = FastAPI()

# Start the pipeline in a background thread
threading.Thread(target=run_pipeline, daemon=True).start()

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    while True:
        await ws.send_json(latest_frame_data)
        await asyncio.sleep(0.03)  # ~30fps

# Optional: simple HTTP health check
@app.get("/health")
async def health():
    return {"status": "ok"}