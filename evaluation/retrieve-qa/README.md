# Evaluation on Retrieve Augmented Question Answering

Here we evaluation the E2E question answering performance on [NaturalQuestion](https://ai.google.com/research/NaturalQuestions) dataset.
We collected 5332 nonredundant context documents and 6775 queries from [HuggingFace Dataset](https://huggingface.co/datasets/thinkall/NaturalQuestionsQA).

First, we created a document collection based on all the context corpus and stored them in a vector database; then we selected the some questions and answered them with RetrieveChat.
Next, to evaluate the performance of RetrieveChat in QA, we employ the metrics of exact match (EM), F1 score and Recall.
The EM score indicates the percentage of questions where the predicted answer matches the reference answer to the question exactly.
On the other hand, the F1 score measures the similarity between the predicted answer and the reference answer, taking into account both precision and recall.
However, our results imply that recall, which measures the proportion of tokens in the reference answer that are present in the predicted answer, is more highly correlated with correctness than lexical overlap metrics such as EM or F1. Which is also mentioned in [this paper](https://arxiv.org/pdf/2307.16877v1.pdf).

Results on the first 200 questions are as below:
```
Average EM: 0.005
Average F1: 0.22873285469719287
Average Recall: 0.7319256264504997
```
The F1 score and Recall score are significantly higher than the results showed in [this paper](https://arxiv.org/pdf/2307.16877v1.pdf).
