import argparse
import json
import numpy as np

from flaml import autogen
from string import Template
from tqdm import tqdm

OAI_CONFIG = [
    {
        'model': 'foundryt16',
        'api_key': '6910d785a4b74dac8e12c991bcb331b3',
        'api_base': 'https://foundry-eastus.openai.azure.com/',
        'api_type': 'azure',
        'api_version': '2023-06-01-preview'
    }
]

class Generator:
    _BASE_PROMPT = """You are a creative AI agent. You will be provided a task, alongside with some task information, such as further instructions and examples. Your goal is to produce new, hard and complex examples for the same task. In doing so, you should follow these guidelines:
1> ALWAYS generate only a SINGLE new example, even if you are provided with multiple examples.
2> When generating a new example, follow the formatting of the examples provided.
3> You new example should be hard and complex.
4> NEVER provide the solution for the new example.

### TASK INSTRUCTION ###
$task_instructions

### EXAMPLES ###
$few_shot_examples
"""

    def __init__(self, task_description):
        data_dict = {'task_instructions': task_description}
        self.prompt_template = Template(self._BASE_PROMPT).safe_substitute(data_dict)

    def generate(self, few_shot_examples):
        all_few_shot = '\n'.join(few_shot_examples)
        few_shot_str = f"Here are {len(few_shot_examples)} examples to help you:\n{all_few_shot}"
        data_dict = {'few_shot_examples': few_shot_str}
        prompt = Template(self.prompt_template).substitute(data_dict)
        try:
            return autogen.oai.ChatCompletion.create(
                prompt=prompt,
                config_list=OAI_CONFIG
            )['choices'][0]['message']['content']
        except:
            return ''

class TargetLLM:
    _BASE_PROMPT = """$task_description

### POSITIVE EXAMPLES ###
$positive_examples

### NEGATIVE EXAMPLES ###
$negative_examples

### CURRENT EXAMPLE ###
Input: $input
Output: 
"""
    def __init__(self, task_description, positive_examples, negative_examples):
        data_dict = {
            'task_description': task_description,
            'positive_examples': '\n'.join([f'Input: {x["input"]}\nOutput: {x["output"]}\nExplanation: {x["explanation"]}' for x in positive_examples]),
            'negative_examples': '\n'.join([f'Input: {x["input"]}\nOutput: {x["output"]}\nExplanation: {x["explanation"]}' for x in negative_examples]),
        }
        self.prompt_template = Template(self._BASE_PROMPT).safe_substitute(data_dict)

    def run_example(self, example):
        data_dict = {'input': example}
        prompt = Template(self.prompt_template).substitute(data_dict)
        try:
            return autogen.oai.ChatCompletion.create(
                prompt=prompt,
                config_list=OAI_CONFIG
            )['choices'][0]['message']['content']
        except:
            return ''
    
class Evaluator:
    _BASE_PROMPT = """You are an assistant AI responsible for verifying the solution for an example of a task. You will be provided with a task, alongside with some task information, such as further instructions or correctly and incorrectly answered examples. You will also receive an additional example and a solution specifically designed for this example.
Your goal is to evaluate whether the solution for the example is CORRECT or INCORRECT. In doing so, follow these guidelines:
1> If some explanation or reasoning is provided alongside with the solution, assess each step of the solution to verify its correctness.
2> If no explanation or reasoning is provided alonside with the solution, break down the problem into smaller problems and think step-by-step.
3> Always conclude your evaluation by writing EVALUATION RESULT: CORRECT or EVALUATION RESULT: INCORRECT on a new line. DO NOT add anything after this line.

### TASK INSTRUCTION ###
$task_description

### POSITIVE EXAMPLES ###
$positive_examples

### NEGATIVE EXAMPLES ###
$negative_examples

### CURRENT EXAMPLE ###
Input: $input
Output: $output
"""
    def __init__(self, task_description, positive_examples, negative_examples):
        data_dict = {
            'task_description': task_description,
            'positive_examples': '\n'.join([f'Input: {x["input"]}\nOutput: {x["output"]}\nExplanation: {x["explanation"]}' for x in positive_examples]),
            'negative_examples': '\n'.join([f'Input: {x["input"]}\nOutput: {x["output"]}\nExplanation: {x["explanation"]}' for x in negative_examples]),
        }
        self.prompt_template = Template(self._BASE_PROMPT).safe_substitute(data_dict)

    def evaluate(self, input, output):
        data_dict = {'input': input, 'output': output}
        prompt = Template(self.prompt_template).substitute(data_dict)
        try:
            return autogen.oai.ChatCompletion.create(
                prompt=prompt,
                config_list=OAI_CONFIG
            )['choices'][0]['message']['content']
        except:
            return ''
    
class OracleEvaluator:
    _BASE_PROMPT = """You are an assistant AI responsible for verifying the solution for an example of a task. You will be provided with a task, alongside with some task information, such as further instructions or correctly and incorrectly answered examples. You will also receive an additional example, a solution found by another agent for this example and the expected solution.
Your goal is to verify if the solution provided for the example matches the expected solution. Please follow these guidelines:
1> If the provided solution matches the expected solution, write EVALUATION RESULT: CORRECT.
2> If the provided solution matches the expected solution, write EVALUATION RESULT: INCORRECT.
3> DO NOT write anything else.

### TASK INSTRUCTION ###
$task_description

### POSITIVE EXAMPLES ###
$positive_examples

### NEGATIVE EXAMPLES ###
$negative_examples

### CURRENT EXAMPLE ###
Input: $input
Output: $output
Expected Output: $expected_output
"""
    def __init__(self, task_description, positive_examples, negative_examples):
        data_dict = {
            'task_description': task_description,
            'positive_examples': '\n'.join([f'Input: {x["input"]}\nOutput: {x["output"]}\nExplanation: {x["explanation"]}' for x in positive_examples]),
            'negative_examples': '\n'.join([f'Input: {x["input"]}\nOutput: {x["output"]}\nExplanation: {x["explanation"]}' for x in negative_examples]),
        }
        self.prompt_template = Template(self._BASE_PROMPT).safe_substitute(data_dict)

    def evaluate(self, input, output, ground_truth):
        data_dict = {'input': input, 'output': output, 'expected_output': ground_truth}
        prompt = Template(self.prompt_template).substitute(data_dict)
        try:
            return autogen.oai.ChatCompletion.create(
                prompt=prompt,
                config_list=OAI_CONFIG
            )['choices'][0]['message']['content']
        except:
            return ''

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_file', type=str, required=True)
    parser.add_argument('--num_few_shot', type=int, required=False, default=3)
    parser.add_argument('--filter_adversarial', type=bool, required=False, default=False)
    parser.add_argument('--num_iter', type=int, required=False, default=10)
    parser.add_argument('--results_file', type=str, required=True)
    args = parser.parse_args()

    np.random.seed(42)

    with open(args.data_file, encoding='utf-8') as fdata:
        data = json.loads(fdata.read())

    # Setting up generator module
    generator = Generator(data['Definition'][0])

    # Setting up target LLM module for which we are creating adversarial examples
    target_llm = TargetLLM(data['Definition'][0], data['Positive Examples'], data['Negative Examples'])

    # Setting up evaluator module
    evaluator = Evaluator(data['Definition'][0], data['Positive Examples'], data['Negative Examples'])

    if args.filter_adversarial:
        oracle = OracleEvaluator(data['Definition'][0], data['Positive Examples'], data['Negative Examples'])
        samples = data['Instances']
        adversarial_samples = []
        for sample in tqdm(samples, desc='Retrieving adversarial examples from dataset...'):
            output = target_llm.run_example(sample['input'])
            evaluation = oracle.evaluate(sample['input'], output, sample['output'])
            lines = evaluation.strip().split('\n')
            last_line = lines[-1]
            if last_line.strip().lower() == 'evaluation result: incorrect':
                adversarial_samples.append(sample)
        print(f'Found {len(adversarial_samples)} adversarial examples out of {len(samples)} examples.')
        data['Instances'] = adversarial_samples

    new_examples = []
    for _ in tqdm(range(args.num_iter), desc='Generating new samples...'):
        # Sampling few-shot examples for generator
        indices = np.random.choice(len(data['Instances']), args.num_few_shot, replace=False)
        few_shot_examples = [data['Instances'][idx]['input'] for idx in range(len(data['Instances'])) if idx in indices]

        # Generate example
        example = generator.generate(few_shot_examples)

        # Run example against LLM module
        output = target_llm.run_example(example)

        # Run evaluator
        evaluation = evaluator.evaluate(example, output)

        # Process evaluation and classify example as ADVERSARIAL, NON-ADVERSARIAL or INCONCLUSIVE
        classification = 'inconclusive'
        lines = evaluation.strip().split('\n')
        last_line = lines[-1]
        if last_line.strip().lower() == 'evaluation result: correct':
            classification = 'non-adversarial'
        elif last_line.strip().lower() == 'evaluation result: incorrect':
            classification = 'adversarial'

        # Log example and results
        cur_example = {
            'input': example,
            'output': output,
            'evaluation': evaluation,
            'classification': classification
        }
        new_examples.append(cur_example)

    # Generate metrics based on results
    inconclusive_count = 0
    adversarial_count = 0
    nonadversarial_count = 0
    for example in new_examples:
        if example['classification'] == 'inconclusive':
            inconclusive_count += 1
        elif example['classification'] == 'adversarial':
            adversarial_count += 1
        elif example['classification'] == 'non-adversarial':
            nonadversarial_count += 1
    print(f'Inconclusive rate: {inconclusive_count / args.num_iter}')
    print(f'Adversarial rate: {adversarial_count / (adversarial_count + nonadversarial_count)}')

    with open(args.results_file, 'w', encoding='utf-8') as fout:
        fout.write(json.dumps(new_examples))
        