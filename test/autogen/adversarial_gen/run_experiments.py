import subprocess

experiments = {
    'math': 'MathNewOperatorEvaluator',
    #'reviewsum': ('ReviewSummarizationEvaluator'),
    #'simplification': ('TextSimplificationEvaluator'),
    #'explanation': ('ExplanationEvaluator'),
    #'composition': ('StoryCompositionEvaluator'),
    #'title': ('TitleGenerationEvaluator'),
    #'paraphrasing': ('ParaphrasingEvaluator'),
    'boolean': ('BooleanExpressionEvaluator'),
    'recommendation': ('MovieRecommendationEvaluator'),
    'names': ('RuinNamesEvaluator'),
}

for exp in experiments:
    args = {
        'data_file': f'data/train_{exp}_samples.json',
        'target_llm_prompt': f'prompts/target_llm_{exp}.txt',
        'num_few_shot': 5,
        'evaluator': experiments[exp],
        'generator': 'Generator',
        'sampler': 'SimilarityThresholdSampler',
        'sampler_threshold': 0.85,
        'adversarial_threshold': 0.5,
        'num_samples': 500,
        'results_file': f'results/{exp}_sim0.85.json'
    }
    args_str = ' '.join([f"--{key} {args[key]}" for key in args])
    cmd = f"python adversarial_gen_loop.py {args_str}"
    print(f"Running: {cmd}")
    subprocess.call(cmd)