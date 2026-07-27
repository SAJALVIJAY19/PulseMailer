from sqlalchemy import create_engine, Column, String, Boolean, Integer, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from dotenv import load_dotenv
from datetime import datetime
from uuid import uuid4
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, connect_args={"sslmode": "require"})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    product_name = Column(String(100), nullable=False)
    tone = Column(String(20), nullable=False)
    target_audience = Column(String(500), nullable=False)
    goal = Column(String(50), nullable=False)
    num_variants = Column(Integer, default=1)
    schedule_weekly = Column(Boolean, default=False)
    cached = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    emails = relationship("GeneratedEmail", back_populates="campaign")


class GeneratedEmail(Base):
    __tablename__ = "generated_emails"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    campaign_id = Column(PGUUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=False)
    subject_line = Column(String(78), nullable=False)
    body = Column(Text, nullable=False)
    cta_text = Column(String(200), nullable=False)
    tokens_used = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    campaign = relationship("Campaign", back_populates="emails")


def init_db():
    Base.metadata.create_all(bind=engine)