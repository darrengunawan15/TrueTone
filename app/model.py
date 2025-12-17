import torch
from transformers import RobertaTokenizer, RobertaForSequenceClassification
from pathlib import Path

# Paths relative to this file's directory
APP_DIR = Path(__file__).parent
MODEL_PATH = APP_DIR / "emotion_roberta.pt"
TOKENIZER_PATH = APP_DIR / "tokenizer"
LABEL_PATH = APP_DIR / "id2label.pt"

NUM_LABELS = 6

torch.set_num_threads(2)

tokenizer = RobertaTokenizer.from_pretrained(str(TOKENIZER_PATH))

model = RobertaForSequenceClassification.from_pretrained(
    "distilroberta-base",
    num_labels=NUM_LABELS
)

model.load_state_dict(torch.load(str(MODEL_PATH), map_location="cpu", weights_only=False))
model.eval()

id2label = torch.load(str(LABEL_PATH))


def predict_emotion(text: str):
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=128
    )

    with torch.inference_mode():
        logits = model(**inputs).logits
        probs = torch.softmax(logits, dim=-1)

    # Get all probabilities
    probs_dict = {}
    for idx, prob in enumerate(probs[0]):
        emotion = id2label[idx]
        probs_dict[emotion] = round(prob.item(), 4)

    # Get top emotion
    confidence, idx = probs.max(dim=-1)
    top_emotion = id2label[idx.item()]
    top_confidence = round(confidence.item(), 4)

    # Neutral fallback (important for apps)
    if top_confidence < 0.4:
        top_emotion = "neutral"

    return top_emotion, top_confidence, probs_dict