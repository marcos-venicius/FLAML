import json
import numpy as np

if __name__ == '__main__':
    with open('raw_ruin_names.json', encoding='utf-8') as fdata:
        data = json.load(fdata)

    formatted_data = []
    for example in data['examples']:
        suggestions = '\n'.join([key for key in example['target_scores']])
        sample = {
            'definition': '',
            'input': f'{example["input"]}.\n{suggestions}',
            'ground_truth': [candidate for candidate in example['target_scores'] if example['target_scores'][candidate] == 1]
        }
        formatted_data.append(sample)

    np.random.shuffle(formatted_data)
    train_samples = formatted_data[:250]
    test_samples = formatted_data[250:]

    with open('train_names_samples.json', 'w', encoding='utf-8') as fout:
        fout.write(json.dumps(train_samples))

    with open('test_names_samples.json', 'w', encoding='utf-8') as fout:
        fout.write(json.dumps(test_samples))