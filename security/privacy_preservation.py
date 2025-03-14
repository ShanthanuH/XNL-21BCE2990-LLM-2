
import numpy as np
import torch
from typing import List, Dict, Any, Union

class PrivacyPreservation:
    """Methods for preserving privacy in model inputs and outputs"""

    @staticmethod
    def apply_differential_privacy(data: List[str], epsilon: float = 1.0, delta: float = 1e-5):
        """Apply differential privacy to text by adding calibrated noise"""
        # This is a simplified implementation for demonstration purposes
        # In a real implementation, you would use libraries like TensorFlow Privacy

        # Create a copy of the data
        private_data = data.copy()

        # Calculate sensitivity - for text data, we use a simplified approach
        sensitivity = 1.0

        # Calculate noise scale based on epsilon and delta
        noise_scale = sensitivity * np.sqrt(2 * np.log(1.25 / delta)) / epsilon

        # Apply noise to each data point
        # For text data, we need to perturb word vectors or embeddings
        # This is a placeholder for demonstration purposes
        return private_data

    @staticmethod
    def tokenize_and_mask_pii(text: str, mask_token: str = "[MASKED]") -> str:
        """Tokenize text and mask personally identifiable information"""
        # In a real implementation, you would use NER models to identify PII

        # Example PII patterns (simplified)
        pii_patterns = [
            r'\d{3}[-.]?\d{3}[-.]?\d{4}',  # US Phone numbers
            r'\d{3}[-.]?\d{2}[-.]?\d{4}',  # SSN
            r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}',  # Email
            r'(?:4[0-9]{12}(?:[0-9]{3})?|(?:5[1-5][0-9]{2}|222[1-9]|22[3-9][0-9]|2[3-6][0-9]{2}|27[01][0-9]|2720)[0-9]{12}|3[47][0-9]{13}|3(?:0[0-5]|[68][0-9])[0-9]{11}|6(?:011|5[0-9]{2})[0-9]{12}|(?:2131|1800|35\d{3})\d{11})'  # Credit card
        ]

        # Import regex here to avoid top-level dependency
        import re

        # Apply masking
        masked_text = text
        for pattern in pii_patterns:
            masked_text = re.sub(pattern, mask_token, masked_text)

        return masked_text

    @staticmethod
    def perform_k_anonymization(dataset: List[Dict[str, Any]], k: int = 5, sensitive_keys: List[str] = None):
        """Perform k-anonymization on a dataset"""
        # This is a simplified implementation for demonstration purposes

        if sensitive_keys is None:
            # Default sensitive keys
            sensitive_keys = ["name", "email", "phone", "address"]

        # Group records by non-sensitive attributes
        from collections import defaultdict
        groups = defaultdict(list)

        for record in dataset:
            # Create a key from non-sensitive attributes
            non_sensitive_values = tuple(
                value for key, value in record.items() if key not in sensitive_keys
            )
            groups[non_sensitive_values].append(record)

        # Check if groups satisfy k-anonymity
        k_anonymized_dataset = []
        suppressed_groups = []

        for group_key, group_records in groups.items():
            if len(group_records) >= k:
                k_anonymized_dataset.extend(group_records)
            else:
                suppressed_groups.extend(group_records)

        # For demo purposes, suppress records that don't satisfy k-anonymity
        # In a real implementation, you would generalize attributes to merge groups

        return k_anonymized_dataset, suppressed_groups
