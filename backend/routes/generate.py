from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import CampaignRequest, CampaignResponse, GeneratedEmail as GeneratedEmailModel
from database import get_db, Campaign, GeneratedEmail as GeneratedEmailDB
from chain import generate_emails, calculate_tokens
from cache import generate_cache_key, get_cached_response, set_cached_response
from uuid import uuid4
from datetime import datetime

router = APIRouter()


@router.post("/", response_model=CampaignResponse)
async def create_campaign(request: CampaignRequest, db: Session = Depends(get_db)):
    try:
        cache_key = generate_cache_key(
            request.product_name,
            request.tone,
            request.target_audience,
            request.goal,
            request.num_variants,
        )

        cached_data = get_cached_response(cache_key)

        if cached_data:
            # Cache HIT
            campaign_id = uuid4()
            now = datetime.utcnow()

            db_campaign = Campaign(
                id=campaign_id,
                product_name=request.product_name,
                tone=request.tone,
                target_audience=request.target_audience,
                goal=request.goal,
                num_variants=request.num_variants,
                schedule_weekly=request.schedule_weekly,
                cached=True,
                created_at=now,
            )
            db.add(db_campaign)

            email_models = []
            for email in cached_data["emails"]:
                db_email = GeneratedEmailDB(
                    id=uuid4(),
                    campaign_id=campaign_id,
                    subject_line=email["subject_line"],
                    body=email["body"],
                    cta_text=email["cta_text"],
                    tokens_used=calculate_tokens(email["body"] + " " + email["subject_line"]),
                    created_at=now,
                )
                db.add(db_email)
                email_models.append(
                    GeneratedEmailModel(
                        subject_line=email["subject_line"],
                        body=email["body"],
                        cta_text=email["cta_text"],
                        tokens_used=calculate_tokens(email["body"] + " " + email["subject_line"]),
                    )
                )

            db.commit()

            return CampaignResponse(
                campaign_id=campaign_id,
                product_name=request.product_name,
                emails=email_models,
                cached=True,
                created_at=now,
            )

        # Cache MISS
        result = await generate_emails(
            product_name=request.product_name,
            tone=request.tone,
            target_audience=request.target_audience,
            goal=request.goal,
            num_variants=request.num_variants,
        )

        campaign_id = uuid4()
        now = datetime.utcnow()

        db_campaign = Campaign(
            id=campaign_id,
            product_name=request.product_name,
            tone=request.tone,
            target_audience=request.target_audience,
            goal=request.goal,
            num_variants=request.num_variants,
            schedule_weekly=request.schedule_weekly,
            cached=False,
            created_at=now,
        )
        db.add(db_campaign)

        email_models = []
        for email in result["emails"]:
            tokens = calculate_tokens(email["body"] + " " + email["subject_line"])
            db_email = GeneratedEmailDB(
                id=uuid4(),
                campaign_id=campaign_id,
                subject_line=email["subject_line"],
                body=email["body"],
                cta_text=email["cta_text"],
                tokens_used=tokens,
                created_at=now,
            )
            db.add(db_email)
            email_models.append(
                GeneratedEmailModel(
                    subject_line=email["subject_line"],
                    body=email["body"],
                    cta_text=email["cta_text"],
                    tokens_used=tokens,
                )
            )

        db.commit()

        set_cached_response(cache_key, result)

        return CampaignResponse(
            campaign_id=campaign_id,
            product_name=request.product_name,
            emails=email_models,
            cached=False,
            created_at=now,
        )

    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")
