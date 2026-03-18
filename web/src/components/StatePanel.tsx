export default function StatePanel({ state, error }: { state: "empty" | "loading" | "success" | "error"; error?: string }) {
  if (state === "loading") return <div className="panel p-4 text-sm">Resolving messy text into structured artifact sheets…</div>;
  if (state === "error") return <div className="panel p-4 text-sm text-red-700">Error: {error || "Something went wrong."}</div>;
  if (state === "success") return <div className="panel p-4 text-sm text-success">Success: brief generated, trace attached, and snapshot shelf updated.</div>;
  return <div className="panel p-4 text-sm">Empty state: select a starter example or paste discovery notes to generate your first brief.</div>;
}
