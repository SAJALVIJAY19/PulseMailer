from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy.orm import Session
from models import CampaignRequest, CampaignResponse, GeneratedEmail as GeneratedEmailModel
from database import get_db, Campaign, GeneratedEmail as GeneratedEmailDB
from chain import generate_emails, calculate_tokens, InvalidInputError
from cache import generate_cache_key, get_cached_response, set_cached_response, check_rate_limit
from uuid import uuid4
from datetime import datetime

router = APIRouter()


@router.post("/", response_model=CampaignResponse)
async def create_campaign(
    http_request: Request,
    request: CampaignRequest,
    db: Session = Depends(get_db),
    x_client_id: str = Header(default=""),
):
    forwarded = http_request.headers.get("x-forwarded-for")
    if forwarded:
        ip = forwarded.split(",")[0].strip()
    else:
        ip = http_request.client.host
    if not check_rate_limit(ip):
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Please wait a minute and try again.",
            headers={"Retry-After": "60"},
        )
    try:
        cache_key = generate_cache_key(
            request.product_name,
            request.brand_description,
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
                brand_description=request.brand_description,
                tone=request.tone,
                target_audience=request.target_audience,
                goal=request.goal,
                num_variants=request.num_variants,
                schedule_weekly=request.schedule_weekly,
                cached=True,
                client_id=x_client_id,
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
                    tokens_used=0,
                    created_at=now,
                )
                db.add(db_email)
                email_models.append(
                    GeneratedEmailModel(
                        subject_line=email["subject_line"],
                        body=email["body"],
                        cta_text=email["cta_text"],
                        tokens_used=0,
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
            brand_description=request.brand_description,
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
            brand_description=request.brand_description,
            tone=request.tone,
            target_audience=request.target_audience,
            goal=request.goal,
            num_variants=request.num_variants,
            schedule_weekly=request.schedule_weekly,
            cached=False,
            client_id=x_client_id,
            created_at=now,
        )
        db.add(db_campaign)

        email_models = []
        emails = result["emails"]
        total_tokens = result.get("total_tokens", 0)
        for email in emails:
            if total_tokens > 0:
                tokens = total_tokens // len(emails)
            else:
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

    except HTTPException:
        raise
    except InvalidInputError:
        raise HTTPException(status_code=422, detail="Please enter a real brand name, description and audience.")
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")
