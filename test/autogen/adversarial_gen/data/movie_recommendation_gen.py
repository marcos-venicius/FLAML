import json
import numpy as np

if __name__ == '__main__':
    with open('raw_movie_recommendation.json', encoding='utf-8') as fdata:
        data = json.load(fdata)

    formatted_data = []
    for example in data['examples']:
        suggestions = '\n'.join([key for key in example['target_scores']])
        sample = {
            'definition': 'You are a movie specialist AI agent. Your job is to provide movie recommendations for users. For that, you will receive a list of movies the user has watched and enjoyed, as well as a list of potential recommendations. You must pick the movie that is the most similar to the previously enjoyed movies.',
            'input': f'Previously enjoyed: {example["input"].strip(":")}.\nPotential recommendations:\n{suggestions}',
            'ground_truth': [candidate for candidate in example['target_scores'] if example['target_scores'][candidate] == 1]
        }
        formatted_data.append(sample)

    np.random.shuffle(formatted_data)
    train_samples = formatted_data[:250]
    test_samples = formatted_data[250:]

    with open('train_recommendation_samples.json', 'w', encoding='utf-8') as fout:
        fout.write(json.dumps(train_samples))

    with open('test_recommendation_samples.json', 'w', encoding='utf-8') as fout:
        fout.write(json.dumps(test_samples))