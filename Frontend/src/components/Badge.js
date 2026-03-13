export default function Badge({ label, value }) {
  return (
    <div style={{ margin: 5, padding: 8, border: "1px solid #ccc", borderRadius: 5 }}>
      <strong>{label}:</strong> {value}
    </div>
  );
}