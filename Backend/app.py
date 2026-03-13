from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import threading
import asyncio

from pipeline import run_pipeline
from shared_state import latest_frame_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    stop_event = threading.Event()
    pipeline_thread = threading.Thread(
        target=run_pipeline,
        args=(stop_event,),
        name="camera-pipeline",
    )
    pipeline_thread.start()

    app.state.pipeline_stop_event = stop_event
    app.state.pipeline_thread = pipeline_thread

    try:
        yield
    finally:
        stop_event.set()
        pipeline_thread.join(timeout=2)


app = FastAPI(lifespan=lifespan)

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            await ws.send_json(latest_frame_data)
            await asyncio.sleep(0.03)  # ~30fps
    except WebSocketDisconnect:
        return

# Optional: simple HTTP health check
@app.get("/health")
async def health():
    return {"status": "ok"}
