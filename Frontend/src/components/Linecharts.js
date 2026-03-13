import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";

export default function SignalChart({ data, dataKey, color, name }) {
  return (
    <LineChart width={400} height={200} data={data}>
      <CartesianGrid stroke="#ccc" />
      <XAxis dataKey="timestamp" />
      <YAxis />
      <Tooltip />
      <Line
        type="monotone"
        dataKey={dataKey}
        stroke={color}
        name={name}
        dot={false}
        isAnimationActive={false}
      />
    </LineChart>
  );
}
