import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from app.model import predict_emotion

app = FastAPI(
    title="Emotion Recognition API",
    description="""
    Real-time text emotion recognition API.
    
    • Model: DistilRoBERTa  
    • Dataset: dair-ai/emotion  
    • Emotions: anger, fear, joy, love, sadness, surprise (+ neutral fallback)
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class EmotionRequest(BaseModel):
    text: str = Field(
        ...,
        example="I feel really happy and excited today!"
    )


class EmotionResponse(BaseModel):
    emotion: str = Field(
        example="joy",
        description="The predicted emotion"
    )
    confidence: float = Field(
        example=0.92,
        description="Confidence score for the predicted emotion"
    )
    probabilities: dict[str, float] = Field(
        example={"anger": 0.05, "fear": 0.02, "joy": 0.92, "love": 0.01, "sadness": 0.0, "surprise": 0.0},
        description="Probability scores for all emotions"
    )


@app.get(
    "/",
    summary="Health check",
    description="Check if the API is running"
)
def health_check():
    return {"status": "ok"}


@app.post(
    "/predict",
    response_model=EmotionResponse,
    summary="Predict emotion from text",
    description="Returns the most probable emotion, confidence score, and probabilities for all emotions"
)
def predict_emotion_api(data: EmotionRequest):
    emotion, confidence, probabilities = predict_emotion(data.text)

    return EmotionResponse(
        emotion=emotion,
        confidence=confidence,
        probabilities=probabilities
    )
    
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        reload=False
    )
