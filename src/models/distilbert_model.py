# src/models/distilbert_model.py

import torch
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
import logging
from tqdm.auto import tqdm

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check and set the device (MPS for Mac, CUDA for Nvidia GPUs, CPU otherwise)
if torch.backends.mps.is_available():
    device = torch.device("mps")
    logger.info("Using MPS (Metal Performance Shaders) device for GPU acceleration.")
elif torch.cuda.is_available():
    device = torch.device("cuda")
    logger.info("Using CUDA device for GPU acceleration.")
else:
    device = torch.device("cpu")
    logger.info("No GPU device found. Using CPU.")

# Initialize the DistilBERT tokenizer and model
tokenizer = DistilBertTokenizer.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")
model = DistilBertForSequenceClassification.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")
model.to(device)
model.eval()

def analyze_sentiment_distilbert(text):
    """
    Analyze sentiment of a single text using DistilBERT.

    Args:
        text (str): Text content to analyze.

    Returns:
        str: Sentiment label ('POSITIVE', 'NEGATIVE', or 'Error').
    """
    try:
        inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
        inputs = {key: value.to(device) for key, value in inputs.items()}

        with torch.no_grad():
            outputs = model(**inputs)
        
        probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)
        probs = probabilities.cpu().numpy()[0]
        sentiment_label = "POSITIVE" if probs[1] > probs[0] else "NEGATIVE"
        return sentiment_label
    except Exception as e:
        logger.error(f"Error in DistilBERT model for text: {text}\nError: {e}")
        return 'Error'

def analyze_distilbert_batch(texts, batch_size=32):
    """
    Analyze sentiment of a list of texts using DistilBERT in batches.

    Args:
        texts (list of str): List of text contents to analyze.
        batch_size (int): Number of texts to process in each batch.

    Returns:
        list of dict: List containing sentiment analysis results.
    """
    sentiments = []
    for i in tqdm(range(0, len(texts), batch_size), desc="Analyzing DistilBERT in Batches"):
        batch = texts[i:i+batch_size]
        try:
            inputs = tokenizer(batch, return_tensors="pt", truncation=True, padding=True, max_length=512)
            inputs = {key: value.to(device) for key, value in inputs.items()}

            with torch.no_grad():
                outputs = model(**inputs)
            
            probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)
            probs = probabilities.cpu().numpy()

            for prob in probs:
                positive_prob = prob[1]
                negative_prob = prob[0]
                sentiment_label = "POSITIVE" if positive_prob > negative_prob else "NEGATIVE"
                sentiments.append({
                    'distilbert_negative_prob': negative_prob,
                    'distilbert_positive_prob': positive_prob,
                    'distilbert_sentiment_label': sentiment_label
                })
        except Exception as e:
            logger.error(f"DistilBERT error for batch {i}-{i+batch_size}: {e}")
            for _ in batch:
                sentiments.append({
                    'distilbert_negative_prob': None,
                    'distilbert_positive_prob': None,
                    'distilbert_sentiment_label': None
                })
    return sentiments