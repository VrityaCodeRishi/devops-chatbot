from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn
from inference import DevOpsChatbot

app = FastAPI(
    title="DevOps Chatbot API",
    description="Intent classification chatbot for DevOps FAQs",
    version="1.0.0"
)

chatbot = None

@app.on_event("startup")
async def load_model():
    global chatbot
    chatbot = DevOpsChatbot(model_path='models/distilbert-devops-faq')
    print("Model loaded and ready!")

class QuestionRequest(BaseModel):
    question: str
    return_confidence: Optional[bool] = True

class PredictionResponse(BaseModel):
    question: str
    intent: str
    answer: str
    confidence: float

@app.get("/")
async def root():
    return {
        "message": "DevOps Chatbot API",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: QuestionRequest):
    if not chatbot:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    try:
        result = chatbot.predict(
            request.question, 
            return_confidence=request.return_confidence
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
