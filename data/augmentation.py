"""
Data augmentation techniques for enhancing the IMDB dataset
"""

# Install required packages
import sys
!pip install -q nlpaug datasets

import nlpaug.augmenter.word as naw
import pandas as pd
import random
from datasets import load_dataset, Dataset
import nltk
nltk.download('wordnet', quiet=True)

def get_augmented_dataset(sample_size=5000, save=True):
    """Generate augmented dataset for training"""
    
    print("Loading IMDB dataset...")
    dataset = load_dataset("imdb")
    
    # Initialize augmenters
    print("Setting up augmentation techniques...")
    synonym_aug = naw.SynonymAug(aug_src='wordnet')
    random_aug = naw.RandomWordAug()
    
    # Define augmentation function
    def augment_text(text):
        augmentation_type = random.choice(["synonym", "random", "none"])
        
        if augmentation_type == "synonym":
            try:
                return synonym_aug.augment(text)
            except:
                return text
        elif augmentation_type == "random":
            try:
                return random_aug.augment(text)
            except:
                return text
        else:
            return text  # No augmentation
    
    # Take a subset for augmentation
    print(f"Selecting {sample_size} examples for augmentation...")
    train_subset = dataset["train"].select(range(sample_size))
    
    # Apply augmentation
    print("Applying augmentation techniques...")
    augmented_texts = []
    augmented_labels = []
    
    for i, example in enumerate(train_subset):
        if i % 500 == 0:
            print(f"  Processed {i}/{sample_size} examples...")
        
        augmented_text = augment_text(example["text"])
        augmented_texts.append(augmented_text)
        augmented_labels.append(example["label"])
    
    # Create augmented dataset
    augmented_data = {
        "text": augmented_texts,
        "label": augmented_labels
    }
    
    augmented_dataset = Dataset.from_dict(augmented_data)
    
    if save:
        augmented_dataset.save_to_disk("data/augmented_imdb")
        print("Augmented dataset saved to data/augmented_imdb")
    
    print("Augmentation complete!")
    return augmented_dataset

if __name__ == "__main__":
    get_augmented_dataset()
