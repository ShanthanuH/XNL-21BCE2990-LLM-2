
import os
import time
import json
import logging
import torch
import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from datetime import datetime, timedelta
import numpy as np

# Setup logging
logging.basicConfig(
    level=getattr(logging, os.environ.get("LOG_LEVEL", "INFO")),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("model-server")

# Initialize application
app = FastAPI(
    title="BLOOM Sentiment Analysis API",
    description="API for sentiment analysis using fine-tuned BLOOM model",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security schemes
api_key_header = APIKeyHeader(name="X-API-Key")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Metrics
REQUESTS = Counter("http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"])
LATENCY = Histogram("http_request_duration_seconds", "HTTP request latency", ["method", "endpoint"])
PREDICTIONS = Counter("model_predictions_total", "Total model predictions", ["class"])

# Input/Output models
class SentimentRequest(BaseModel):
    text: str
    include_metadata: Optional[bool] = False

class BatchSentimentRequest(BaseModel):
    texts: List[str]
    include_metadata: Optional[bool] = False

class SentimentResponse(BaseModel):
    text: str
    sentiment: str
    score: float
    processing_time: float
    metadata: Optional[Dict] = None

class BatchSentimentResponse(BaseModel):
    results: List[SentimentResponse]
    processing_time: float

# Global variables
MODEL = None
TOKENIZER = None
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
MAX_BATCH_SIZE = int(os.environ.get("MAX_BATCH_SIZE", 32))
API_KEYS = {
    "test-key-1": "service-1",
    "test-key-2": "service-2",
    # In production, these would be securely loaded from a vault or environment
}

# Load the model
def load_model():
    global MODEL, TOKENIZER

    model_path = os.environ.get("MODEL_PATH", "/models/bloom-finetuned-sentiment")
    logger.info(f"Loading model from {model_path}")

    try:
        start_time = time.time()

        # Load tokenizer and model
        TOKENIZER = AutoTokenizer.from_pretrained(model_path)
        MODEL = AutoModelForSequenceClassification.from_pretrained(model_path)
        MODEL.to(DEVICE)
        MODEL.eval()

        logger.info(f"Model loaded successfully in {time.time() - start_time:.2f} seconds")
        return True
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        return False

# Security dependency
async def verify_api_key(api_key: str = Depends(api_key_header)):
    if api_key not in API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )
    return api_key

# Request timing middleware
@app.middleware("http")
async def add_timing_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    # Record metrics
    endpoint = request.url.path
    method = request.method
    status_code = response.status_code

    REQUESTS.labels(method=method, endpoint=endpoint, status=status_code).inc()
    LATENCY.labels(method=method, endpoint=endpoint).observe(process_time)

    response.headers["X-Process-Time"] = str(process_time)
    return response

# Health check endpoint
@app.get("/health")
async def health():
    if MODEL is None or TOKENIZER is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return {"status": "healthy", "device": str(DEVICE)}

# Metrics endpoint
@app.get("/metrics")
async def metrics():
    return JSONResponse(
        content=generate_latest().decode("utf-8"),
        media_type=CONTENT_TYPE_LATEST,
    )

# Prediction endpoint
@app.post("/predict", response_model=SentimentResponse, dependencies=[Depends(verify_api_key)])
async def predict(request: SentimentRequest):
    if MODEL is None or TOKENIZER is None:
        if not load_model():
            raise HTTPException(status_code=503, detail="Model not loaded and could not be loaded")

    start_time = time.time()

    try:
        # Tokenize
        inputs = TOKENIZER(request.text, return_tensors="pt", truncation=True, max_length=512)
        inputs = {k: v.to(DEVICE) for k, v in inputs.items()}

        # Inference
        with torch.no_grad():
            outputs = MODEL(**inputs)

        # Process results
        scores = torch.nn.functional.softmax(outputs.logits, dim=1)
        predicted_class = torch.argmax(scores, dim=1).item()
        predicted_score = scores[0][predicted_class].item()

        # Map to sentiment label
        sentiment = "Positive" if predicted_class == 1 else "Negative"

        # Increment prediction counter
        PREDICTIONS.labels(class=sentiment).inc()

        # Prepare response
        processing_time = time.time() - start_time
        response = {
            "text": request.text,
            "sentiment": sentiment,
            "score": predicted_score,
            "processing_time": processing_time
        }

        # Add metadata if requested
        if request.include_metadata:
            response["metadata"] = {
                "model": os.path.basename(os.environ.get("MODEL_PATH", "bloom-finetuned")),
                "timestamp": datetime.now().isoformat(),
                "device": str(DEVICE),
                "version": "1.0.0"
            }

        return response

    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

# Batch prediction endpoint
@app.post("/predict/batch", response_model=BatchSentimentResponse, dependencies=[Depends(verify_api_key)])
async def predict_batch(request: BatchSentimentRequest):
    if MODEL is None or TOKENIZER is None:
        if not load_model():
            raise HTTPException(status_code=503, detail="Model not loaded and could not be loaded")

    if len(request.texts) > MAX_BATCH_SIZE:
        raise HTTPException(status_code=400, detail=f"Batch size exceeds maximum of {MAX_BATCH_SIZE}")

    start_time = time.time()

    try:
        results = []

        # Process in batch
        inputs = TOKENIZER(request.texts, padding=True, truncation=True, return_tensors="pt", max_length=512)
        inputs = {k: v.to(DEVICE) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = MODEL(**inputs)

        # Process each result
        scores = torch.nn.functional.softmax(outputs.logits, dim=1)
        predicted_classes = torch.argmax(scores, dim=1).tolist()

        for i, (text, predicted_class) in enumerate(zip(request.texts, predicted_classes)):
            predicted_score = scores[i][predicted_class].item()
            sentiment = "Positive" if predicted_class == 1 else "Negative"

            # Increment prediction counter
            PREDICTIONS.labels(class=sentiment).inc()

            result = {
                "text": text,
                "sentiment": sentiment,
                "score": predicted_score,
                "processing_time": 0  # Will be updated with the batch time
            }

            # Add metadata if requested
            if request.include_metadata:
                result["metadata"] = {
                    "model": os.path.basename(os.environ.get("MODEL_PATH", "bloom-finetuned")),
                    "timestamp": datetime.now().isoformat(),
                    "device": str(DEVICE),
                    "batch_index": i,
                    "version": "1.0.0"
                }

            results.append(result)

        # Update processing time for all results
        processing_time = time.time() - start_time
        for result in results:
            result["processing_time"] = processing_time

        return {"results": results, "processing_time": processing_time}

    except Exception as e:
        logger.error(f"Batch prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch prediction failed: {str(e)}")

# Load model at startup
@app.on_event("startup")
async def startup_event():
    logger.info("Starting model server...")
    load_model()

# Main entry point
if __name__ == "__main__":
    port = int(os.environ.get("SERVING_PORT", 8000))
    uvicorn.run("serve:app", host="0.0.0.0", port=port, log_level="info")
