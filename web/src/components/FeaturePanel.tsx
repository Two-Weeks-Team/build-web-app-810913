"use client";

import { InsightsResponse, PlanResponse } from "@/lib/api";

export default function FeaturePanel({ plan, insights }: { plan: PlanResponse | null; insights: InsightsResponse | null }) {
  return (
    <section className="panel p-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">Structured Product Brief sheet</h2>
        <span className="rounded-full border border-success px-2 py-0.5 text-xs text-success">Draft</span>
      </div>
      {plan ? (
        <div className="mt-3 space-y-3">
          <p className="rounded-md bg-muted p-3 text-sm">{plan.summary}</p>
          <div>
            <h3 className="text-sm font-semibold">Feature Priorities</h3>
            <ul className="mt-1 list-disc pl-5 text-sm">
              {plan.items.map((item) => <li key={item}>{item}</li>)}
            </ul>
          </div>
          {insights && (
            <div>
              <h3 className="text-sm font-semibold">Source-to-output trace highlights</h3>
              <div className="mt-1 flex flex-wrap gap-2">
                {insights.highlights.map((h) => <span key={h} className="rounded bg-accent/30 px-2 py-1 text-xs">{h}</span>)}
              </div>
            </div>
          )}
        </div>
      ) : (
        <p className="mt-4 text-sm text-gray-600">Run one-pass generation to populate target users, problem framing, workflow map, assumptions, and next actions.</p>
      )}
    </section>
  );
}
