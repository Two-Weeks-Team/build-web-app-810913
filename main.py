import json

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

from models import ArtifactCard, PlanningProject, PlanningSnapshot, SessionLocal, init_db
from routes import router


app = FastAPI(title="Build Web App API", version="1.0.0")

@app.middleware("http")
async def normalize_api_prefix(request: Request, call_next):
    if request.scope.get("path", "").startswith("/api/"):
        request.scope["path"] = request.scope["path"][4:] or "/"
    return await call_next(request)

app.include_router(router)


def seed_demo_data() -> None:
    db = SessionLocal()
    try:
        existing = db.query(PlanningProject).count()
        if existing > 0:
            return

        seeds = [
            "AI meeting notes summarizer for remote teams",
            "Local service marketplace for independent fitness coaches",
            "Browser-based invoice tracker for freelance designers",
        ]

        for idx, idea in enumerate(seeds, start=1):
            project = PlanningProject(
                name=idea,
                raw_context=idea,
                preferences="Audience: founders; Platform: web; Horizon: 90 days",
                status="saved",
            )
            db.add(project)
            db.flush()

            brief = {
                "summary": f"Structured brief for: {idea}",
                "items": [
                    {
                        "section": "target_users",
                        "title": "Target users",
                        "content": "Primary users who need faster planning outcomes from rough context.",
                        "source_quote": idea,
                    },
                    {
                        "section": "next_actions",
                        "title": "Next actions",
                        "content": "Run a validation sprint and promote top 3 insights into saved artifacts.",
                        "source_quote": "Turn rough input into structured outputs",
                    },
                ],
                "score": 75 + idx,
            }

            snapshot = PlanningSnapshot(
                project_id=project.id,
                version_number=1,
                status="saved",
                summary=brief["summary"],
                brief_json=json.dumps(brief),
                score=brief["score"],
            )
            db.add(snapshot)
            db.flush()

            db.add(
                ArtifactCard(
                    snapshot_id=snapshot.id,
                    card_type="feature_priorities",
                    title="One-pass generation",
                    body="Convert messy notes into a complete brief in one run.",
                    source_quote="instantly receive a structured Product Brief",
                    promoted=True,
                )
            )

        db.commit()
    finally:
        db.close()


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    seed_demo_data()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def root() -> HTMLResponse:
    html = """
    <!doctype html>
    <html>
      <head>
        <meta charset=\"utf-8\" />
        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
        <title>Build Web App API</title>
        <style>
          body { background:#0b1020; color:#e8ecff; font-family:Inter,Arial,sans-serif; margin:0; padding:24px; }
          .card { max-width:980px; margin:0 auto; background:#121a33; border:1px solid #26345f; border-radius:12px; padding:24px; }
          h1 { margin:0 0 8px; font-size:28px; }
          h2 { margin-top:24px; font-size:18px; color:#9fb3ff; }
          p, li { color:#cdd8ff; line-height:1.5; }
          code { background:#1a2447; padding:2px 6px; border-radius:6px; }
          a { color:#7dd3fc; text-decoration:none; }
        </style>
      </head>
      <body>
        <div class=\"card\">
          <h1>Build Web App API</h1>
          <p>Turn rough product ideas into structured, saved planning briefs in one pass.</p>

          <h2>Endpoints</h2>
          <ul>
            <li><code>GET /health</code> — service health check</li>
            <li><code>POST /plan</code> and <code>POST /api/plan</code> — generate brief and save snapshot</li>
            <li><code>POST /insights</code> and <code>POST /api/insights</code> — generate promotable insights</li>
            <li><code>POST /artifacts/promote</code> and <code>POST /api/artifacts/promote</code> — save promoted artifact card</li>
            <li><code>GET /snapshots</code> and <code>GET /api/snapshots</code> — list versioned planning snapshots</li>
          </ul>

          <h2>Tech Stack</h2>
          <p>FastAPI + SQLAlchemy + PostgreSQL-ready models + DigitalOcean Serverless Inference (Claude 4.6 Sonnet via OpenAI-compatible endpoint).</p>

          <h2>Docs</h2>
          <p><a href=\"/docs\">OpenAPI Docs</a> · <a href=\"/redoc\">ReDoc</a></p>
        </div>
      </body>
    </html>
    """
    return HTMLResponse(content=html)
