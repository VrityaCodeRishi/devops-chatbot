from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime
import uvicorn
import os
from pathlib import Path
from src.inference import DevOpsChatbot

# Initialize FastAPI app
app = FastAPI(
    title="DevOps Chatbot API",
    description="AI-powered DevOps assistant with 96%+ accuracy",
    version=os.getenv("MODEL_VERSION", "1.0.0")
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model at startup
chatbot = None
MODEL_VERSION = os.getenv("MODEL_VERSION", "unknown")

@app.on_event("startup")
async def load_model():
    global chatbot
    model_path = os.getenv("MODEL_PATH", "models/distilbert-devops-faq")
    print(f"🤖 Loading model from: {model_path}")
    print(f"📊 Model version: {MODEL_VERSION}")
    chatbot = DevOpsChatbot(model_path=model_path)
    print("✅ Model loaded and ready!")

# Request/Response models
class QuestionRequest(BaseModel):
    question: str
    return_confidence: Optional[bool] = True
    
    @validator('question')
    def validate_question(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Question cannot be empty')
        if len(v) > 500:
            raise ValueError('Question too long (max 500 characters)')
        return v.strip()

class PredictionResponse(BaseModel):
    question: str
    intent: str
    answer: str
    confidence: float
    model_version: str

# API Routes
@app.get("/")
async def root():
    """Root endpoint - redirect to frontend"""
    return FileResponse("frontend/build/index.html")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model_loaded": chatbot is not None,
        "model_version": MODEL_VERSION,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: QuestionRequest):
    """Get intent and answer for a question"""
    if not chatbot:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        result = chatbot.predict(
            request.question, 
            return_confidence=request.return_confidence
        )
        result['model_version'] = MODEL_VERSION
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

# Serve React frontend static files
frontend_path = Path("frontend/build")
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory="frontend/build/static"), name="static")
    
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        """Serve React app for all other routes"""
        file_path = frontend_path / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(frontend_path / "index.html")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
