export default function Badge({ label, value }) {
  // Badges are intentionally simple because the parent layout handles grouping and spacing.
  return (
    <div
      style={{
        padding: "14px 16px",
        borderRadius: 18,
        border: "1px solid rgba(20, 55, 90, 0.12)",
        background: "linear-gradient(180deg, rgba(255,255,255,0.98), rgba(240,247,252,0.94))",
        boxShadow: "0 14px 30px rgba(17, 43, 68, 0.08)",
        minWidth: 130,
      }}
    >
      <div
        style={{
          fontSize: 12,
          textTransform: "uppercase",
          letterSpacing: "0.12em",
          color: "#6b8398",
          marginBottom: 8,
        }}
      >
        {label}
      </div>
      <div
        style={{
          fontSize: 24,
          fontWeight: 700,
          color: "#11314b",
          lineHeight: 1.1,
        }}
      >
        {value}
      </div>
    </div>
  );
}
