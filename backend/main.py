from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel
import os

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

class Question(BaseModel):
    question: str
    concept: str
    expected_concepts: list[str]

class AnswerEvaluation(BaseModel):
    score: int
    understanding: str
    demonstrated_concepts: list[str]
    missing_concepts: list[str]
    misconceptions: list[str]
    explanation: str


class EvaluationResponse(BaseModel):
    evaluations: list[AnswerEvaluation]

class QuestionsResponse(BaseModel):
    questions: list[Question]

class EvaluationRequest(BaseModel):
    questions: list[Question]
    answers: list[str]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Welcome to the FastAPI application!"}

@app.get("/generate-questions")
def generate_questions():
    return {
        "questions": [
            "What is a List in Java?",
            "What is the a Set in Java?",
            "What is a Map in Java?",
            "What is HashMap?",
            "What is the TreeMap?",
        ]
    }

@app.get("/test-gemini")
def test_gemini():
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents = "Say Hello in one Short sentence."
    )
    return {
        "response": response.text
    }

@app.get("/generate-ai-questions")
def generate_ai_questions():
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="""
        Generate exactly 5 beginner-level questions about Java Collections.

        Cover these concepts:
        1. List
        2. Set
        3. Map
        4. HashMap
        5. TreeMap

        For each question provide:
        - question: the question text
        - concept: the main concept being tested
        - expected_concepts: the important concepts a good answer should demonstrate

        Do not provide answers.
        Do not provide explanations.
        """,
        config={
            "response_mime_type": "application/json",
            "response_schema": QuestionsResponse,
        }
    )

    result = QuestionsResponse.model_validate_json(response.text)

    return result

@app.post("/evaluate-answers")
def evaluate_answers(data: EvaluationRequest):

    prompt = f"""
    You are an educational answer evaluator.

    Evaluate each student's answer based on the question and expected concepts.

    Rules:
    - Evaluate the meaning of the answer, not exact keyword matching.
    - Identify which expected concepts the student demonstrated.
    - Identify which expected concepts are missing.
    - Identify factual misconceptions.
    - Give a score from 0 to 100.
    - Use understanding values: "strong", "partial", or "weak".
    - Do not assume that a missing concept means the student completely does not know it.
    - Be fair and concise.

    Student assessment:

    {[
        {
            "question": q.question,
            "concept": q.concept,
            "expected_concepts": q.expected_concepts,
            "student_answer": data.answers[i] if i < len(data.answers) else ""
        }
        for i, q in enumerate(data.questions)
    ]}
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": EvaluationResponse,
        }
    )

    result = EvaluationResponse.model_validate_json(response.text)

    return result

