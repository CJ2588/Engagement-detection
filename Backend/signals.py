"""Per-frame facial signal calculations derived from MediaPipe landmarks."""

import cv2
import numpy as np


def compute_signals(landmarks, w, h):
    """Compute the set of per-frame signals consumed by the feature pipeline."""
    eyes = compute_eye_signals(landmarks, w, h)
    smile = compute_smile_proxy(landmarks, w, h)
    mouth = compute_mouth_open(landmarks, w, h)
    brows = compute_eyebrow_raise(landmarks, w, h)
    head = compute_head_pose(landmarks, w, h)

    return {
        **eyes,
        "smile": smile,
        "mouth_open": mouth,
        **brows,
        **head,
    }


def lm_to_xy(landmarks, idx, w, h):
    """Convert a normalized MediaPipe landmark into pixel coordinates."""
    lm = landmarks[idx]
    return np.array([lm.x * w, lm.y * h], dtype=np.float32)


def dist2(a, b):
    """Return Euclidean distance between two 2D points."""
    return float(np.linalg.norm(a - b))


def face_scale(landmarks, w, h):
    """Use the outer eye corners as a stable face-size normalization factor."""
    left_outer = lm_to_xy(landmarks, 33, w, h)
    right_outer = lm_to_xy(landmarks, 263, w, h)
    return max(dist2(left_outer, right_outer), 1e-6)


def compute_ear(landmarks, w, h, eye_idxs):
    """Compute eye aspect ratio (EAR) for a single eye."""
    p1 = lm_to_xy(landmarks, eye_idxs[0], w, h)
    p2 = lm_to_xy(landmarks, eye_idxs[1], w, h)
    p3 = lm_to_xy(landmarks, eye_idxs[2], w, h)
    p4 = lm_to_xy(landmarks, eye_idxs[3], w, h)
    p5 = lm_to_xy(landmarks, eye_idxs[4], w, h)
    p6 = lm_to_xy(landmarks, eye_idxs[5], w, h)

    vertical_1 = dist2(p2, p6)
    vertical_2 = dist2(p3, p5)
    horizontal = dist2(p1, p4)

    return (vertical_1 + vertical_2) / (2.0 * max(horizontal, 1e-6))


def compute_eye_signals(landmarks, w, h):
    """Return eye openness and left/right symmetry measurements."""
    left_eye = [33, 160, 158, 133, 153, 144]
    right_eye = [362, 385, 387, 263, 373, 380]

    left_ear = compute_ear(landmarks, w, h, left_eye)
    right_ear = compute_ear(landmarks, w, h, right_eye)
    avg_ear = (left_ear + right_ear) / 2.0

    return {
        "left_EAR": float(left_ear),
        "right_EAR": float(right_ear),
        "avg_EAR": float(avg_ear),
        "eye_symmetry": float(abs(left_ear - right_ear)),
    }


def compute_smile_proxy(landmarks, w, h):
    """Estimate smiling by comparing lip center height to mouth corners."""
    left_corner = lm_to_xy(landmarks, 61, w, h)
    right_corner = lm_to_xy(landmarks, 291, w, h)
    upper_lip = lm_to_xy(landmarks, 13, w, h)
    lower_lip = lm_to_xy(landmarks, 14, w, h)

    mouth_center = 0.5 * (upper_lip + lower_lip)
    avg_corner_y = (left_corner[1] + right_corner[1]) / 2.0
    scale = face_scale(landmarks, w, h)

    # Positive values mean the mouth corners sit higher than the lip center.
    smile = (mouth_center[1] - avg_corner_y) / scale
    return float(smile)


def compute_mouth_open(landmarks, w, h):
    """Estimate mouth openness using normalized lip distance."""
    upper_lip = lm_to_xy(landmarks, 13, w, h)
    lower_lip = lm_to_xy(landmarks, 14, w, h)
    left_corner = lm_to_xy(landmarks, 61, w, h)
    right_corner = lm_to_xy(landmarks, 291, w, h)

    vertical = dist2(upper_lip, lower_lip)
    horizontal = dist2(left_corner, right_corner)
    ratio = vertical / max(horizontal, 1e-6)

    return float(ratio)


def compute_eyebrow_raise(landmarks, w, h):
    """Measure brow-to-eye distance for both sides of the face."""
    left_brow = lm_to_xy(landmarks, 105, w, h)
    left_eye = lm_to_xy(landmarks, 159, w, h)
    right_brow = lm_to_xy(landmarks, 334, w, h)
    right_eye = lm_to_xy(landmarks, 386, w, h)

    scale = face_scale(landmarks, w, h)
    left_raise = dist2(left_brow, left_eye) / scale
    right_raise = dist2(right_brow, right_eye) / scale

    return {
        "left_brow_raise": float(left_raise),
        "right_brow_raise": float(right_raise),
        "brow_symmetry": float(abs(left_raise - right_raise)),
    }


# Canonical 3D anchor points used to recover approximate head pose with solvePnP.
face_3d_points = np.array([
    [0.0, 0.0, 0.0],       # Nose tip (landmark 1)
    [0.0, -63.6, -12.5],   # Chin (landmark 152)
    [-43.3, 32.7, -26.0],  # Left eye outer corner (landmark 33)
    [43.3, 32.7, -26.0],   # Right eye outer corner (landmark 263)
    [-28.9, -28.9, -20.0], # Left mouth corner (landmark 61)
    [28.9, -28.9, -20.0],  # Right mouth corner (landmark 291)
], dtype=np.float32)


def get_2d_points(landmarks, w, h):
    """Collect the 2D facial anchor points that correspond to the 3D template."""
    return np.array([
        lm_to_xy(landmarks, 1, w, h),
        lm_to_xy(landmarks, 152, w, h),
        lm_to_xy(landmarks, 33, w, h),
        lm_to_xy(landmarks, 263, w, h),
        lm_to_xy(landmarks, 61, w, h),
        lm_to_xy(landmarks, 291, w, h),
    ], dtype=np.float32)


def get_camera_matrix(w, h):
    """Build a simple pinhole camera matrix from the current frame size."""
    focal_length = w
    center = (w / 2, h / 2)
    return np.array([
        [focal_length, 0, center[0]],
        [0, focal_length, center[1]],
        [0, 0, 1],
    ], dtype=np.float32)


def compute_head_pose(landmarks, w, h):
    """Approximate yaw, pitch, and roll from the detected face landmarks."""
    image_points = get_2d_points(landmarks, w, h)
    cam_matrix = get_camera_matrix(w, h)
    dist_coeffs = np.zeros((4, 1))

    success, rotation_vector, translation_vector = cv2.solvePnP(
        face_3d_points,
        image_points,
        cam_matrix,
        dist_coeffs,
    )
    del translation_vector

    if not success:
        return {"yaw": 0.0, "pitch": 0.0, "roll": 0.0}

    rotation_matrix, _ = cv2.Rodrigues(rotation_vector)
    sy = np.sqrt(rotation_matrix[0, 0] ** 2 + rotation_matrix[1, 0] ** 2)
    singular = sy < 1e-6

    if not singular:
        x = np.arctan2(rotation_matrix[2, 1], rotation_matrix[2, 2])
        y = np.arctan2(-rotation_matrix[2, 0], sy)
        z = np.arctan2(rotation_matrix[1, 0], rotation_matrix[0, 0])
    else:
        x = np.arctan2(-rotation_matrix[1, 2], rotation_matrix[1, 1])
        y = np.arctan2(-rotation_matrix[2, 0], sy)
        z = 0

    pitch = np.degrees(x)
    yaw = np.degrees(y)
    roll = np.degrees(z)

    return {"yaw": yaw, "pitch": pitch, "roll": roll}
