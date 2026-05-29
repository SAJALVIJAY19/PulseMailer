from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db, Campaign, GeneratedEmail

router = APIRouter()


@router.get("/")
def get_stats(db: Session = Depends(get_db)):
    total_campaigns = db.query(func.count(Campaign.id)).scalar() or 0
    total_emails_generated = db.query(func.count(GeneratedEmail.id)).scalar() or 0
    total_tokens_used = db.query(func.sum(GeneratedEmail.tokens_used)).scalar() or 0
    cached_campaigns = db.query(func.count(Campaign.id)).filter(Campaign.cached == True).scalar() or 0

    if total_campaigns > 0:
        cache_hit_rate = round((cached_campaigns / total_campaigns) * 100, 2)
    else:
        cache_hit_rate = 0.0

    # Tone breakdown
    tone_results = db.query(Campaign.tone, func.count(Campaign.id)).group_by(Campaign.tone).all()
    tone_breakdown = {tone: count for tone, count in tone_results}

    # Goal breakdown
    goal_results = db.query(Campaign.goal, func.count(Campaign.id)).group_by(Campaign.goal).all()
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
