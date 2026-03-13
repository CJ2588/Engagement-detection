import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
} from "recharts";

export default function SignalChart({ data, dataKey, color, name }) {
  return (
    <div
      style={{
        minHeight: 260,
        padding: 16,
        borderRadius: 22,
        background: "linear-gradient(180deg, rgba(255,255,255,0.98), rgba(243,248,251,0.94))",
        border: "1px solid rgba(17, 49, 75, 0.1)",
        boxShadow: "0 18px 40px rgba(17, 43, 68, 0.08)",
        display: "flex",
        flexDirection: "column",
        flexShrink: 0,
      }}
    >
      <div
        style={{
          fontSize: 13,
          fontWeight: 700,
          letterSpacing: "0.08em",
          textTransform: "uppercase",
          color: "#526b81",
          marginBottom: 8,
        }}
      >
        {name}
      </div>
      <div style={{ flex: 1, minHeight: 190 }}>
        <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <CartesianGrid stroke="rgba(58, 99, 132, 0.12)" vertical={false} />
          <XAxis dataKey="timestamp" tick={{ fill: "#698195", fontSize: 12 }} />
          <YAxis tick={{ fill: "#698195", fontSize: 12 }} width={42} />
          <Tooltip />
          <Line
            type="monotone"
            dataKey={dataKey}
            stroke={color}
            strokeWidth={3}
            name={name}
            dot={false}
            isAnimationActive={false}
          />
        </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
