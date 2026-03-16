"""Sliding-window feature engineering for the engagement model."""

import numpy as np


def compute_window_features(window, FPS):
    """Aggregate recent per-frame signals into model-ready summary features."""
    if len(window) == 0:
        return None

    # Re-group the deque so each signal can be summarized across time.
    keys = window[0].keys()
    data = {k: np.array([f[k] for f in window]) for k in keys}

    features = {}

    # Head pose stability and central tendency.
    for k in ["yaw", "pitch", "roll"]:
        features[f"{k}_mean"] = np.mean(data[k])
        features[f"{k}_std"] = np.std(data[k])

    # Eye openness and left/right balance.
    features["avg_EAR_mean"] = np.mean(data["avg_EAR"])
    features["avg_EAR_std"] = np.std(data["avg_EAR"])
    features["eye_symmetry_mean"] = np.mean(data["eye_symmetry"])
    features["eye_symmetry_std"] = np.std(data["eye_symmetry"])

    # Blink rate approximated from threshold crossings in the EAR sequence.
    EAR_THRESHOLD = 0.18
    ear_below = data["avg_EAR"] < EAR_THRESHOLD
    blink_count = np.sum(np.diff(ear_below.astype(int)) == 1)
    features["blink_rate"] = blink_count / (len(window) / FPS)

    # Mouth movement.
    features["mouth_open_mean"] = np.mean(data["mouth_open"])
    features["mouth_open_std"] = np.std(data["mouth_open"])

    # Brow movement and left/right consistency.
    for k in ["left_brow_raise", "right_brow_raise", "brow_symmetry"]:
        features[f"{k}_mean"] = np.mean(data[k])
        features[f"{k}_std"] = np.std(data[k])

    # Smile intensity over the same window.
    features["smile_mean"] = np.mean(data["smile"])
    features["smile_std"] = np.std(data["smile"])

    # Motion energy is a simple proxy for how much the face state changes frame-to-frame.
    motion_energy = 0.0
    for i in range(1, len(window)):
        prev = np.array(
            [window[i - 1][k] for k in ["yaw", "pitch", "roll", "avg_EAR", "mouth_open"]],
        )
        curr = np.array(
            [window[i][k] for k in ["yaw", "pitch", "roll", "avg_EAR", "mouth_open"]],
        )
        motion_energy += np.linalg.norm(curr - prev)
    features["motion_energy"] = motion_energy / max(len(window) - 1, 1)

    return features
