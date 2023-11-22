import json
import os
import string
import re
import random
import argparse
import nltk
from nltk.corpus import words, stopwords
from nltk.tokenize import word_tokenize

nltk.download("stopwords")
nltk.download("punkt")
nltk.download("words")

random.seed(42)


def generate_random_word():
    # Get the list of English words from the nltk corpus
    word_list = words.words()

    # Choose a random word from the list
    random_word = random.choice(word_list)

    return random_word


def random_variation(question):
    # Split the question into words
    words = question.split()

    # Randomly select a word to modify
    index_to_modify = random.randint(0, len(words) - 1)

    # Generate a random modification (you can customize this part)
    modification_options = ["add", "remove", "replace"]
    modification = random.choice(modification_options)

    if modification == "add":
        # Add a random word
        new_word = generate_random_word()
        words.insert(index_to_modify, new_word)
    elif modification == "remove":
        # Remove the selected word
        del words[index_to_modify]
    elif modification == "replace":
        # Replace the selected word with a random word
        new_word = generate_random_word()
        words[index_to_modify] = new_word

    # Join the modified words back into a question
    modified_question = " ".join(words)

    return modified_question


# https://qa.fastforwardlabs.com/no%20answer/null%20threshold/bert/distilbert/exact%20match/f1/robust%20predictions/2020/06/09/Evaluating_BERT_on_SQuAD.html#F1
def normalize_text(s):
    """Removing articles and punctuation, and standardizing whitespace are all typical text processing steps."""

    def remove_articles(text):
        regex = re.compile(r"\b(a|an|the)\b", re.UNICODE)
        return re.sub(regex, " ", text)

    def white_space_fix(text):
        return " ".join(text.split())

    def remove_punc(text):
        exclude = set(string.punctuation)
        return "".join(ch for ch in text if ch not in exclude)

    def lower(text):
        return text.lower()

    return white_space_fix(remove_articles(remove_punc(lower(s))))


def compute_exact_match(prediction, truth):
    return int(normalize_text(prediction) == normalize_text(truth))


def compute_f1_recall(prediction, truth):
    pred_tokens = normalize_text(prediction).split()
    truth_tokens = normalize_text(truth).split()

    # if either the prediction or the truth is no-answer then f1 = 1 if they agree, 0 otherwise
    if len(pred_tokens) == 0 or len(truth_tokens) == 0:
        return int(pred_tokens == truth_tokens), int(pred_tokens == truth_tokens)

    common_tokens = set(pred_tokens) & set(truth_tokens)

    # if there are no common tokens then f1 = 0
    if len(common_tokens) == 0:
        return 0, 0

    prec = len(common_tokens) / len(pred_tokens)
    rec = len(common_tokens) / len(truth_tokens)

    return 2 * (prec * rec) / (prec + rec), rec


def get_gold_answers(example):
    """helper function that retrieves all possible true answers from a squad2.0 example"""

    gold_answers = [answer["text"] for answer in example.answers if answer["text"]]

    # if gold_answers doesn't exist it's because this is a negative example -
    # the only correct answer is an empty string
    if not gold_answers:
        gold_answers = [""]

    return gold_answers


def compute_metrics(results, mode="all"):
    """mode: all, update_context, no_update_context"""
    all_em_scores = []
    all_f1_scores = []
    all_recall_scores = []
    for i in range(len(results)):
        if results[i]["update_context"] == 0 and mode == "update_context":
            continue
        elif results[i]["update_context"] == 1 and mode == "no_update_context":
            continue

        prediction = results[i]["answer"]
        gold_answers = results[i]["gold_answers"]

        em_score = max((compute_exact_match(prediction, answer)) for answer in gold_answers)
        f1_score = max((compute_f1_recall(prediction, answer)[0]) for answer in gold_answers)
        recall_score = max((compute_f1_recall(prediction, answer)[1]) for answer in gold_answers)

        all_em_scores.append(em_score)
        all_f1_scores.append(f1_score)
        all_recall_scores.append(recall_score)

    print(f"\n\n====================== {mode=} ======================")
    print(f"Number of questions: {len(all_em_scores)}")
    print(f"Average EM: {sum(all_em_scores) / len(all_em_scores)}")
    print(f"Average F1: {sum(all_f1_scores) / len(all_f1_scores)}")
    print(f"Average Recall: {sum(all_recall_scores) / len(all_recall_scores)}")


def remove_common_words(text):
    # Tokenize the text into words
    words = word_tokenize(text)

    # Get the list of English stop words
    stop_words = set(stopwords.words("english"))

    # Filter out common words
    filtered_words = [word for word in words if word.lower() not in stop_words]

    # Reconstruct the text without common words
    filtered_text = " ".join(filtered_words)

    return filtered_text


def main(log_file="logs-100.txt", question_process=None):
    if not question_process:

        def question_process(x):
            return x

    print("\nAnalysis log file:", log_file)
    queries_file = "https://huggingface.co/datasets/thinkall/NaturalQuestionsQA/resolve/main/queries.jsonl"
    if not os.path.exists("/tmp/chromadb/queries.jsonl"):
        os.popen(f"wget -O /tmp/chromadb/queries.jsonl {queries_file}").read()
    queries = [json.loads(line) for line in open("/tmp/chromadb/queries.jsonl").readlines() if line]
    questions = [question_process(q["text"]) for q in queries]
    answers = [q["metadata"]["answer"] for q in queries]
    print("Total Number of questions:", len(questions))

    results = []
    _cnt_update_context = 0
    _idx_question = 0
    with open(log_file, "r") as f:
        lines = f.readlines()
        question = answer = update_context = None
        len_lines = len(lines)
        print(f"{len_lines=}")
        for idx in range(len_lines):
            # print(f"{idx=}, {lines[idx]}")
            if idx == 2 or lines[idx].startswith(">>>>>>>>>>>>>> case:"):
                update_context = 0
                question = lines[idx].split("case:")[1].replace("<<<<<<<<<<<<<<", "").strip()
            elif (
                "you should reply exactly `UPDATE CONTEXT`" not in lines[idx] and "update context" in lines[idx].lower()
            ):
                update_context = 1
                _cnt_update_context += 1
                if (
                    idx < len_lines - 5
                    and "----------------------------------------------------------------------" in lines[idx + 2]
                    and lines[idx + 5].startswith(">>>>>>>>>>>>>> case:")
                ):
                    answer = lines[idx].strip()
                    # print(f"{question=}")
                    res = {
                        "question": question,
                        "answer": answer,
                        "update_context": update_context,
                        "gold_answers": answers[_idx_question]
                        if questions[_idx_question] == question
                        else answers[questions.index(question)],
                    }
                    results.append(res)  # if res not in results else None
                    question = answer = update_context = None
                    _idx_question += 1
            elif (
                idx < len_lines - 5
                and "----------------------------------------------------------------------" in lines[idx + 2]
                and lines[idx + 5].startswith(">>>>>>>>>>>>>> case:")
            ) or idx == len_lines - 2:
                answer = lines[idx].strip()
                # print(f"{question=}")
                res = {
                    "question": question,
                    "answer": answer,
                    "update_context": update_context,
                    "gold_answers": answers[_idx_question]
                    if questions[_idx_question] == question
                    else answers[questions.index(question)],
                }
                results.append(res)  # if res not in results else None
                question = answer = update_context = None
                _idx_question += 1

    print(f"{_cnt_update_context=}")
    compute_metrics(results, mode="all")
    compute_metrics(results, mode="update_context")
    compute_metrics(results, mode="no_update_context")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--log_file", type=str, default="logs-clean-100.txt")
    args = parser.parse_args()
    main(args.log_file, question_process=remove_common_words)
