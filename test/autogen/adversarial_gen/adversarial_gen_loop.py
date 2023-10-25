import argparse
import json
import numpy as np

from tqdm import tqdm

from evaluators import EvaluatorFactory
from generators import GeneratorFactory
from sampling import SamplerFactory

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_file', type=str, required=True)
    parser.add_argument('--target_llm_prompt', type=str, required=True)
    parser.add_argument('--num_few_shot', type=int, required=False, default=3)
    parser.add_argument('--evaluator', type=str, required=True)
    parser.add_argument('--generator', type=str, required=True)
    parser.add_argument('--sampler', type=str, required=True)
    parser.add_argument('--sampler_threshold', type=float, required=False, default=0.9)
    parser.add_argument('--adversarial_threshold', type=float, required=False, default=0.5)
    parser.add_argument('--num_samples', type=int, required=False, default=10)
    parser.add_argument('--results_file', type=str, required=True)
    args = parser.parse_args()

    np.random.seed(42)

    with open(args.data_file, encoding='utf-8') as fdata:
        data = json.load(fdata)
    inputs = [sample['input'] for sample in data]
    with open(args.target_llm_prompt, encoding='utf-8') as fprompt:
        prompt_template = fprompt.read()

    # Setting up agents and sampler
    generator = GeneratorFactory.create(args.generator, data[0]['definition'])
    evaluator = EvaluatorFactory.create(args.evaluator, args.adversarial_threshold, prompt_template, data[0]['definition'])
    sampler = SamplerFactory.create(args.sampler, inputs, evaluator, args.sampler_threshold, '$input')

    new_examples = []
    num_adversarial = 0
    num_inconclusive = 0
    for _ in tqdm(range(args.num_samples), desc='Generating new samples...'):
        few_shot_examples = sampler.sample(args.num_few_shot)
        few_shot_str = '\n\n'.join(few_shot_examples)

        # Generate new sample
        new_sample = generator.generate(few_shot_examples)

        # Run evaluator
        evaluation, new_sample, output, feedback = evaluator.evaluate(new_sample)
        cur_example = {
            'input': new_sample,
            'output': output,
            'evaluation': evaluation
        }
        new_examples.append(cur_example)
        if evaluation < 0:
            num_inconclusive += 1
        elif evaluation == 0:
            num_adversarial += 1

    with open(args.results_file, 'w', encoding='utf-8') as fout:
        fout.write(json.dumps(new_examples))

    print(f'Inconclusive rate: {num_inconclusive / len(new_examples)}')
    print(f'Adversarial rate: {num_adversarial / len(new_examples)}')
