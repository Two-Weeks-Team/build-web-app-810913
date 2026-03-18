export type PlanRequest = { query: string; preferences: string };
export type PlanResponse = { summary: string; items: string[]; score: number };

export type InsightsRequest = { selection: string; context: string };
export type InsightsResponse = { insights: string[]; next_actions: string[]; highlights: string[] };

// Used by CollectionPanel + legacy components (kept minimal for build compatibility)
export type PlanningSnapshot = {
  id: number;
  title: string;
  status: string;
  created_at: string;
  promoted_insights: string[];
};

export async function generatePlan(payload: PlanRequest): Promise<PlanResponse> {
  const res = await fetch("/api/plan", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error("Could not generate plan");
  return res.json();
}

export async function generateInsights(payload: InsightsRequest): Promise<InsightsResponse> {
  const res = await fetch("/api/insights", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error("Could not fetch insights");
  return res.json();
}
