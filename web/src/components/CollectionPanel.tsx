"use client";

import type { PlanningSnapshot } from "@/lib/api";

export default function CollectionPanel({
  snapshots,
  activeSnapshotId,
  onOpenSnapshot
}: {
  snapshots: PlanningSnapshot[];
  activeSnapshotId: number | null;
  onOpenSnapshot: (id: number) => void;
}) {
  return (
    <section className="sheet p-4 md:p-5">
      <h2 className="text-xl font-bold">Versioned Results Shelf</h2>
      <p className="mt-1 text-sm text-foreground/70">Saved planning snapshots and promoted insights with instant reopen.</p>
      <div className="mt-3 space-y-2">
        {snapshots.map((s) => (
          <button
            key={s.id}
            onClick={() => onOpenSnapshot(s.id)}
            className={`w-full rounded-lg border p-3 text-left transition ${
              activeSnapshotId === s.id ? "border-primary bg-primary/5" : "bg-white/70 hover:border-primary/60"
            }`}
          >
            <div className="flex items-center justify-between">
              <p className="font-semibold text-sm">{s.title}</p>
              <span className="text-xs uppercase">{s.status}</span>
            </div>
            <p className="mt-1 text-xs text-foreground/65">{new Date(s.created_at).toLocaleString()}</p>
            <div className="mt-2 flex flex-wrap gap-1">
              {s.promoted_insights.slice(0, 2).map((i) => (
                <span key={i} className="rounded-full border px-2 py-0.5 text-[11px]">
                  {i}
                </span>
              ))}
            </div>
          </button>
        ))}
      </div>
    </section>
  );
}
