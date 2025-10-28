from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
from inference import DevOpsChatbot

# Initialize FastAPI app
app = FastAPI(
    title="DevOps Chatbot API",
    description="Intent classification chatbot for DevOps FAQs",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # React default ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model at startup
chatbot = None

@app.on_event("startup")
async def load_model():
    global chatbot
    chatbot = DevOpsChatbot(model_path='models/distilbert-devops-faq')
    print("✅ Model loaded and ready!")

# Request model
class QuestionRequest(BaseModel):
    question: str
    return_confidence: Optional[bool] = True

# Response model
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
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "model_loaded": chatbot is not None}

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: QuestionRequest):
    """Get intent and answer for a question"""
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
