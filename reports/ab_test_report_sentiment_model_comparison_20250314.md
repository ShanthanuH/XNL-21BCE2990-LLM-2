# A/B Testing Report: sentiment_model_comparison

Generated on: 2025-03-14 16:58:51

## Experiment Details

- Model A (Baseline): bloom-finetuned-v1
- Model B (Variant): bloom-finetuned-v2
- Sample Size: 2000
- Test Duration: 23 minutes
- Completion Date: 2025-03-14 16:58:51

## Performance Metrics Comparison

| Metric | Model A | Model B | Difference | % Change |
|--------|---------|---------|------------|----------|
| Accuracy | 0.8781 | 0.8899 | +0.0118 | +1.34% |
| Precision | 0.8600 | 0.8906 | +0.0306 | +3.56% |
| Recall | 0.8682 | 0.8782 | +0.0100 | +1.15% |
| F1 | 0.8701 | 0.8782 | +0.0081 | +0.93% |
| Latency | 115.1372 | 128.5063 | +13.3691 | +11.61% |
| Throughput | 99.1195 | 81.8436 | -17.2759 | -17.43% |

![Performance Metrics](testing/ab_test_sentiment_model_comparison_performance.png)

![Efficiency Metrics](testing/ab_test_sentiment_model_comparison_efficiency.png)

## Statistical Significance

In a real implementation, we would perform statistical significance tests (e.g., t-tests) to determine if the observed differences are statistically significant. For this simulation, we assume:

- None of the performance differences are statistically significant (p > 0.05).

## Recommendation

**Recommendation: Further testing required**

While Model B shows better accuracy (+1.34%), the increased latency (+11.61%) may impact user experience. Consider:  

1. A/B testing with real users to measure impact on user experience  
2. Further optimization to reduce latency while maintaining accuracy gains  
