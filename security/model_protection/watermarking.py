
import os
import time
import torch
import random
import numpy as np
from transformers import AutoModelForSequenceClassification

class ModelWatermarker:
    """Implementation of model watermarking for LLM protection"""

    def __init__(self, model, watermark_key=None):
        self.model = model
        self.watermark_key = watermark_key or os.urandom(16).hex()
        self.watermarked = False

    def apply_watermark(self, seed=None):
        """Apply a watermark to the model by subtly modifying specific weights"""
        if self.watermarked:
            return False

        # Set seed for reproducibility, but use the watermark key to make it unique
        if seed is None:
            # Convert watermark_key to an integer seed
            seed = int(self.watermark_key[:8], 16)

        # Set the seeds
        torch.manual_seed(seed)
        random.seed(seed)
        np.random.seed(seed)

        # Get model parameters that will be watermarked
        # For this example, we'll watermark the last classification layer
        if hasattr(self.model, 'score'):
            target_layer = self.model.score
            print(f"Watermarking classification layer with shape {target_layer.weight.shape}")

            # Backup original weights
            original_weights = target_layer.weight.clone().detach()

            # Add a very small watermark pattern
            # The pattern is deterministic based on the seed but hard to detect
            watermark_pattern = torch.randn_like(target_layer.weight) * 1e-5

            # Apply the watermark
            with torch.no_grad():
                target_layer.weight.add_(watermark_pattern)

            self.watermarked = True

            # Calculate the difference
            diff = torch.norm(target_layer.weight - original_weights).item()
            print(f"Watermark applied. L2 difference: {diff}")

            return True
        else:
            print("Could not find appropriate layer to watermark")
            return False

    def verify_watermark(self, suspected_model, threshold=1e-6):
        """Verify if the suspected model contains our watermark"""
        if not self.watermarked:
            print("Original model not watermarked")
            return False

        # Set seed for reproducibility, using the same watermark key
        seed = int(self.watermark_key[:8], 16)
        torch.manual_seed(seed)
        random.seed(seed)
        np.random.seed(seed)

        # Generate the expected watermark pattern
        if hasattr(self.model, 'score') and hasattr(suspected_model, 'score'):
            target_layer = self.model.score
            suspected_layer = suspected_model.score

            # Create the watermark pattern
            watermark_pattern = torch.randn_like(target_layer.weight) * 1e-5

            # Get watermarked weights
            watermarked_weights = target_layer.weight.clone().detach()
            suspected_weights = suspected_layer.weight.clone().detach()

            # Remove the watermark to get the original weights
            original_weights = watermarked_weights - watermark_pattern

            # Calculate correlation between suspected model and both watermarked and original
            corr_with_watermarked = torch.nn.functional.cosine_similarity(
                watermarked_weights.flatten(), suspected_weights.flatten(), dim=0
            ).item()

            corr_with_original = torch.nn.functional.cosine_similarity(
                original_weights.flatten(), suspected_weights.flatten(), dim=0
            ).item()

            # Check if suspected is closer to watermarked than to original
            watermark_detected = (corr_with_watermarked - corr_with_original) > threshold

            print(f"Correlation with watermarked: {corr_with_watermarked}")
            print(f"Correlation with original: {corr_with_original}")
            print(f"Watermark detected: {watermark_detected}")

            return watermark_detected
        else:
            print("Could not find appropriate layer to verify watermark")
            return False

def watermark_model(model_path, output_path=None, watermark_key=None):
    """Utility function to watermark a saved model"""
    # Load the model
    model = AutoModelForSequenceClassification.from_pretrained(model_path)

    # Create watermarker
    watermarker = ModelWatermarker(model, watermark_key)

    # Apply watermark
    success = watermarker.apply_watermark()

    if success and output_path:
        # Save the watermarked model
        model.save_pretrained(output_path)
        print(f"Watermarked model saved to {output_path}")

        # Save watermark key for verification
        watermark_info = {
            "original_model": model_path,
            "watermarked_model": output_path,
            "watermark_key": watermarker.watermark_key,
            "timestamp": time.time()
        }

        watermark_dir = os.path.dirname(output_path)
        with open(os.path.join(watermark_dir, "watermark_info.json"), "w") as f:
            import json
            json.dump(watermark_info, f)

    return watermarker.watermark_key if success else None
