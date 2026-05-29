from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db, Campaign, GeneratedEmail

router = APIRouter()


@router.get("/")
def get_history(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    campaigns = (
        db.query(Campaign)
        .order_by(Campaign.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    results = []
    for campaign in campaigns:
        emails = (
            db.query(GeneratedEmail)
            .filter(GeneratedEmail.campaign_id == campaign.id)
            .all()
        )
        results.append(
            {
                "campaign_id": str(campaign.id),
                "product_name": campaign.product_name,
                "tone": campaign.tone,
                "goal": campaign.goal,
                "cached": campaign.cached,
                "created_at": campaign.created_at.isoformat(),
                "email_count": len(emails),
                "emails": [
                    {
                        "subject_line": email.subject_line,
                        "body": email.body,
                        "cta_text": email.cta_text,
                    }
                    for email in emails
                ],
            }
        )

    return results
