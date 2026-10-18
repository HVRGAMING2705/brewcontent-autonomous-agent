export default function NotFound() {
  return (
    <div
      style={{
        display: "flex",
        height: "100vh",
        alignItems: "center",
        justifyContent: "center",
        flexDirection: "column",
        gap: 12,
        fontFamily: "system-ui, sans-serif",
        background: "#0f0f12",
        color: "#e8e8ea",
      }}
    >
      <div style={{ fontSize: 64 }}>🍺</div>
      <h1 style={{ margin: 0 }}>Page not found</h1>
      <p style={{ color: "#9a9aa3", margin: 0 }}>
        This page slipped off the brew log.
      </p>
      <a href="/" style={{ color: "#d8a24a", marginTop: 8 }}>
        ← Back to BrewContent
      </a>
    </div>
  );
}
