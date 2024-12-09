# src/models/roberta_model.py

import torch
from transformers import pipeline
import logging
from tqdm.auto import tqdm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Determine the appropriate device
if torch.cuda.is_available():
    device = torch.device("cuda")
    logger.info("Using CUDA device for GPU acceleration.")
elif torch.backends.mps.is_available():
    device = torch.device("mps")
    logger.info("Using MPS device for GPU acceleration.")
else:
    device = torch.device("cpu")
    logger.info("No GPU device found. Using CPU.")

# Initialize the sentiment analysis pipeline
classifier = pipeline(
    'sentiment-analysis',
    model='cardiffnlp/twitter-roberta-base-sentiment',
    tokenizer='cardiffnlp/twitter-roberta-base-sentiment',
    device=0 if device.type == 'cuda' else -1  # Note: 'mps' is not directly supported
)

LABEL_MAPPING = {
    "LABEL_0": "Negative",
    "LABEL_1": "Neutral",
    "LABEL_2": "Positive"
}

def analyze_sentiment_roberta(text):
    """
    Analyzes the sentiment of the given text using the RoBERTa model.

    Args:
        text (str): The input text to analyze.

    Returns:
        dict: A dictionary containing the sentiment label and probabilities.
    """
    try:
        # Perform sentiment analysis using the pipeline
        result = classifier(text)[0]
        label = LABEL_MAPPING.get(result['label'], "Unknown")

        # Extract the model and tokenizer from the pipeline
        model = classifier.model
        tokenizer = classifier.tokenizer

        # Tokenize the input text for manual model inference
        inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
        inputs = {k: v.to(model.device) for k, v in inputs.items()}

        # Perform manual inference to get logits
        with torch.no_grad():
            outputs = model(**inputs)
        probs = torch.nn.functional.softmax(outputs.logits, dim=-1).cpu().numpy()[0]

        # Extract probabilities
        negative_prob = float(probs[0])
        neutral_prob = float(probs[1])
        positive_prob = float(probs[2])

        return {
            'roberta_sentiment_label': label,
            'roberta_negative_prob': negative_prob,
            'roberta_neutral_prob': neutral_prob,
            'roberta_positive_prob': positive_prob
        }
    except Exception as e:
        # Catch all exceptions to ensure graceful degradation
        logger.error(f"Error processing text with RoBERTa: {e}")
        return {
            'roberta_sentiment_label': 'Error',
            'roberta_negative_prob': None,
            'roberta_neutral_prob': None,
            'roberta_positive_prob': None
        }