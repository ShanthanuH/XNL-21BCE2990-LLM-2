# Model Drift Monitoring Report: bloom-finetuned-sentiment

Generated on: 2025-03-14 16:58:51

## Reference Distribution (Baseline)

- Timestamp: 2025-03-14 16:58:51
- Label Distribution: {0: 0.5, 1: 0.5}
- Average Text Length: 58.78 characters

## Latest Monitoring Results

- Timestamp: 2025-03-14 16:58:51
- Drift Detected: Yes
- Label Distribution PSI: 0.0405 (threshold: 0.2)
- Text Length Change: 30.43%
- Current Accuracy: 0.8000

## Drift Visualization

![Drift Visualization](monitoring/model_drift_visualization.png)

## Drift Monitoring History

| Timestamp | Drift Detected | PSI | Text Length Change | Accuracy |
|-----------|----------------|-----|-------------------|----------|
| 2025-03-14 16:58:51 | No | 0.1110 | 2.27% | 0.8400 |
| 2025-03-14 16:58:51 | Yes | 0.0061 | 30.43% | 0.8400 |
| 2025-03-14 16:58:51 | Yes | 0.0061 | 30.43% | 0.8400 |
| 2025-03-14 16:58:51 | Yes | 0.0271 | 30.43% | 0.8200 |
| 2025-03-14 16:58:51 | Yes | 0.0271 | 30.43% | 0.8200 |
| 2025-03-14 16:58:51 | Yes | 0.0405 | 30.43% | 0.8000 |
| 2025-03-14 16:58:51 | Yes | 0.0405 | 30.43% | 0.8000 |

## Recommendations

**Action Required**: Model drift detected. Recommended actions:

3. **Monitoring Frequency**: Increase monitoring frequency to daily until drift stabilizes.
