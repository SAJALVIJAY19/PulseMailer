from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db, Campaign, GeneratedEmail

router = APIRouter()


@router.get("/")
def get_stats(db: Session = Depends(get_db), x_client_id: str = Header(default="")):
    if not x_client_id:
        return {
            "total_campaigns": 0,
            "total_emails_generated": 0,
            "total_tokens_used": 0,
            "cached_campaigns": 0,
            "cache_hit_rate": 0.0,
            "tone_breakdown": {},
            "goal_breakdown": {},
        }

    total_campaigns = db.query(func.count(Campaign.id)).filter(Campaign.client_id == x_client_id).scalar() or 0
    total_emails_generated = (
        db.query(func.count(GeneratedEmail.id))
        .join(Campaign, GeneratedEmail.campaign_id == Campaign.id)
        .filter(Campaign.client_id == x_client_id)
        .scalar()
        or 0
    )
    total_tokens_used = (
        db.query(func.sum(GeneratedEmail.tokens_used))
        .join(Campaign, GeneratedEmail.campaign_id == Campaign.id)
        .filter(Campaign.client_id == x_client_id)
        .scalar()
        or 0
    )
    cached_campaigns = (
        db.query(func.count(Campaign.id))
        .filter(Campaign.client_id == x_client_id, Campaign.cached == True)
        .scalar()
        or 0
    )

    if total_campaigns > 0:
        cache_hit_rate = round((cached_campaigns / total_campaigns) * 100, 2)
    else:
        cache_hit_rate = 0.0

    # Tone breakdown
    tone_results = (
        db.query(Campaign.tone, func.count(Campaign.id))
        .filter(Campaign.client_id == x_client_id)
        .group_by(Campaign.tone)
        .all()
    )
    tone_breakdown = {tone: count for tone, count in tone_results}

    # Goal breakdown
    goal_results = (
        db.query(Campaign.goal, func.count(Campaign.id))
        .filter(Campaign.client_id == x_client_id)
        .group_by(Campaign.goal)
        .all()
    )
    goal_breakdown = {goal: count for goal, count in goal_results}

    return {
        "total_campaigns": total_campaigns,
        "total_emails_generated": total_emails_generated,
        "total_tokens_used": total_tokens_used,
        "cached_campaigns": cached_campaigns,
        "cache_hit_rate": cache_hit_rate,
        "tone_breakdown": tone_breakdown,
        "goal_breakdown": goal_breakdown,
    }
