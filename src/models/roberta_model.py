# src/models/roberta_model.py

import torch
from transformers import pipeline
import logging
from tqdm.auto import tqdm

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check and set the device to MPS (Metal Performance Shaders) if available
if torch.backends.mps.is_available():
    device = torch.device("mps")
    logger.info("Using MPS (Metal Performance Shaders) device for GPU acceleration.")
elif torch.cuda.is_available():
    device = torch.device("cuda")
    logger.info("Using CUDA device for GPU acceleration.")
else:
    device = torch.device("cpu")
    logger.info("No GPU device found. Using CPU.")

# Initialize the RoBERTa pipeline for sentiment analysis
classifier = pipeline(
    'sentiment-analysis',
    model='cardiffnlp/twitter-roberta-base-sentiment',
    tokenizer='cardiffnlp/twitter-roberta-base-sentiment',
    device=0 if device.type == 'cuda' else -1  # Set device index for Hugging Face
)

# Mapping from model labels to desired sentiment labels
LABEL_MAPPING = {
    "LABEL_0": "Negative",
    "LABEL_1": "Neutral",
    "LABEL_2": "Positive"
}

def analyze_sentiment_roberta(text):
    """
    Analyze the sentiment of the given text using the RoBERTa model.

    Args:
        text (str): The text to analyze.

    Returns:
        str: The sentiment label ('Positive', 'Neutral', 'Negative') or 'Error' if analysis fails.
    """
    try:
        result = classifier(text)[0]
        label = LABEL_MAPPING.get(result['label'], "Unknown")
        return label
    except (ValueError, RuntimeError) as e:
        logger.error(f"Error processing text with RoBERTa: {e}")
        return 'Error'

def analyze_roberta_batch(texts, batch_size=32):
    """
    Analyze sentiments for a batch of texts using the RoBERTa model.

    Args:
        texts (list of str): The texts to analyze.
        batch_size (int): Number of texts to process in each batch.

    Returns:
        list of str: A list of sentiment labels ('Positive', 'Neutral', 'Negative') or 'Error' if analysis fails.
    """
    sentiments = []
    total_batches = (len(texts) + batch_size - 1) // batch_size  # Ceiling division

    for i in tqdm(range(0, len(texts), batch_size), desc="Analyzing RoBERTa in Batches"):
        batch = texts[i:i + batch_size]
        try:
            results = classifier(batch)
            for result in results:
                label = LABEL_MAPPING.get(result['label'], "Unknown")
                sentiments.append(label)
        except Exception as e:
            logger.error(f"RoBERTa error for batch {i}-{i + batch_size}: {e}")
            sentiments.extend(['Error'] * len(batch))
    return sentiments