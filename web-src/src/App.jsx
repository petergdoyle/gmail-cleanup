import React, { useEffect, useState } from "react";

// A single downstream-resource status row for the sidebar footer.
// state: 'ok' (green) | 'down' (red) | 'n/a' (grey, not wired yet).
function Status({ label, state }) {
  const color = state === "ok" ? "#16a34a" : state === "down" ? "#dc2626" : "#9ca3af";
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 8,
                  fontSize: ".85rem", color: state === "n/a" ? "#9ca3af" : "#e5e7eb" }}>
      <span style={{ width: 9, height: 9, borderRadius: "50%", background: color }} />
      <span>{label}</span>
      <span style={{ marginLeft: "auto", opacity: .8 }}>{state}</span>
    </div>
  );
}

export default function App() {
  const [health, setHealth] = useState("checking…");
  useEffect(() => {
    fetch("/api/health")
      .then((r) => r.json())
      .then((d) => setHealth(d.ok ? "ok" : "down"))
      .catch(() => setHealth("down"));
  }, []);
  return (
    <div style={{ fontFamily: "system-ui, sans-serif", display: "flex",
                  minHeight: "100vh" }}>
      {/* Left sidebar: nav on top, connection status pinned to the bottom. */}
      <aside style={{ width: 220, background: "#111827", color: "#e5e7eb",
                      display: "flex", flexDirection: "column", padding: "1.25rem" }}>
        <strong style={{ fontSize: "1.05rem" }}>gmail-cleanup</strong>
        <nav style={{ marginTop: "1rem", color: "#9ca3af",
                     fontSize: ".9rem" }}>Home</nav>
        <div style={{ marginTop: "auto", borderTop: "1px solid #374151",
                      paddingTop: ".75rem", display: "grid", gap: 6 }}>
          <div style={{ fontSize: ".7rem", textTransform: "uppercase",
                        letterSpacing: ".05em", color: "#6b7280" }}>Connections</div>
          <Status label="API" state={health === "checking…" ? "n/a" : health} />
        </div>
      </aside>
      {/* Main panel: the brand banner. */}
      <main style={{ flex: 1, padding: "3rem", lineHeight: 1.5 }}>
        <h1 style={{ margin: "0 0 .25rem" }}>gmail-cleanup</h1>
        <p style={{ margin: "0 0 1.5rem", color: "#4b5563" }}>{"a utility to clear out old gmail items"}</p>
        <p style={{ margin: 0, fontSize: ".9rem", color: "#6b7280" }}>
          Scaffolded by raven — replace this page with the real UI.
        </p>
      </main>
    </div>
  );
}
