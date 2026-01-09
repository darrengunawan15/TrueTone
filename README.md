# TrueTone

TrueTone is a real-time emotion recognition application that analyzes text and classifies emotional tone using advanced. The system combines a React-based frontend with a FastAPI backend powered by a fine-tuned transformer model for accurate and efficient emotion detection.

## Overview

TrueTone enables users to input text and receive instant classification across seven different emotional categories. The application provides not only the primary emotion prediction but also confidence scores and probability distributions across all emotion types, offering comprehensive insight into the model's classification reasoning.

## Supported Emotions

- **Anger** - Expressions of frustration or rage
- **Fear** - Expressions of anxiety or dread
- **Joy** - Expressions of happiness or elation
- **Love** - Expressions of affection or tenderness
- **Sadness** - Expressions of sorrow or melancholy
- **Surprise** - Expressions of astonishment
- **Neutral** - Emotionally neutral text

## Key Features

- **Real-time Emotion Detection**: Instantly classify text into emotional categories
- **Confidence Scoring**: View the model's confidence level for each prediction
- **Probability Distribution**: Examine how the model scores all emotions
- **Responsive User Interface**: Intuitive, modern interface built with React and Vite
- **Containerized Architecture**: Fully containerized for consistent deployment across environments
- **Scalable Design**: Cloud-native architecture supporting Kubernetes orchestration and Azure deployment

## System Architecture

TrueTone follows a microservices architecture pattern with clear separation of concerns between frontend and backend components:

```
┌─────────────────────────────────────────────────────────┐
│                 React Frontend                           │
│          (Vite + React + Component State)               │
│                                                          │
│  - User Interface for text input                        │
│  - Real-time result display                            │
│  - Emotion visualization with confidence scores        │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP/REST API
                         │ JSON Request/Response
                         ▼
┌─────────────────────────────────────────────────────────┐
│              FastAPI Backend                             │
│          (ASGI Web Framework)                            │
│                                                          │
│  - REST API endpoints (/predict, /health)              │
│  - CORS middleware for cross-origin requests           │
│  - Request validation using Pydantic models            │
│  - Response transformation and formatting              │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│        Machine Learning Model Layer                      │
│                                                          │
│  - Pre-trained transformer model                       │
│  - Emotion classification head                         │
│  - Softmax probability distribution                    │
└─────────────────────────────────────────────────────────┘
```

### Component Responsibilities

**Frontend (React + Vite):**
- Handles user interaction and input validation
- Makes asynchronous API calls to the backend
- Transforms API responses into visual components
- Displays emotion predictions with confidence metrics
- Provides error handling and user feedback

**Backend (FastAPI):**
- Exposes REST API endpoints for emotion prediction
- Manages model loading and inference
- Validates incoming requests using Pydantic schemas
- Returns structured JSON responses with detailed classification results
- Implements CORS to allow cross-origin requests from frontend

**Model (DistilRoBERTa):**
- Tokenizes input text into subword tokens
- Processes tokens through transformer layers
- Generates contextual embeddings
- Classifies text into one of seven emotional categories
- Produces probability scores for all emotions

## Project Structure

```
TrueTone/
├── app/                           # Backend Application
│   ├── main.py                   # FastAPI application entry point
│   ├── model.py                  # Emotion prediction logic & inference
│   ├── audio_main.py             # Audio processing module (future feature)
│   ├── emotion_roberta.pt        # Pre-trained model weights
│   ├── __init__.py               # Package initialization
│   └── tokenizer/                # Model tokenizer components
│       ├── vocab.json            # BPE vocabulary
│       ├── merges.txt            # BPE merge operations
│       ├── tokenizer_config.json # Tokenizer configuration
│       └── special_tokens_map.json
│
├── frontend/                      # Frontend Application
│   ├── App.jsx                   # Main React component & logic
│   ├── main.jsx                  # Application entry point
│   ├── App.css                   # Component styling
│   ├── index.html                # HTML template
│   ├── index.css                 # Global styles
│   ├── vite.config.js            # Vite bundler configuration
│   ├── nginx.conf                # Nginx reverse proxy config
│   ├── Dockerfile                # Frontend container specification
│   └── package.json              # JavaScript dependencies
│
├── kubernetes/                    # Kubernetes Manifests
│   ├── namespace.yml             # K8s namespace definition
│   ├── backend-deployment.yml    # Backend service & deployment config
│   └── frontend-deployment.yml   # Frontend service & deployment config
│
├── Dockerfile                     # Backend container specification
├── docker-compose.yml            # Local multi-container setup
├── requirements.txt              # Python package dependencies
├── DEPLOYMENT.md                 # Detailed deployment instructions
├── README.md                      # This file
└── .gitignore                     # Git ignore rules
```

### Directory Descriptions

**app/** - Backend API and ML model
- Implements FastAPI REST service for emotion prediction
- Contains pre-trained DistilRoBERTa model and tokenizer
- Handles inference, request validation, and response formatting

**frontend/** - React user interface
- Built with Vite for fast development and optimized builds
- Provides text input interface and emotion visualization
- Communicates with backend via REST API

**kubernetes/** - Cloud orchestration configuration
- Defines Kubernetes deployments for backend and frontend
- Specifies resource limits, health checks, and service routing
- Includes namespace isolation for organized resource management

## API Specification

### POST /predict

Predicts the emotion classification for input text.

**Request Schema:**
```json
{
  "text": "string (required) - The text to analyze"
}
```

**Response Schema:**
```json
{
  "emotion": "string - The predicted emotion category",
  "confidence": "float - Confidence score (0.0 to 1.0)",
  "probabilities": {
    "anger": 0.0,
    "fear": 0.0,
    "joy": 0.0,
    "love": 0.0,
    "sadness": 0.0,
    "surprise": 0.0
  }
}
```

**Example Request:**
```json
{
  "text": "I feel absolutely amazing today!"
}
```

**Example Response:**
```json
{
  "emotion": "joy",
  "confidence": 0.94,
  "probabilities": {
    "anger": 0.01,
    "fear": 0.01,
    "joy": 0.94,
    "love": 0.02,
    "sadness": 0.01,
    "surprise": 0.01
  }
}
```

### GET /

Health check endpoint to verify API is operational.

## Technology Stack

**Backend:**
- **Framework:** FastAPI - Modern, high-performance Python web framework
- **Server:** Uvicorn - ASGI web server implementation
- **ML Framework:** PyTorch - Deep learning framework for model inference
- **Validation:** Pydantic - Data validation using Python type hints
- **Middleware:** CORS (Cross-Origin Resource Sharing) for frontend integration

**Frontend:**
- **Framework:** React - Component-based UI library
- **Build Tool:** Vite - Next-generation frontend build tool
- **Styling:** CSS - Custom component styling
- **Server:** Nginx - Reverse proxy and static file serving

**Containerization & Deployment:**
- **Containers:** Docker for packaging and running services
- **Orchestration:** Docker Compose for local multi-container setup
- **Cloud:** Kubernetes for scalable cloud deployment
- **Registry:** Azure Container Registry (ACR) for image storage
- **Cloud Platform:** Microsoft Azure Kubernetes Service (AKS)

## Deployment Information

For comprehensive deployment instructions covering local testing, Azure setup, container registry configuration, and Kubernetes deployment, refer to [DEPLOYMENT.md](DEPLOYMENT.md).

## Contact

For questions or issues, please refer to the project documentation or contact the development team.
