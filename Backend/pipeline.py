import cv2
import time
import numpy as np
import tensorflow as tf
from collections import deque
import threading

import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from shared_state import latest_frame_data
from signals import compute_signals
from features import compute_window_features


# =============================
# Model
# =============================

ml_model = tf.keras.models.load_model("models/model.keras")


# =============================
# MediaPipe model
# =============================

MODEL_PATH = "models/face_landmarker_v2_with_blendshapes.task"


# =============================
# Sliding window config
# =============================

WINDOW_SECONDS = 2.0
FPS = 30
MAX_FRAMES = int(WINDOW_SECONDS * FPS)

window = deque(maxlen=MAX_FRAMES)

WINDOW_TICK_FRAMES = 5
frame_count = 0


# =============================
# Landmark storage
# =============================

latest_landmarks = None
lm_lock = threading.Lock()


# =============================
# MediaPipe callback
# =============================

def on_result(result: vision.FaceLandmarkerResult, output_image: mp.Image, timestamp_ms: int):

    global latest_landmarks

    if result.face_landmarks:

        with lm_lock:
            latest_landmarks = result.face_landmarks[0]


# =============================
# Initialize MediaPipe
# =============================

base_options = python.BaseOptions(model_asset_path=MODEL_PATH)

options = vision.FaceLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.LIVE_STREAM,
    num_faces=1,
    output_face_blendshapes=False,
    output_facial_transformation_matrixes=False,
    result_callback=on_result,
)

landmarker = vision.FaceLandmarker.create_from_options(options)


# =============================
# Pipeline
# =============================

def run_pipeline():

    global frame_count

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        raise RuntimeError("Could not open webcam")

    start_time = time.perf_counter()
    prev_time = time.perf_counter()

    engagement_score = 0.0
    intensity_score = 0.0

    while True:

        # ---------------------------
        # Capture
        # ---------------------------

        t0 = time.perf_counter()

        ok, frame_bgr = cap.read()

        capture_time = time.perf_counter() - t0

        if not ok:
            continue

        frame_bgr = cv2.flip(frame_bgr, 1)

        h, w = frame_bgr.shape[:2]


        # ---------------------------
        # MediaPipe FaceMesh
        # ---------------------------

        t1 = time.perf_counter()

        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=frame_rgb
        )

        timestamp_ms = int((time.perf_counter() - start_time) * 1000)

        landmarker.detect_async(mp_image, timestamp_ms)

        facemesh_time = time.perf_counter() - t1


        # ---------------------------
        # Get latest landmarks
        # ---------------------------

        with lm_lock:
            lms = latest_landmarks


        if lms is None:
            continue


        # ---------------------------
        # Signal extraction
        # ---------------------------

        t2 = time.perf_counter()

        signals = compute_signals(lms, w, h)

        feature_time = time.perf_counter() - t2


        # ---------------------------
        # Sliding window
        # ---------------------------

        window.append(signals)

        frame_count += 1

        features = None


        # ---------------------------
        # Model prediction
        # ---------------------------

        t3 = time.perf_counter()

        if frame_count % WINDOW_TICK_FRAMES == 0:

            features = compute_window_features(window,FPS)

            if features:

                feature_array = np.array(
                    [list(features.values())],
                    dtype=np.float32
                )

                pred = ml_model.predict(feature_array, verbose=0)

                engagement_score = float(pred[0][0])
                intensity_score = float(pred[0][1])

        model_time = time.perf_counter() - t3


        # ---------------------------
        # FPS calculation
        # ---------------------------

        current_time = time.perf_counter()

        fps = 1 / (current_time - prev_time)

        prev_time = current_time


        # ---------------------------
        # Update shared state
        # ---------------------------

        latest_frame_data.update({

            "timestamp": timestamp_ms,

            "signals": signals,

            "features": features,

            "model": {
                "engagement": engagement_score,
                "intensity": intensity_score
            },

            "latency": {
                "capture": capture_time,
                "facemesh": facemesh_time,
                "features": feature_time,
                "model": model_time
            },

            "fps": fps
        })