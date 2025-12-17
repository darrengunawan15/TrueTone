# audio_api.py
import torch
import torch.nn as nn
import numpy as np
import librosa
import tempfile
import os

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse

# -------------------------
# Config
# -------------------------
SAMPLE_RATE = 16000
N_MELS = 64
MAX_LEN = 300        # time frames
CONF_THRESHOLD = 0.50

# -------------------------
# Labels (AUDIO ONLY)
# -------------------------
AUDIO_ID2LABEL = {
    0: "anger",
    1: "disgust",
    2: "fear",
    3: "happy",
    4: "neutral",
    5: "sad"
}

NUM_CLASSES = len(AUDIO_ID2LABEL)

# -------------------------
# Feature Extraction
# -------------------------
def extract_log_mel(path: str) -> np.ndarray:
    y, sr = librosa.load(path, sr=SAMPLE_RATE)

    mel = librosa.feature.melspectrogram(
        y=y,
        sr=sr,
        n_mels=N_MELS,
        n_fft=1024,
        hop_length=512
    )

    log_mel = librosa.power_to_db(mel)

    # Pad / truncate
    if log_mel.shape[1] < MAX_LEN:
        pad_width = MAX_LEN - log_mel.shape[1]
        log_mel = np.pad(log_mel, ((0, 0), (0, pad_width)))
    else:
        log_mel = log_mel[:, :MAX_LEN]

    return log_mel.astype(np.float32)

# -------------------------
# Model Definition
# -------------------------
class AudioEmotionCNN(nn.Module):
    def __init__(self, num_classes=6):
        super().__init__()

        self.conv = nn.Sequential(
            nn.Conv2d(1, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),

            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2)
        )

        self.fc = nn.Sequential(
            nn.Linear(64 * (N_MELS // 4) * (MAX_LEN // 4), 128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, num_classes)
        )

    def forward(self, x):
        x = self.conv(x)
        x = x.view(x.size(0), -1)
        return self.fc(x)

# -------------------------
# App Init
# -------------------------
app = FastAPI(title="Audio Emotion Recognition API")

device = torch.device("cpu")

model = AudioEmotionCNN(num_classes=NUM_CLASSES)
model.load_state_dict(torch.load("audio_emotion.pt", map_location=device))
model.to(device)
model.eval()

# -------------------------
# Health Check
# -------------------------
@app.get("/")
def health():
    return {"status": "ok", "model": "audio_emotion_cnn", "device": "cpu"}

# -------------------------
# Prediction Endpoint
# -------------------------
@app.post("/predict-audio")
async def predict_audio(file: UploadFile = File(...)):
    if not file.filename.lower().endswith((".wav", ".mp3", ".ogg")):
        return JSONResponse(
            status_code=400,
            content={"error": "Unsupported audio format"}
        )

    # Save temp audio file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        mel = extract_log_mel(tmp_path)
        x = torch.tensor(mel).unsqueeze(0).unsqueeze(0).to(device)

        with torch.inference_mode():
            logits = model(x)
            probs = torch.softmax(logits, dim=-1)

        confidence, idx = probs.max(dim=-1)
        confidence = confidence.item()
        idx = idx.item()

        if confidence < CONF_THRESHOLD:
            emotion = "neutral"
        else:
            emotion = AUDIO_ID2LABEL[idx]

        return {
            "emotion": emotion,
            "confidence": round(confidence, 4)
        }

    finally:
        os.remove(tmp_path)