from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
import os
import json

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.7,
    api_key=os.getenv("GROQ_API_KEY"),
)

EMAIL_PROMPT = PromptTemplate(
    input_variables=["product_name", "tone", "target_audience", "goal", "num_variants"],
    template="""You are an expert email marketing copywriter.

Generate {num_variants} unique marketing email(s) for the following:

Product/Brand: {product_name}
Target Audience: {target_audience}
Email Tone: {tone}
Campaign Goal: {goal}

For each email variant, you MUST respond in this exact JSON format:
{{
  "emails": [
    {{
      "subject_line": "compelling subject line under 78 characters",
      "body": "full email body text minimum 50 words",
      "cta_text": "call to action button text"
    }}
  ]
}}

Rules:
- Return ONLY valid JSON, no extra text, no markdown, no code blocks
- Each email must be unique and creative
- subject_line must be under 78 characters
- body must be at least 50 words
- cta_text must be short and action-oriented (max 5 words)
- Generate exactly {num_variants} email(s) in the emails array""",
)


async def generate_emails(
    product_name: str,
    tone: str,
    target_audience: str,
    goal: str,
    num_variants: int = 1,
) -> dict:
    try:
        formatted_prompt = EMAIL_PROMPT.format(
            product_name=product_name,
            tone=tone,
            target_audience=target_audience,
            goal=goal,
            num_variants=num_variants,
        )
        response = await llm.ainvoke(formatted_prompt)
        text = response.content.strip()

        # Remove markdown code blocks if present
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        parsed = json.loads(text)
        return parsed
    except Exception as e:
        raise ValueError(f"LLM generation failed: {e}")


def calculate_tokens(text: str) -> int:
    return len(text.split())
