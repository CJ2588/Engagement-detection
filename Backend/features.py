import numpy as np

def compute_window_features(window,FPS):
 
    if len(window) == 0:
        return None

    # Convert deque of dicts to dict of arrays
    keys = window[0].keys()
    data = {k: np.array([f[k] for f in window]) for k in keys}

    features = {}

    # Head pose
    for k in ["yaw", "pitch", "roll"]:
        features[f"{k}_mean"] = np.mean(data[k])
        features[f"{k}_std"] = np.std(data[k])

    # Eyes
    features["avg_EAR_mean"] = np.mean(data["avg_EAR"])
    features["avg_EAR_std"] = np.std(data["avg_EAR"])
    features["eye_symmetry_mean"] = np.mean(data["eye_symmetry"])
    features["eye_symmetry_std"] = np.std(data["eye_symmetry"])

    # Blink rate (threshold crossings)
    EAR_THRESHOLD = 0.18
    ear_below = data["avg_EAR"] < EAR_THRESHOLD
    # Count rising edges
    blink_count = np.sum(np.diff(ear_below.astype(int)) == 1)
    features["blink_rate"] = blink_count / (len(window)/FPS)

    # Mouth
    features["mouth_open_mean"] = np.mean(data["mouth_open"])
    features["mouth_open_std"] = np.std(data["mouth_open"])

    # Brow
    for k in ["left_brow_raise", "right_brow_raise", "brow_symmetry"]:
        features[f"{k}_mean"] = np.mean(data[k])
        features[f"{k}_std"] = np.std(data[k])

    # Smile
    features["smile_mean"] = np.mean(data["smile"])
    features["smile_std"] = np.std(data["smile"])

    # Motion energy: L2 displacement of landmarks between frames
    motion_energy = 0.0
    for i in range(1, len(window)):
        # Use avg_EAR + head pose + mouth_open as proxy
        prev = np.array([window[i-1][k] for k in ["yaw","pitch","roll","avg_EAR","mouth_open"]])
        curr = np.array([window[i][k] for k in ["yaw","pitch","roll","avg_EAR","mouth_open"]])
        motion_energy += np.linalg.norm(curr - prev)
    features["motion_energy"] = motion_energy / max(len(window)-1, 1)

    return features