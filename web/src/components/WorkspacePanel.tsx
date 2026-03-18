"use client";

import { useState } from "react";

const ideas = [
  "AI meeting notes summarizer for remote teams",
  "Local service marketplace for independent fitness coaches",
  "Browser-based invoice tracker for freelance designers",
  "Neighborhood tool-sharing app for apartment buildings",
  "Lightweight CRM for boutique recruiting agencies"
];

export default function WorkspacePanel({
  onGenerate,
  status,
  error
}: {
  onGenerate: (query: string, preferences: Record<string, string>) => Promise<void>;
  status: "idle" | "loading" | "success" | "error";
  error: string;
}) {
  const [query, setQuery] = useState(
    "We have messy notes from founder interviews, customers say onboarding is confusing, we think there is a B2B SaaS angle but not sure who pays first. Need a launchable scope in 8 weeks with one PM and two engineers."
  );
  const [preferences, setPreferences] = useState({
    audience_type: "Founders + PMs",
    platform_constraints: "Web first",
    business_model: "Subscription",
    complexity_target: "MVP",
    launch_horizon: "8 weeks"
  });

  return (
    <section className="sheet p-4 md:p-5">
      <h2 className="text-xl font-bold">Rough Context Intake Canvas</h2>
      <p className="mt-1 text-sm text-foreground/70">Paste raw notes, transcript fragments, or half-formed strategy text.</p>
      <textarea
        className="mt-3 h-44 w-full rounded-md border border-border bg-white/70 p-3 text-sm outline-none focus:border-primary"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />
      <div className="mt-3 flex flex-wrap gap-2">
        {ideas.map((idea) => (
          <button key={idea} onClick={() => setQuery(idea)} className="rounded-full border bg-card px-3 py-1 text-xs hover:border-primary">
            {idea}
          </button>
        ))}
      </div>
      <div className="mt-4 grid gap-2 sm:grid-cols-2">
        {Object.entries(preferences).map(([key, val]) => (
          <label key={key} className="text-xs">
            <span className="mb-1 block uppercase tracking-wide text-foreground/65">{key.replaceAll("_", " ")}</span>
            <input
              value={val}
              onChange={(e) => setPreferences((p) => ({ ...p, [key]: e.target.value }))}
              className="w-full rounded-md border border-border bg-white/70 px-2 py-1.5 text-sm"
            />
          </label>
        ))}
      </div>
      <div className="mt-4 flex items-center gap-3">
        <button
          onClick={() => onGenerate(query, preferences)}
          className="rounded-md bg-primary px-4 py-2 text-sm font-semibold text-white transition hover:brightness-110"
        >
          {status === "loading" ? "Generating…" : "Generate Brief"}
        </button>
        {status === "success" && <span className="text-sm text-success">Structured brief generated and snapshot saved.</span>}
        {status === "error" && <span className="text-sm text-warning">{error}</span>}
      </div>
    </section>
  );
}
