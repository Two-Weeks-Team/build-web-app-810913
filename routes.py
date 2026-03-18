import json
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import desc
from sqlalchemy.orm import Session

from ai_service import generate_insights, generate_plan
from models import ArtifactCard, PlanningProject, PlanningSnapshot, SessionLocal


router = APIRouter()


class PlanRequest(BaseModel):
    query: str
    preferences: str = ""


class InsightsRequest(BaseModel):
    selection: str
    context: str = ""


class PromoteArtifactRequest(BaseModel):
    snapshot_id: int
    card_type: str
    title: str
    body: str
    source_quote: Optional[str] = None


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/plan")
@router.post("/plan")
async def plan(payload: PlanRequest, db: Session = Depends(get_db)):
    ai_output = await generate_plan(payload.query, payload.preferences)

    title = payload.query.strip().split("\n")[0][:120] or "Untitled planning brief"
    project = PlanningProject(
        name=title,
        raw_context=payload.query,
        preferences=payload.preferences,
        status="draft",
    )
    db.add(project)
    db.flush()

    latest = (
        db.query(PlanningSnapshot)
        .filter(PlanningSnapshot.project_id == project.id)
        .order_by(desc(PlanningSnapshot.version_number))
        .first()
    )
    next_version = 1 if latest is None else latest.version_number + 1

    snapshot = PlanningSnapshot(
        project_id=project.id,
        version_number=next_version,
        status="draft",
        summary=ai_output.get("summary", ""),
        brief_json=json.dumps(ai_output),
        score=int(ai_output.get("score", 75)),
    )
    db.add(snapshot)
    db.flush()

    items = ai_output.get("items", [])
    for item in items:
        db.add(
            ArtifactCard(
                snapshot_id=snapshot.id,
                card_type=item.get("section", "insight"),
                title=item.get("title", "Insight"),
                body=item.get("content", ""),
                source_quote=item.get("source_quote", ""),
                promoted=False,
            )
        )

    db.commit()

    return {
        "summary": ai_output.get("summary", ""),
        "items": ai_output.get("items", []),
        "score": int(ai_output.get("score", 75)),
        "snapshot_id": snapshot.id,
        "project_id": project.id,
        "status": "draft",
        "created_at": datetime.utcnow().isoformat(),
    }


@router.post("/insights")
@router.post("/insights")
async def insights(payload: InsightsRequest):
    data = await generate_insights(payload.selection, payload.context)
    return {
        "insights": data.get("insights", []),
        "next_actions": data.get("next_actions", []),
        "highlights": data.get("highlights", []),
    }


@router.post("/artifacts/promote")
@router.post("/artifacts/promote")
async def promote_artifact(payload: PromoteArtifactRequest, db: Session = Depends(get_db)):
    snapshot = db.query(PlanningSnapshot).filter(PlanningSnapshot.id == payload.snapshot_id).first()
    if not snapshot:
        raise HTTPException(status_code=404, detail="Snapshot not found")

    card = ArtifactCard(
        snapshot_id=payload.snapshot_id,
        card_type=payload.card_type,
        title=payload.title,
        body=payload.body,
        source_quote=payload.source_quote,
        promoted=True,
    )
    db.add(card)
    db.commit()
    db.refresh(card)

    return {
        "artifact_id": card.id,
        "snapshot_id": card.snapshot_id,
        "card_type": card.card_type,
        "title": card.title,
        "body": card.body,
        "source_quote": card.source_quote,
        "promoted": card.promoted,
    }


@router.get("/snapshots")
@router.get("/snapshots")
def list_snapshots(db: Session = Depends(get_db)):
    rows: List[PlanningSnapshot] = db.query(PlanningSnapshot).order_by(desc(PlanningSnapshot.created_at)).limit(30).all()
    result = []
    for row in rows:
        cards = db.query(ArtifactCard).filter(ArtifactCard.snapshot_id == row.id).all()
        result.append(
            {
                "snapshot_id": row.id,
                "project_id": row.project_id,
                "version_number": row.version_number,
                "status": row.status,
                "summary": row.summary,
                "score": row.score,
                "created_at": row.created_at.isoformat(),
                "artifacts": [
                    {
                        "id": c.id,
                        "card_type": c.card_type,
                        "title": c.title,
                        "body": c.body,
                        "source_quote": c.source_quote,
                        "promoted": c.promoted,
                    }
                    for c in cards
                ],
            }
        )
    return {"snapshots": result}
