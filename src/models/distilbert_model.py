# src/models/distilbert_model.py

import torch
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
import logging
from tqdm.auto import tqdm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if torch.backends.mps.is_available():
    device = torch.device("mps")
    logger.info("Using MPS device for GPU acceleration.")
elif torch.cuda.is_available():
    device = torch.device("cuda")
    logger.info("Using CUDA device for GPU acceleration.")
else:
    device = torch.device("cpu")
    logger.info("No GPU device found. Using CPU.")

tokenizer = DistilBertTokenizer.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")
model = DistilBertForSequenceClassification.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")
model.to(device)
model.eval()

def analyze_sentiment_distilbert(text):
    try:
        inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
        inputs = {key: value.to(device) for key, value in inputs.items()}

        with torch.no_grad():
            outputs = model(**inputs)
        
        probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)
        probs = probabilities.cpu().numpy()[0]
        negative_prob = float(probs[0])
        positive_prob = float(probs[1])
        sentiment_label = "Positive" if positive_prob > negative_prob else "Negative"
        return {
            'distilbert_sentiment_label': sentiment_label,
            'distilbert_negative_prob': negative_prob,
            'distilbert_positive_prob': positive_prob
        }
    except Exception as e:
        logger.error(f"Error in DistilBERT model for text: {text}\nError: {e}")
        return {
            'distilbert_sentiment_label': 'Error',
            'distilbert_negative_prob': None,
            'distilbert_positive_prob': None
        }