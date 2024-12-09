# src/models/roberta_model.py

import torch
from transformers import pipeline
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

classifier = pipeline(
    'sentiment-analysis',
    model='cardiffnlp/twitter-roberta-base-sentiment',
    tokenizer='cardiffnlp/twitter-roberta-base-sentiment',
    device=0 if device.type == 'cuda' else -1
)

LABEL_MAPPING = {
    "LABEL_0": "Negative",
    "LABEL_1": "Neutral",
    "LABEL_2": "Positive"
}

def analyze_sentiment_roberta(text):
    try:
        result = classifier(text)[0]
        label = LABEL_MAPPING.get(result['label'], "Unknown")

        model = classifier.model
        tokenizer = classifier.tokenizer

        inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
        inputs = {k: v.to(model.device) for k, v in inputs.items()}
        with torch.no_grad():
            outputs = model(**inputs)
        probs = torch.nn.functional.softmax(outputs.logits, dim=-1).cpu().numpy()[0]

        negative_prob = float(probs[0])
        neutral_prob = float(probs[1])
        positive_prob = float(probs[2])

        return {
            'roberta_sentiment_label': label,
            'roberta_negative_prob': negative_prob,
            'roberta_neutral_prob': neutral_prob,
            'roberta_positive_prob': positive_prob
        }
    except (ValueError, RuntimeError) as e:
        logger.error(f"Error processing text with RoBERTa: {e}")
        return {
            'roberta_sentiment_label': 'Error',
            'roberta_negative_prob': None,
            'roberta_neutral_prob': None,
            'roberta_positive_prob': None
        }