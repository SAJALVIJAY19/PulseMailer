# PulseMailer — AI Email Marketing Platform

> AI-powered email campaign generator built with FastAPI, LangChain, Groq LLM, PostgreSQL, and Redis.

## Tech Stack

| Tool | Purpose |
|------|---------|
| FastAPI | REST API backend |
| Pydantic | Request/response validation |
| LangChain | LLM orchestration pipeline |
| Groq LLM (Llama 3) | AI email generation |
| PostgreSQL (Supabase) | Campaign storage |
| Redis (Upstash) | Response caching |
| APScheduler | Weekly campaign automation |
| HTML + Tailwind CSS | Frontend UI |

## Features

- **A/B Variants**: Generate up to 5 unique highly-targeted email variants in a single request.
- **Weekly Scheduling**: Set campaigns to run automatically every week with built-in APScheduler automation.
- **Redis Response Caching**: Sub-millisecond response times for identical generation requests with cache hit metrics.
- **Analytics Dashboard**: Comprehensive charts showing token consumption, cache hit rate, tone breakdowns, and campaign goals.
- **Campaign History**: Browse, search, filter, and review all historically generated campaigns and email variants.
- **Pydantic Validation**: Robust input and schema validations protecting LLM prompt boundaries.
- **REST API**: Structured FastAPI backend with clean routing, error-handling, and database models.
- **Glassmorphism UI**: Beautiful, interactive visual design featuring modern gradients, clean typography, and micro-animations.

## Project Structure

```
mailcraft-ai/
├── backend/
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── generate.py      # /generate API endpoint
│   │   ├── history.py       # /history API endpoint
│   │   └── stats.py         # /stats analytics endpoint
│   ├── cache.py             # Redis connection & cache management
│   ├── chain.py             # LangChain & Groq LLM integration
│   ├── database.py          # SQLAlchemy PostgreSQL connection & tables
│   ├── init.py              # Database table initializer script
│   ├── main.py              # FastAPI main entrypoint and scheduler lifespan
│   ├── models.py            # Pydantic request & response schemas
│   └── scheduler.py         # Weekly APScheduler background workers
├── frontend/
│   ├── analytics.html       # Analytics dashboard user interface
│   ├── dashboard.html       # Saved campaigns history dashboard
│   ├── index.html           # Main AI campaign builder & generator UI
│   └── landing.html         # Premium platform showcase & marketing landing page
├── .env                     # Local environment keys & credentials
└── requirements.txt         # Project dependencies
```

## Getting Started

### Prerequisites

- Python 3.9+
- Groq API key (free at console.groq.com)
- Supabase account (free at supabase.com)
- Upstash Redis (free at upstash.com)

### Installation

Step by step:

1. Clone the repo:
   ```bash
   git clone https://github.com/yourusername/mailcraft-ai.git
   ```
2. Navigate to the backend directory:
   ```bash
   cd mailcraft-ai/backend
   ```
3. Install required Python packages:
   ```bash
   pip install -r ../requirements.txt
   ```
4. Copy the environment template and fill in keys:
   ```bash
   cp .env.example .env
   # Open .env and add GROQ_API_KEY, DATABASE_URL, UPSTASH_REDIS_REST_URL, and UPSTASH_REDIS_REST_TOKEN
   ```
5. Initialize PostgreSQL database tables:
   ```bash
   python init.py
   ```
6. Run the uvicorn development server:
   ```bash
   uvicorn main:app --reload
   ```

### Usage

- Open `frontend/landing.html` in your favorite web browser.
- Click **"Get Started Free"** to go to the generator dashboard (`index.html`).
- Fill in the form details (product name, audience, tone, goal, variants, scheduling) and click **"Generate Campaign"**.
- View history of all generated campaigns and variants at `dashboard.html`.
- View performance metrics, tokens, and cache distribution at `analytics.html`.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check and server status |
| POST | `/generate/` | Generate a new email campaign |
| GET | `/history/` | Get historical campaign list |
| GET | `/stats/` | Get analytics metrics & tone stats |

## How It Works

User fills out the form → Pydantic schema validates the payload → Redis cache lookup checks for existing prompt results → LangChain compiles the tailored prompt → Groq LLM generates multi-variant email structure (subject, body, CTA) → PostgreSQL saves the campaign details and variants → Campaign response is returned to the client and rendered smoothly in the browser.

## Environment Variables

Copy the structure below into your `.env` file:

```env
GROQ_API_KEY="your_groq_api_key"
DATABASE_URL="postgresql://username:password@hostname:port/dbname"
UPSTASH_REDIS_REST_URL="your_upstash_redis_rest_url"
UPSTASH_REDIS_REST_TOKEN="your_upstash_redis_rest_token"
```

## Screenshots

<!-- Add screenshots here -->

## Author

Built by **Raghav** as a top SDE fresher project.

Demonstrates production practices in:
- REST API Design and Development
- LLM Pipeline Orchestration (LangChain & Groq)
- Real-time caching (Redis) & background automation (APScheduler)
- Relational schema design & persistence (Supabase PostgreSQL)
- Premium animated frontend development (HTML, Tailwind CSS, Vanilla JS)

---

Built with FastAPI · LangChain · Groq · PostgreSQL · Redis
