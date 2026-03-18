"use client";

import { useMemo, useState } from "react";
import Hero from "@/components/Hero";
import FeaturePanel from "@/components/FeaturePanel";
import StatsStrip from "@/components/StatsStrip";
import StatePanel from "@/components/StatePanel";
import { generatePlan, generateInsights, PlanResponse, InsightsResponse } from "@/lib/api";

const seeds = [
  "AI meeting notes summarizer for remote teams",
  "Local service marketplace for independent fitness coaches",
  "Browser-based invoice tracker for freelance designers",
  "Neighborhood tool-sharing app for apartment buildings",
  "Lightweight CRM for boutique recruiting agencies"
];

export default function Page() {
  const [query, setQuery] = useState("Messy notes: We keep losing context after discovery calls. Maybe a product-planning studio where PMs paste raw interviews, constraints like B2B + mobile-first + 6-week launch, and instantly get a polished brief with priorities and next steps.");
  const [preferences, setPreferences] = useState("Audience: founders + PMs; Platform: web-first; Complexity: medium; Horizon: 6 weeks");
  const [plan, setPlan] = useState<PlanResponse | null>(null);
  const [insights, setInsights] = useState<InsightsResponse | null>(null);
  const [status, setStatus] = useState<"empty" | "loading" | "success" | "error">("empty");
  const [error, setError] = useState<string>("");

  const stats = useMemo(() => ({ runs: 4, saved: 3, promoted: insights?.insights.length ?? 2 }), [insights]);

  const onGenerate = async () => {
    setStatus("loading");
    setError("");
    try {
      const p = await generatePlan({ query, preferences });
      setPlan(p);
      const i = await generateInsights({ selection: p.summary, context: query });
      setInsights(i);
      setStatus("success");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Generation failed");
      setStatus("error");
    }
  };

  return (
    <main className="min-h-screen p-4 md:p-8">
      <div className="mx-auto max-w-7xl space-y-4">
        <Hero />
        <StatsStrip runs={stats.runs} saved={stats.saved} promoted={stats.promoted} />

        <section className="grid gap-4 lg:grid-cols-2">
          <div className="panel p-4">
            <h2 className="text-xl font-semibold">Rough context intake canvas</h2>
            <p className="text-sm text-muted-foreground">Paste-or-drop your scraps, then apply lightweight constraints.</p>
            <textarea className="mt-3 h-44 w-full rounded-md border border-border bg-card p-3" value={query} onChange={(e) => setQuery(e.target.value)} />
            <textarea className="mt-3 h-20 w-full rounded-md border border-border bg-card p-3" value={preferences} onChange={(e) => setPreferences(e.target.value)} />
            <div className="mt-3 flex flex-wrap gap-2">
              {seeds.map((s) => (
                <button key={s} className="rounded-full border border-border px-3 py-1 text-xs hover:border-primary" onClick={() => setQuery(s)}>{s}</button>
              ))}
            </div>
            <button className="mt-4 rounded-md bg-primary px-4 py-2 text-primary-foreground" onClick={onGenerate}>Generate Brief</button>
          </div>

          <FeaturePanel plan={plan} insights={insights} />
        </section>

        <StatePanel state={status} error={error} />
      </div>
    </main>
  );
}
