"""Camera pipeline for capture, signal extraction, feature building, and inference."""

import base64
from collections import deque
from pathlib import Path
import threading
import time

import cv2
import mediapipe as mp
import numpy as np
import tensorflow as tf
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from features import compute_window_features
from shared_state import latest_frame_data
from signals import compute_signals


# Load the trained engagement model once at import time so the worker thread can reuse it.
BASE_DIR = Path(__file__).resolve().parent
ml_model = tf.keras.models.load_model(BASE_DIR / "models" / "model.keras")

# MediaPipe face landmarker task used for live webcam inference.
MODEL_PATH = BASE_DIR / "models" / "face_landmarker_v2_with_blendshapes.task"

# The model consumes features aggregated over a short sliding window.
WINDOW_SECONDS = 2.0
FPS = 30
MAX_FRAMES = int(WINDOW_SECONDS * FPS)
WINDOW_TICK_FRAMES = 5

# The dashboard receives a smaller JPEG frame so the websocket payload stays manageable.
VIDEO_FRAME_MAX_WIDTH = 640
VIDEO_JPEG_QUALITY = 70

window = deque(maxlen=MAX_FRAMES)
frame_count = 0

# MediaPipe results arrive asynchronously, so the latest landmarks are shared via a lock.
latest_landmarks = None
lm_lock = threading.Lock()


def on_result(
    result: vision.FaceLandmarkerResult,
    output_image: mp.Image,
    timestamp_ms: int,
):
    """Store the latest face landmarks produced by MediaPipe's async callback."""
    del output_image, timestamp_ms

    global latest_landmarks

    if result.face_landmarks:
        with lm_lock:
            latest_landmarks = result.face_landmarks[0]


base_options = python.BaseOptions(model_asset_path=str(MODEL_PATH))

options = vision.FaceLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.LIVE_STREAM,
    num_faces=1,
    output_face_blendshapes=False,
    output_facial_transformation_matrixes=False,
    result_callback=on_result,
)

landmarker = vision.FaceLandmarker.create_from_options(options)


def _open_camera():
    """Open the default webcam with a Windows-friendly backend preference."""
    # Prefer DirectShow on Windows to avoid MSMF grab issues during long-running capture.
    preferred_backends = [cv2.CAP_DSHOW, cv2.CAP_ANY]

    for backend in preferred_backends:
        cap = cv2.VideoCapture(0, backend)
        if cap.isOpened():
            return cap
        cap.release()

    return cv2.VideoCapture(0)


def _encode_preview_frame(frame_bgr: np.ndarray) -> str | None:
    """Resize and JPEG-encode a frame for websocket transport to the dashboard."""
    h, w = frame_bgr.shape[:2]

    if w > VIDEO_FRAME_MAX_WIDTH:
        scale = VIDEO_FRAME_MAX_WIDTH / float(w)
        preview_frame = cv2.resize(
            frame_bgr,
            (VIDEO_FRAME_MAX_WIDTH, int(h * scale)),
            interpolation=cv2.INTER_AREA,
        )
    else:
        preview_frame = frame_bgr

    encoded_ok, encoded_buffer = cv2.imencode(
        ".jpg",
        preview_frame,
        [int(cv2.IMWRITE_JPEG_QUALITY), VIDEO_JPEG_QUALITY],
    )

    if not encoded_ok:
        return None

    return base64.b64encode(encoded_buffer).decode("ascii")


def run_pipeline(stop_event: threading.Event):
    """Run the live capture and inference loop until the app requests shutdown."""
    global frame_count

    cap = _open_camera()

    if not cap.isOpened():
        raise RuntimeError("Could not open webcam")

    start_time = time.perf_counter()
    prev_time = time.perf_counter()
    engagement_score = 0.0
    intensity_score = 0.0
    consecutive_failures = 0

    try:
        latest_frame_data.update({
            "status": "running",
            "error": None,
        })

        while not stop_event.is_set():
            t0 = time.perf_counter()
            ok, frame_bgr = cap.read()
            capture_time = time.perf_counter() - t0

            if not ok:
                consecutive_failures += 1
                if stop_event.is_set() or consecutive_failures >= 10:
                    latest_frame_data.update({
                        "status": "error",
                        "error": "Camera capture failed repeatedly.",
                    })
                    break
                time.sleep(0.05)
                continue

            consecutive_failures = 0
            frame_bgr = cv2.flip(frame_bgr, 1)
            h, w = frame_bgr.shape[:2]
            video_frame = _encode_preview_frame(frame_bgr)

            t1 = time.perf_counter()
            frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
            timestamp_ms = int((time.perf_counter() - start_time) * 1000)
            landmarker.detect_async(mp_image, timestamp_ms)
            facemesh_time = time.perf_counter() - t1

            with lm_lock:
                lms = latest_landmarks

            # The live stream keeps running even before MediaPipe returns its first face.
            if lms is None:
                continue

            t2 = time.perf_counter()
            signals = compute_signals(lms, w, h)
            feature_time = time.perf_counter() - t2

            window.append(signals)
            frame_count += 1
            features = None

            t3 = time.perf_counter()
            if frame_count % WINDOW_TICK_FRAMES == 0:
                features = compute_window_features(window, FPS)

                if features:
                    feature_array = np.array([list(features.values())], dtype=np.float32)
                    pred = ml_model.predict(feature_array, verbose=0)
                    engagement_score = float(pred[0][0])
                    intensity_score = float(pred[0][1])

            model_time = time.perf_counter() - t3

            current_time = time.perf_counter()
            fps = 1 / (current_time - prev_time)
            prev_time = current_time

            latest_frame_data.update({
                "timestamp": timestamp_ms,
                "video_frame": video_frame,
                "signals": signals,
                "features": features,
                "model": {
                    "engagement": engagement_score,
                    "intensity": intensity_score,
                },
                "latency": {
                    "capture": capture_time,
                    "facemesh": facemesh_time,
                    "features": feature_time,
                    "model": model_time,
                },
                "fps": fps,
                "resolution": {
                    "width": w,
                    "height": h,
                },
                "status": "running",
                "error": None,
            })
    except Exception as exc:
        latest_frame_data.update({
            "status": "error",
            "error": str(exc),
        })
        raise
    finally:
        cap.release()
        landmarker.close()
