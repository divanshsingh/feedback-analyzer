from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client()

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Server is listening..."}

class Review(BaseModel):
    text : str

class Analysis(BaseModel):
    label: str
    score: int
    theme: str

@app.post("/analyze", response_model=Analysis)
def analyze(review: Review):
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=(
            "You are a customer feedback analyst.\n"
            "Analyze the following customer review and classify its sentiment.\n"
            "Return these fields:\n"
            "- label: 'positive', 'negative', or 'neutral'\n"
            "- score: integer from 1 (very bad) to 5 (very good)\n"
            "- theme: one lowercase word describing the main topic "
            "(e.g., delivery, taste, price, service, quality).\n"
            "If the sentiment is unclear, use 'neutral'. "
            "If the main topic is unclear, use 'other'.\n"
            "Example: Review: 'Great food and friendly staff.'\n"
            "Output: label=positive, score=5, theme=service\n"
            f"Review: {review.text}"
        ),
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=Analysis,
        ),
    )
    return response.parsed