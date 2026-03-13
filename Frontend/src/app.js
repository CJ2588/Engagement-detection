import React, { useEffect, useState } from "react";
import SignalChart from "./components/Linecharts";
import Badge from "./components/Badge";
import { connectWS } from "./utils/wsClient";

export default function App() {
  const [frames, setFrames] = useState([]);
  const [videoFrame, setVideoFrame] = useState(null);
  const [fps, setFps] = useState(0);
  const [latency, setLatency] = useState({
    capture: 0,
    facemesh: 0,
    features: 0,
    model: 0,
  });
  const [resolution, setResolution] = useState({ w: 640, h: 480 });
  const [status, setStatus] = useState("starting");
  const [error, setError] = useState(null);

  useEffect(() => {
    const ws = connectWS((data) => {
      const { video_frame: incomingVideoFrame, ...chartFrame } = data;

      setFrames((prev) => [...prev.slice(-99), chartFrame]);
      setVideoFrame(
        incomingVideoFrame
          ? `data:image/jpeg;base64,${incomingVideoFrame}`
          : null,
      );
      setFps(data.fps ?? 0);
      setLatency(
        data.latency ?? { capture: 0, facemesh: 0, features: 0, model: 0 },
      );
      setStatus(data.status ?? "starting");
      setError(data.error ?? null);
      if (data.resolution) {
        setResolution({ w: data.resolution.width, h: data.resolution.height });
      }
    });

    return () => ws.close();
  }, []);

  const latestFrame = frames[frames.length - 1];
  const panelTitle = status === "running" ? "Live Session" : "Awaiting Stream";
  const statusTone = error
    ? "#b42318"
    : status === "running"
      ? "#1f7a5a"
      : "#916f1f";

  return (
    <div
      style={{
        minHeight: "100vh",
        background:
          "linear-gradient(180deg, #edf5f8 0%, #f7fafc 24%, #f6f1e8 100%)",
        color: "#15324a",
        fontFamily: '"Segoe UI", "Trebuchet MS", sans-serif',
      }}
    >
      <header
        style={{
          padding: "44px 28px 88px",
          background:
            "radial-gradient(circle at top left, rgba(255,255,255,0.28), transparent 34%), linear-gradient(135deg, #0f3554 0%, #1d5f74 42%, #d6a24f 120%)",
          color: "#f6fbff",
          boxShadow: "inset 0 -1px 0 rgba(255,255,255,0.18)",
        }}
      >
        <div style={{ maxWidth: 1400, margin: "0 auto" }}>
          <h1
            style={{
              margin: "18px 0 12px",
              fontSize: "clamp(2.4rem, 5vw, 4.5rem)",
              lineHeight: 0.95,
            }}
          >
            Real-Time Engagement Dashboard
          </h1>
          <p
            style={{
              maxWidth: 760,
              fontSize: 18,
              lineHeight: 1.6,
              margin: 0,
              color: "rgba(246,251,255,0.86)",
            }}
          >
            Watch the live camera session, inspect current health badges, and
            scroll through signal history
          </p>
        </div>
      </header>

      <main
        style={{
          maxWidth: 1400,
          margin: "-44px auto 0",
          padding: "0 28px 28px",
        }}
      >
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(360px, 1fr))",
            gap: 24,
            alignItems: "start",
          }}
        >
          <section
            style={{
              display: "flex",
              flexDirection: "column",
              gap: 20,
            }}
          >
            <div
              style={{
                padding: 22,
                borderRadius: 28,
                background:
                  "linear-gradient(180deg, rgba(12,38,58,0.98), rgba(22,64,87,0.94))",
                boxShadow: "0 24px 60px rgba(8, 24, 38, 0.24)",
                color: "#f3fbff",
              }}
            >
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  gap: 16,
                  alignItems: "flex-start",
                  marginBottom: 18,
                }}
              >
                <div>
                  <div
                    style={{
                      fontSize: 12,
                      letterSpacing: "0.12em",
                      textTransform: "uppercase",
                      color: "rgba(243,251,255,0.62)",
                    }}
                  >
                    Camera Panel
                  </div>
                  <div style={{ fontSize: 28, fontWeight: 700, marginTop: 4 }}>
                    {panelTitle}
                  </div>
                </div>
                <div style={{ fontSize: 14, color: "rgba(243,251,255,0.72)" }}>
                  {resolution.w} x {resolution.h}
                </div>
              </div>

              <div
                style={{
                  minHeight: 360,
                  borderRadius: 24,
                  overflow: "hidden",
                  position: "relative",
                  background:
                    "radial-gradient(circle at 20% 20%, rgba(214,162,79,0.4), transparent 26%), linear-gradient(145deg, #173f5d 0%, #091a2a 100%)",
                  border: "1px solid rgba(255,255,255,0.08)",
                  display: "flex",
                  alignItems: "flex-end",
                }}
              >
                {videoFrame ? (
                  <img
                    src={videoFrame}
                    alt="Live camera stream"
                    style={{
                      position: "absolute",
                      inset: 0,
                      width: "100%",
                      height: "100%",
                      objectFit: "cover",
                    }}
                  />
                ) : null}

                <div
                  style={{
                    position: "absolute",
                    inset: 0,
                    background:
                      "linear-gradient(180deg, rgba(255,255,255,0.04), transparent 30%, rgba(6,16,24,0.34) 100%)",
                  }}
                />
                <div
                  style={{
                    position: "absolute",
                    top: 18,
                    left: 18,
                    display: "flex",
                    gap: 10,
                    alignItems: "center",
                    padding: "8px 12px",
                    borderRadius: 999,
                    background: "rgba(8,18,29,0.46)",
                    backdropFilter: "blur(8px)",
                    zIndex: 1,
                  }}
                >
                  <span
                    style={{
                      width: 10,
                      height: 10,
                      borderRadius: "50%",
                      background: status === "running" ? "#3ddc97" : "#f0b24f",
                      boxShadow: `0 0 14px ${status === "running" ? "#3ddc97" : "#f0b24f"}`,
                    }}
                  />
                  <span
                    style={{
                      fontSize: 12,
                      letterSpacing: "0.1em",
                      textTransform: "uppercase",
                    }}
                  >
                    {status === "running"
                      ? "Live Video Feed"
                      : "No Live Video Frame"}
                  </span>
                </div>

                <div
                  style={{
                    position: "relative",
                    zIndex: 1,
                    width: "100%",
                    padding: 22,
                    display: "grid",
                    gap: 10,
                    background:
                      "linear-gradient(180deg, transparent, rgba(3,10,16,0.82))",
                  }}
                >
                  <div style={{ fontSize: 18, fontWeight: 700 }}>
                    {latestFrame?.model
                      ? `Engagement ${latestFrame.model.engagement.toFixed(2)} | Intensity ${latestFrame.model.intensity.toFixed(2)}`
                      : "Waiting for the first encoded camera frame"}
                  </div>
                  <div
                    style={{
                      maxWidth: 580,
                      lineHeight: 1.6,
                      color: "rgba(243,251,255,0.78)",
                    }}
                  >
                    The stream maybe time delayed depending on your internet
                    connection and hardware.
                  </div>
                </div>
              </div>
            </div>

            <div
              style={{
                padding: 22,
                borderRadius: 28,
                background: "rgba(255,255,255,0.82)",
                backdropFilter: "blur(10px)",
                border: "1px solid rgba(17, 49, 75, 0.08)",
                boxShadow: "0 24px 60px rgba(17, 43, 68, 0.12)",
              }}
            >
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  gap: 16,
                  alignItems: "center",
                  marginBottom: 18,
                }}
              >
                <div>
                  <div
                    style={{
                      fontSize: 12,
                      letterSpacing: "0.12em",
                      textTransform: "uppercase",
                      color: "#6f8598",
                    }}
                  >
                    Session Snapshot
                  </div>
                  <div style={{ fontSize: 26, fontWeight: 700, marginTop: 4 }}>
                    Current Metrics
                  </div>
                </div>
                <div
                  style={{
                    padding: "10px 14px",
                    borderRadius: 999,
                    background: "rgba(17,49,75,0.06)",
                    color: statusTone,
                    fontWeight: 700,
                    textTransform: "capitalize",
                  }}
                >
                  {status}
                </div>
              </div>

              <div
                style={{
                  display: "flex",
                  flexWrap: "wrap",
                  gap: 14,
                }}
              >
                <Badge label="FPS" value={fps.toFixed(1)} />
                <Badge
                  label="Capture Latency"
                  value={`${(latency.capture * 1000).toFixed(1)} ms`}
                />
                <Badge
                  label="FaceMesh Latency"
                  value={`${(latency.facemesh * 1000).toFixed(1)} ms`}
                />
                <Badge
                  label="Resolution"
                  value={`${resolution.w}x${resolution.h}`}
                />
                <Badge label="Frames" value={frames.length} />
                <Badge label="Status" value={status} />
              </div>

              {error ? (
                <p
                  style={{
                    margin: "18px 0 0",
                    padding: "14px 16px",
                    borderRadius: 16,
                    background: "rgba(180, 35, 24, 0.08)",
                    color: "#8f2d22",
                    border: "1px solid rgba(180, 35, 24, 0.14)",
                  }}
                >
                  Pipeline error: {error}
                </p>
              ) : null}
            </div>
          </section>

          <aside
            style={{
              padding: 22,
              borderRadius: 28,
              background: "rgba(255,255,255,0.82)",
              backdropFilter: "blur(10px)",
              border: "1px solid rgba(17, 49, 75, 0.08)",
              boxShadow: "0 24px 60px rgba(17, 43, 68, 0.12)",
              position: "sticky",
              top: 24,
              height: "calc(100vh - 48px)",
              maxHeight: "calc(100vh - 48px)",
              display: "flex",
              flexDirection: "column",
              overflow: "hidden",
            }}
          >
            <div style={{ marginBottom: 18 }}>
              <div
                style={{
                  fontSize: 12,
                  letterSpacing: "0.12em",
                  textTransform: "uppercase",
                  color: "#6f8598",
                }}
              >
                Scrollable Charts
              </div>
              <div style={{ fontSize: 28, fontWeight: 700, marginTop: 4 }}>
                Signal History
              </div>
            </div>

            <div
              style={{
                flex: 1,
                overflowY: "auto",
                paddingRight: 8,
                display: "flex",
                flexDirection: "column",
                gap: 16,
                minHeight: 0,
              }}
            >
              <SignalChart
                data={frames}
                dataKey="model.engagement"
                color="#2f9f7f"
                name="Engagement"
              />
              <SignalChart
                data={frames}
                dataKey="signals.yaw"
                color="#3978b5"
                name="Yaw"
              />
              <SignalChart
                data={frames}
                dataKey="signals.pitch"
                color="#e6842a"
                name="Pitch"
              />
              <SignalChart
                data={frames}
                dataKey="signals.roll"
                color="#4d8f55"
                name="Roll"
              />
              <SignalChart
                data={frames}
                dataKey="signals.avg_EAR"
                color="#d94d4d"
                name="EAR"
              />
              <SignalChart
                data={frames}
                dataKey="signals.mouth_open"
                color="#3f6ee8"
                name="Mouth Open"
              />
            </div>
          </aside>
        </div>
      </main>
    </div>
  );
}
