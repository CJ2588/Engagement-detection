"""Shared in-memory payload published to websocket clients."""

from typing import Any, Dict


# The pipeline updates this dictionary in place so the websocket endpoint can stream it
# without rebuilding a fresh object on every send.
latest_frame_data: Dict[str,Any] = {
    "timestamp": None,
    "video_frame": None,
    "signals": None,
    "model": None,
    "features": None,
    "latency": None,
    "fps": None,
    "resolution": None,
    "status": "starting",
    "error": None,
}
