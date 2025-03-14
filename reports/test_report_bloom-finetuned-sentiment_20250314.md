# Model Testing Report: bloom-finetuned-sentiment

Generated on: 2025-03-14 16:58:51

## Standard Test Results

- Accuracy: 0.6600
- Precision: 0.6151
- Recall: 0.6600
- F1 Score: 0.5983
- Test Set Size: 2000

![Confusion Matrix](testing/confusion_matrix_bloom-finetuned-sentiment.png)

## Cross-Validation Results

- Average Accuracy: 0.5260 (±0.0202)
- Average F1 Score: 0.4608 (±0.0246)
- K-Folds: 5

![Cross-Validation Results](testing/cross_validation_bloom-finetuned-sentiment.png)

### Individual Fold Results

| Fold | Accuracy | Precision | Recall | F1 Score |
|------|----------|-----------|--------|----------|
| 1 | 0.5280 | 0.5804 | 0.5280 | 0.4735 |
| 2 | 0.5350 | 0.5424 | 0.5350 | 0.4684 |
| 3 | 0.4920 | 0.5057 | 0.4920 | 0.4207 |
| 4 | 0.5210 | 0.5412 | 0.5210 | 0.4482 |
| 5 | 0.5540 | 0.5767 | 0.5540 | 0.4930 |

## Edge Case Performance

| Category | Accuracy | Precision | Recall | F1 Score | Examples |
|----------|----------|-----------|--------|----------|----------|
| negation | 0.5000 | 1.0000 | 0.5000 | 0.6667 | 4 |
| sarcasm | 0.2500 | 1.0000 | 0.2500 | 0.4000 | 4 |
| ambiguous | 0.8000 | 1.0000 | 0.8000 | 0.8889 | 5 |

![Edge Case Performance](testing/edge_case_performance.png)

## Recommendations

1. **Improve sarcasm handling**: Model performance is weakest on sarcasm cases. Consider augmenting training data with more sarcasm examples.
2. **Focus on precision improvement**: The model has higher recall than precision, indicating it may be generating false positives. Tune the classification threshold or adjust class weights during training.
