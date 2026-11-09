from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
from database import SessionLocal, Campaign
from chain import generate_emails, calculate_tokens, InvalidInputError
from database import GeneratedEmail as GeneratedEmailDB
from uuid import uuid4
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def run_scheduled_campaigns():
    logger.info("Running scheduled weekly campaigns...")
    db: Session = SessionLocal()
    try:
        campaigns = db.query(Campaign).filter(Campaign.schedule_weekly == True).all()
        for campaign in campaigns:
            try:
                # Call await generate_emails() with campaign's details
                result = await generate_emails(
                    product_name=campaign.product_name,
                    brand_description=campaign.brand_description or "",
                    tone=campaign.tone,
                    target_audience=campaign.target_audience,
                    goal=campaign.goal,
                    num_variants=campaign.num_variants,
                )

                campaign_id = uuid4()
                now = datetime.utcnow()

                # Create new Campaign row with schedule_weekly=False
                # so it won't be picked up again next week
                new_campaign = Campaign(
                    id=campaign_id,
                    product_name=campaign.product_name,
                    brand_description=campaign.brand_description or "",
                    tone=campaign.tone,
                    target_audience=campaign.target_audience,
                    goal=campaign.goal,
                    num_variants=campaign.num_variants,
                    schedule_weekly=False,
                    cached=False,
                    client_id=campaign.client_id,
                    created_at=now,
                )
                db.add(new_campaign)

                # Save each generated email linked to new campaign_id
                emails = result.get("emails", [])
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

                db.commit()
                logger.info(f"Scheduled campaign generated for {campaign.product_name}")
            except InvalidInputError as inv_err:
                db.rollback()
                logger.warning(f"Invalid input for scheduled campaign {campaign.product_name}: {inv_err}")
            except Exception as cam_err:
                db.rollback()
                logger.error(f"Failed to generate scheduled campaign for {campaign.product_name}: {cam_err}")
    except Exception as e:
        logger.error(f"Error occurred in run_scheduled_campaigns: {e}")
    finally:
        db.close()


def start_scheduler():
    scheduler.add_job(
        run_scheduled_campaigns,
        trigger=CronTrigger(day_of_week="mon", hour=9, minute=0),
        id="weekly_campaigns",
        replace_existing=True,
        misfire_grace_time=3600,
        coalesce=True,
    )
    scheduler.start()
    logger.info("Scheduler started — weekly campaigns enabled")


def stop_scheduler():
    scheduler.shutdown()
