# Engagement Dashboard

Cortality is a real-time engagement monitoring project that uses a webcam, MediaPipe face landmarks, handcrafted facial signals, and a TensorFlow model to estimate engagement and intensity live. The backend performs capture and inference, while the frontend displays the live video stream, session metrics, and scrolling signal charts.

## What It Does

- Captures live webcam frames from the backend
- Detects facial landmarks with MediaPipe
- Extracts facial behavior signals such as yaw, pitch, roll, eye openness, brow movement, smile, and mouth openness
- Builds short sliding-window features from those signals
- Runs a TensorFlow model to estimate engagement and intensity
- Streams metrics and compressed video frames to a React dashboard over WebSocket

## Project Structure

```text
Project/
  Backend/
    app.py           FastAPI app and WebSocket endpoint
    pipeline.py      Camera capture, feature extraction, model inference
    signals.py       Per-frame facial signal calculations
    features.py      Sliding-window feature generation
    shared_state.py  Shared payload sent to the frontend
    models/          MediaPipe and TensorFlow model files
  Frontend/
    src/
      app.js         Main dashboard layout
      components/    Badge and chart components
      utils/         WebSocket client
```

## Tech Stack

- Backend: FastAPI, OpenCV, MediaPipe, TensorFlow, NumPy
- Frontend: React, Recharts
- Transport: WebSocket

## Dashboard Highlights

- Live video preview from the backend webcam session
- Real-time session badges for FPS, latency, resolution, frame count, and status
- Dedicated chart column with its own scroll behavior
- Continuous chart updates for engagement, yaw, pitch, roll, eye openness, and mouth openness

## How It Works

1. The backend opens the webcam and reads frames continuously.
2. MediaPipe extracts face landmarks from each frame.
3. The backend computes facial signals from those landmarks.
4. A sliding window of signal history is converted into model-ready features.
5. The TensorFlow model predicts engagement and intensity.
6. The backend sends both metrics and compressed video frames to the frontend through `/ws`.
7. The frontend renders the live stream, badges, and charts in real time.

## Running The Project

Backend:

```bash
cd Backend
uvicorn app:app --reload
```

Frontend:

```bash
cd Frontend
npm start
```

The frontend expects the backend WebSocket at `ws://localhost:8000/ws`.

## Notes

- A working webcam is required.
- Model files must exist in `Backend/models/`.
- Video is streamed as compressed JPEG frames over WebSocket for simplicity.

## Demo Media

Yes, adding a short demo is a very good idea.

- A short GIF is great for GitHub because people can see the project instantly without leaving the page.
- A longer video is also useful if you want to show the live stream, chart updates, and overall interaction more clearly.
- Best option: put a GIF near the top of the README and link to a full video below it.

If you want, I can also rewrite this README in a more polished portfolio style with sections like `Motivation`, `Challenges`, and `Future Improvements`.
