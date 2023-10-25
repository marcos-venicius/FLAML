# Adversarial Example Generation Experiment Log

## Generator + Evaluator Loop
Here we explore our baseline approach, where a LLM-based generator is asked to create hard examples for a task. These examples are then assessed by the Evaluator module, which interacts with the target LLM system to obtain the response and evaluates it. For the table below, an adversarial example is any example where the output is deemed sub-optimal by the Evaluator.

| Dataset | Adversarial Rate | Inconclusive Rate | Adversarial Rate over Training Set
| - | - | - | - |
| Math | 58.4% | 0.4% | 47.3%
| Review Summarization | 0.0% | 0.0% | 0.0%
| Story Composition | 99.8% | 0.2% | 98.8%
| Text Simplification | 2.4% | 0.0% | 5.2%
| Explanation | 2.4% | 0.0% | 2.0%
| Title Generation | 0.0% | 0.0% | 0.0%
| Paraphrasing | 9.8% | 0.2% | 12.0%
| Boolean Expressions | 4.8% | 0.2% | 5.5%
| Movie Recommendations | 29.0% | 4.0% | 27.3%
| Ruin Names | 58.4% | 0.0% | 39.3%

## Adversarial Examples as ICE
Here we explore using adversarial examples as in-context learning examples. Two variants are assessed: one which draws ICE uniformly from the training set, and another that draws ICE uniformly from known adversarial examples on the training set. We also modify our definition of adversarial examples to include only examples where the Evaluator provides a score below 0.5 for any of the evaluation criteria used. The variant that uses adversarial examples as ICE was only applied to tasks where we obtained at least 5 adversarial examples.

Overall, we see a drop in adversarial generation for most generative tasks, which indicates that most adversarial examples for these tasks according to our previous definition were actually near-optimal examples. For those tasks, we were not able to leverage adversarial-only ICE since we did not have the minimum number of adversarial examples. For non-generative tasks, on the other hand, we observe a slight increase in the adversarial rate generation.

| Dataset | Adversarial Rate | Inconclusive Rate | Adversarial Rate (Adv ICE) | Inconclusive Rate (Adv ICE) | Adversarial Rate over Training Set
| - | - | - | - | - | - |
| Math | 58.2% | 1.6% | 63.0% | 0.8% | 47.4%
| Review Summarization | 0.2% | 0.0% | N/A | N/A | 0.0%
| Text Simplification | 1.0% | 0.0% | N/A | N/A | 1.2%
| Explanation | 1.0% | 0.0% | N/A | N/A | 1.2%
| Story Composition | 0.0% | 0.2% | N/A | N/A | 1.6%
| Title Generation | 0.0% | 0.0% | N/A | N/A | 0.0%
| Paraphrasing | 0.0% | 0.2% | N/A | N/A | 1.6%
| Boolean Expressions | 5.2% | 0.0% | 7.0% | 0.8% | 5.2%
| Movie Recommendations | 32.4% | 3.6% | 34.0% | 3.8% | 27.3%
| Ruin Names | 54.2% | 0.0% | 55.0% | 0.2% | 39.3%

## Similarity Embedding

### Adversarial Rate

| Method | Math | Boolean Exp. | Movie Rec. | Ruin Names |
| - | - | - | - | - |
| Similarity, 0.85 | 81.2% | 6.0% | 43.0% | 63.8%
| Similarity, 0.90 | 69.8% | 6.0% | 37.2% | 49.6%
| Similarity, 0.95 | 51.8% | 13.2% | 19.2% | 51.0%
| Adversarial, uniform | 63.0% | 7.0% | 34.0% | 55.0%
| All, uniform | 58.2% | 5.2% | 32.4% | 54.2%
| Training set | 47.4% | 5.2% | 27.3% | 39.3%s

### Inconclusive Rate

| Method | Math | Boolean Exp. | Movie Rec. | Ruin Names |
| - | - | - | - | - |
| Similarity, 0.85 | 0.6% | 0.0% | 1.8% | 1.0%
| Similarity, 0.90 | 1.0% | 0.0% | 5.4% | 0.8%
| Similarity, 0.95 | 6.6% | 0.0% | 9.8% | 0.8%
| Adversarial, uniform | 0.8% | 0.8% | 3.8% | 0.2%
| All, uniform | 1.6% | 0.0% | 3.6% | 0.0%