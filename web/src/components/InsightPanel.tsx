"use client";

import type { PlanResponse, PlanningSnapshot } from "@/lib/api";

export default function InsightPanel({
  result,
  activeSnapshot,
  status,
  onPromoteInsight
}: {
  result: PlanResponse | null;
  activeSnapshot: PlanningSnapshot | null;
  status: "idle" | "loading" | "success" | "error";
  onPromoteInsight: (text: string) => Promise<void>;
}) {
  return (
    <section className="sheet p-4 md:p-5">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold">Structured Product Brief Sheet</h2>
        <span className="rounded border bg-muted px-2 py-1 text-xs uppercase tracking-wide">{activeSnapshot?.status ?? "draft"}</span>
      </div>
      {status === "loading" && <p className="mt-4 text-sm">Resolving rough input into target users, priorities, and actions…</p>}
      {!result && status !== "loading" && (
        <p className="mt-4 text-sm text-foreground/70">Run generation to populate Product Brief, Workflow Map, and Feature Priorities.</p>
      )}
      {result && (
        <div className="mt-4 space-y-3">
          <p className="text-sm font-semibold">{result.summary}</p>
          {result.items.map((item) => (
            <article key={item.section} className="rounded-lg border bg-white/70 p-3">
              <h3 className="font-semibold">{item.section}</h3>
              <p className="mt-1 text-sm">{item.content}</p>
              <div className="mt-2 rounded bg-accent/20 p-2 text-xs">
                Trace: {item.source_quotes.slice(0, 1).join(" · ")}
              </div>
              <button
                onClick={() => onPromoteInsight(item.content)}
                className="mt-2 text-xs font-semibold text-primary underline underline-offset-2"
              >
                Promote to Saved Artifact
              </button>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
