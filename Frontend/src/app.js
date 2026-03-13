import React, { useEffect, useState } from "react";
import SignalChart from "./components/Linecharts";
import Badge from "./components/Badge";
import { connectWS } from "./utils/wsClient";

export default function App() {
  const [frames, setFrames] = useState([]);

  const [fps, setFps] = useState(0);
  const [latency, setLatency] = useState({ capture: 0, facemesh: 0, features: 0, model: 0 });
  const [resolution, setResolution] = useState({ w: 640, h: 480 });
  const [status, setStatus] = useState("starting");
  const [error, setError] = useState(null);

  useEffect(() => {
    const ws = connectWS((data) => {
      setFrames((prev) => [...prev.slice(-99), data]); // keep last 100 frames
      setFps(data.fps ?? 0);
      setLatency(data.latency ?? { capture: 0, facemesh: 0, features: 0, model: 0 });
      setStatus(data.status ?? "starting");
      setError(data.error ?? null);
      if (data.resolution) {
        setResolution({ w: data.resolution.width, h: data.resolution.height });
      }
    });

    return () => ws.close();
  }, []);

  return (
    <div style={{ padding: 20 }}>
      <h2>Real-time Engagement Dashboard</h2>

      <div style={{ display: "flex", gap: 20 }}>
        <Badge label="FPS" value={fps.toFixed(1)} />
        <Badge label="Capture Latency" value={(latency.capture*1000).toFixed(1) + " ms"} />
        <Badge label="FaceMesh Latency" value={(latency.facemesh*1000).toFixed(1) + " ms"} />
        <Badge label="Resolution" value={`${resolution.w}x${resolution.h}`} />
        <Badge label="Status" value={status} />
      </div>

      {error ? <p style={{ color: "crimson" }}>Pipeline error: {error}</p> : null}

      <div style={{ display: "flex", flexDirection: "column", gap: 30, marginTop: 20 }}>
        <SignalChart data={frames} dataKey="model.engagement" color="#82ca9d" name="Engagement" />
        <SignalChart data={frames} dataKey="signals.yaw" color="#8884d8" name="Yaw" />
        <SignalChart data={frames} dataKey="signals.pitch" color="#ff7300" name="Pitch" />
        <SignalChart data={frames} dataKey="signals.roll" color="#387908" name="Roll" />
        <SignalChart data={frames} dataKey="signals.avg_EAR" color="#ff0000" name="EAR" />
        <SignalChart data={frames} dataKey="signals.mouth_open" color="#0000ff" name="Mouth Open" />
      </div>
    </div>
  );
}
