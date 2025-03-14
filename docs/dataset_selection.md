# Dataset Selection for Sentiment Analysis

We've selected the **IMDB Movie Reviews** dataset for our sentiment analysis fine-tuning task.

## Dataset Overview
- **Source**: IMDB Movie Reviews (via Hugging Face Datasets)
- **Size**: 50,000 labeled movie reviews (25,000 train, 25,000 test)
- **Classes**: Binary classification (positive/negative sentiment)
- **Average Length**: ~230 words per review

## Selection Rationale
1. **Business Relevance**: Sentiment analysis has clear commercial applications
2. **Quality & Size**: Large corpus of human-written text with high-quality labels
3. **Balanced Classes**: Equal distribution of positive and negative reviews
4. **Evaluation Clarity**: Binary classification with straightforward metrics

## Implementation Details
The dataset will be loaded using the Hugging Face Datasets library:

from datasets import load_dataset
dataset = load_dataset("imdb")

We'll implement a 90/10 train/validation split of the training data for hyperparameter tuning.
