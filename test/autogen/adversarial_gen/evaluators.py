import re
from string import Template
from typing import List, Tuple
from flaml import autogen

from config import SUBSTRATE_CONFIG

class TargetLLM:
    def __init__(self, prompt_template: str, extract_last_line: bool = False) -> None:
        self.prompt_template = prompt_template
        self.extract_last_line = extract_last_line

    def run_example(self, input: str) -> str:
        data_dict = {
            'input': input
        }
        prompt = Template(self.prompt_template).substitute(data_dict)
        try:
            response = autogen.oai.ChatCompletion.create(
                prompt=prompt,
                config_list=SUBSTRATE_CONFIG
            )['choices'][0]['message']['content']
        except Exception as ex:
            print(ex)
            return 'ERROR'

        if self.extract_last_line:
            lines = response.strip().split('\n')
            return lines[-1]
        return response

class Evaluator:
    def __init__(self, target_llm_prompt_template: str, adversarial_threshold: float) -> None:
        self.target_llm = TargetLLM(target_llm_prompt_template)
        self.adversarial_threshold = adversarial_threshold

    def evaluate(self, sample: str) -> Tuple[int, str, str, str]:
        raise NotImplementedError('Abstract method.')
    
class NamedCriteriaEvaluator(Evaluator):
    _BASE_PROMPT = None

    def __init__(self, target_llm_prompt_template: str, adversarial_threshold: float, instructions: str, criteria_names: List[str]) -> None:
        super().__init__(target_llm_prompt_template, adversarial_threshold)
        self.instructions = instructions
        self.criteria_names = criteria_names

    def evaluate(self, sample: str) -> Tuple[int, str, str, str]:
        if self._BASE_PROMPT is None:
            raise NotImplementedError('Abstract class. Please inherit this class and define the _BASE_PROMPT class variable.')
        
        output = self.target_llm.run_example(sample)
        data_dict = self._build_data_dict(sample, output)
        prompt = Template(self._BASE_PROMPT).substitute(data_dict)
        try:
            response = autogen.oai.ChatCompletion.create(
                prompt=prompt,
                config_list=SUBSTRATE_CONFIG
            )['choices'][0]['message']['content']
        except:
            return -1, sample, output, 'ERROR: Prompt failed to execute.'

        regex_patterns = [f'{name}: [0-1](.\d)?\d*' for name in self.criteria_names]
        regex_matches = [re.search(pattern, response) for pattern in regex_patterns]

        no_match = [1 if match is None else 0 for match in regex_matches]
        if sum(no_match) > 0:
            return -2, sample, output, 'ERROR: Failed to extract criteria scores.'

        scores = [float(match.group(0).split(': ')[1]) for match in regex_matches]
        if min(scores) < self.adversarial_threshold:
            return 0, sample, output, f'{response}\nEVALUATION RESULT: INCORRECT'
        return 1, sample, output, f'{response}\nEVALUATION RESULT: INCORRECT'

    def _build_data_dict(self, sample: str, output: str) -> dict:
        raise NotImplementedError('Abstract method. Please override _build_data_dict_method')

class MathNewOperatorEvaluator(Evaluator):
    def evaluate(self, sample: str) -> Tuple[int, str, str, str]:
        pattern = '[+-]?\d+( ?[@#] ?\d+)+'
        match = re.search(pattern, sample)
        if match is None:
            return -1, None, None, 'ERROR: Example incorrectly formatted.'
        matched_exp = match.group(0)

        # Return -1 if the sample is not properly formatted.
        expression = matched_exp.replace('@', '+').replace('#', '-')
        try:
            expected_output = eval(expression)
            expected_output = float(expected_output) # Ensuring result is a numeric value
        except SyntaxError:
            return -1, matched_exp, None, 'ERROR: Example incorrectly formatted.'
        except TypeError:
            return -1, matched_exp, None, 'ERROR: Example incorrectly formatted.'
        except NameError:
            return -1, matched_exp, None, 'ERROR: Example incorrectly formatted.'

        # Retrieving output from target LLM system
        output = self.target_llm.run_example(matched_exp)

        # Return -1.0 in the case of inconclusive results due to bad formatting.
        if 'FINAL ANSWER: ' not in output:
            return -1, matched_exp, output, 'ERROR: Final answer not found.'
        answer = output.strip().split('FINAL ANSWER: ')[-1]
        try:
            answer = float(answer)
        except ValueError:
            return -1, matched_exp, output, 'ERROR: Final answer not numeric!'
        
        # Return 1 if results match expression evaluatio and 0 otherwise.
        if answer == expected_output:
            return 1, matched_exp, output, 'CORRECT'
        return 0, matched_exp, output, 'ERROR: Output does not match expected result.'
    
class ReviewSummarizationEvaluator(NamedCriteriaEvaluator):
    _BASE_PROMPT = """Your task is to evaluate a summary produced for a specific task. You will receive the task instructions and the produced summary. Please evaluate the summary according to the following criteria.

### EVALUATION CRITERIA ###
- Faithfulness (0-1). A faithful summary contains only information available in the original text. If the summary contains only information derived from the original text, it should receive a score of 1. Otherwise, it should receive a score of 0. Even if the summary is missing important information, it should not affect its faithfulness score.
- Own Words (0-1). A good summary should use its own words to capture the information in the original text. If the summary contains 5 or more words copied directly from the review, its "Own Words" score should be 0. Otherwise, it should receive a score of 1.

### TASK INSTRUCTIONS ###
$task_instructions

### ORIGINAL TEXT ###
$text

### SUMMARY ###
$summary

### EVALUATION FORM (CRITERIA: SCORE - EXPLANATION) ###
"""
    def __init__(self, target_llm_prompt_template: str, adversarial_threshold: float, instructions: str) -> None:
        criteria_names = ['Faithfulness', 'Own Words']
        super().__init__(target_llm_prompt_template, adversarial_threshold, instructions, criteria_names)

    def evaluate(self, sample: str) -> Tuple[int, str, str, str]:
        lines = sample.strip().split('\n')
        reviews = None
        for line in lines:
            if line.strip().startswith('Review_1:'):
                reviews = line.strip()
                break
        if reviews is None:
            return -3, sample, None, 'ERROR: Input not properly formatted.'
        
        return super().evaluate(reviews)
    
    def _build_data_dict(self, sample: str, output: str) -> dict:
        return {
            'task_instructions': self.instructions,
            'text': sample,
            'summary': output
        }
    
class TextSimplificationEvaluator(NamedCriteriaEvaluator):
    _BASE_PROMPT = """Your task is to evaluate a simplified version of a text. You will receive additional task instructions, the original text and its simplified version. Please evaluate the simplified text according to the following criteria:

### EVALUATION CRITERIA ###
- Simplification (0-1). The simplified text should use simpler English words, simpler grammatical structures or be shorter than the original text. A simpler text might omit details that are not crucial to the understanding of the text, such as definitions, categories or numerical data. If the simplified text is indeed simpler than the original text, it should receive a score of 1. Otherwise, it should receive a score of 0.
- Faithfulness (0-1). The simplified text should not create new facts or ideas. If the simplified text creates any information that is not present in the original text, it should receive a score of 0. Otherwise, it should receive a score of 1.

### TASK INSTRUCTIONS ###
$task_instructions

### ORIGINAL TEXT ###
$text

### SIMPLIFIED TEXT ###
$simplified_text

### EVALUATION FORM (CRITERIA: SCORE - EXPLANATION) ###
"""
    def __init__(self, target_llm_prompt_template: str, adversarial_threshold: float, instructions: str) -> None:
        criteria_names = ['Simplification', 'Faithfulness']
        super().__init__(target_llm_prompt_template, adversarial_threshold, instructions, criteria_names)

    def _build_data_dict(self, sample: str, output: str) -> dict:
        return {
            'task_instructions': self.instructions,
            'text': sample,
            'simplified_text': output
        }
    
class ExplanationEvaluator(NamedCriteriaEvaluator):
    _BASE_PROMPT = """Your task is to evaluate an explanation for an answer to a question. You will receive additional task instructions, the question, the answer and the explanation. Please evaluate the explanation according to the following criteria:

### EVALUATION CRITERIA ###
- Corroboration (0-1). We say an explanation corroborates with the answer if we can derive the answer from the explanation. If the explanation is not connected to the answer or we cannot derive the answer from the explanation, it should receive a score of 0. Otherwise, it should receive a score of 1.
- Internal Consistency (0-1). An explanation has internal consistency if we cannot derive contradictions from it and whole sequence of logical elements make sense together. If all elements of the explanation are connected together in a logical way and no contradiction can be derived from logical elements within the explanation, it should receive a score of 1. Otherwise, it should receive a score of 0.
- Clarity (0-1). An explanation is clear if it is well-written and easy to understand. If the explanation is written in such way that is confusing, it should receive a score of 0. Otherwise, it should receive a score of 1.

### TASK INSTRUCTIONS ###
$task_instructions

### QUESTION AND ANSWER ###
$qa

### EXPLANATION ###
$explanation

### EVALUATION FORM (CRITERIA: SCORE - EXPLANATION) ###
"""
    def __init__(self, target_llm_prompt_template: str, adversarial_threshold: float, instructions: str) -> None:
        criteria_names = ['Corroboration', 'Internal Consistency', 'Clarity']
        super().__init__(target_llm_prompt_template, adversarial_threshold, instructions, criteria_names)
    
    def _build_data_dict(self, sample: str, output: str) -> dict:
        return {
            'task_instructions': self.instructions,
            'qa': sample,
            'explanation': output
        }
    
class StoryCompositionEvaluator(NamedCriteriaEvaluator):
    _BASE_PROMPT = """Your task is to evaluate a story produced based on a list of facts. You will receive additional task instructions, the list of facts and the produced story. Please evaluate the story according to the following criteria:

### EVALUATION CRITERIA ###
- Appropriate Length (0-1). The story should contain 100 to 1000 words. If the story length is within this range, its score should be 1. Otherwise, it should be 0.
- Coverage (0-1). The story should contain all the facts provided. The coverage score is derived as the proportion of the facts from the list incorporated in the story.
- Textual Quality (0-1). Textual quality refers to how fluent, coherent and engaging the story is. A high quality story would be well-written, interesting and able to keep the reader engaged.

### TASK INSTRUCTIONS ###
$task_instructions

### LIST OF FACTS ###
$facts

### STORY ###
$story

### EVALUATION FORM (CRITERIA: SCORE - EXPLANATION) ###
"""

    def __init__(self, target_llm_prompt_template: str, adversarial_threshold: float, instructions: str) -> None:
        criteria_names = ['Appropriate Length', 'Coverage', 'Textual Quality']
        super().__init__(target_llm_prompt_template, adversarial_threshold, instructions, criteria_names)

    def _build_data_dict(self, sample: str, output: str) -> dict:
        return {
            'task_instructions': self.instructions,
            'facts': sample,
            'story': output
        }
    
class TitleGenerationEvaluator(NamedCriteriaEvaluator):
    _BASE_PROMPT = """Your task is to evaluate a title based on a paragraph of a research paper. You will receive additional task instructions, the paragraph, and the title. Please evaluate the title according to the following criteria:

### EVALUATION CRITERIA ###
- Length (0-1). A title should be no longer than 100 words. If the title has more than 100 words, it should receive a score of 0. Otherwise, it should receive a score of 1.
- Informative (0-1). A title should be informative, being able to describe the content of the paragraph in a short text. If the title is not aligned with the content of the paragraph or is not informative enough such that a reader would not be able to understand what the paragraph is about, it should receive a score of 0. Otherwise, it should receive a score of 1.

### TASK INSTRUCTIONS ###
$task_instructions

### QUESTION AND ANSWER ###
$qa

### EXPLANATION ###
$explanation

### EVALUATION FORM (CRITERIA: SCORE - EXPLANATION) ###
"""

    def __init__(self, target_llm_prompt_template: str, adversarial_threshold: float, instructions: str) -> None:
        criteria_names = ['Length', 'Informative']
        super().__init__(target_llm_prompt_template, adversarial_threshold, instructions, criteria_names)

    def _build_data_dict(self, sample: str, output: str) -> dict:
        return {
            'task_instructions': self.instructions,
            'qa': sample,
            'explanation': output
        }
    
class ParaphrasingEvaluator(NamedCriteriaEvaluator):
    _BASE_PROMPT = """Your task is to evaluate a sentence constructed by paraphrasing another sentence. You will receive additional task instructions, the original sentence, and the paraphrase. Please evaluate the paraphrase according to the following criteria:

### EVALUATION CRITERIA ###
- Preserved Information (0-1). A paraphrase should preserve the same information present in the original sentence. If the information on both sentences are the same, it should receive a score of 1. Otherwise, it should receive a score of 0.
- Different Wording (0-1). A paraphrase should use different words than the original sentence, with the exception of common words such as articles and prepositions. If the uncommon words used in the paraphrase are mostly different than the ones used in the original sentence, it should receive a score of 1. Otherwise, it should receive a score of 0.

### TASK INSTRUCTIONS ###
$task_instructions

### ORIGINAL SENTENCE ###
$text

### PARAPHRASE ###
$paraphrase

### EVALUATION FORM (CRITERIA: SCORE - EXPLANATION) ###
"""

    def __init__(self, target_llm_prompt_template: str, adversarial_threshold: float, instructions: str) -> None:
        criteria_names = ['Preserved Information', 'Different Wording']
        super().__init__(target_llm_prompt_template, adversarial_threshold, instructions, criteria_names)

    def _build_data_dict(self, sample: str, output: str) -> dict:
        return {
            'task_instructions': self.instructions,
            'text': sample,
            'paraphrase': output
        }
    
class BooleanExpressionEvaluator(Evaluator):
    def evaluate(self, sample: str) -> Tuple[int, str, str, str]:
        try:
            expected_output = eval(sample)
        except:
            return -1, sample, None, 'ERROR: Invalid sample'
        output = self.target_llm.run_example(sample)
        if 'FINAL ANSWER: ' not in output:
            return -1, sample, output, 'ERROR: Final answer not found.'
        answer = output.split('FINAL ANSWER: ')[-1]
        result = answer.lower() == 'true'

        if result == expected_output:
            return 1, sample, output, 'EVALUATION RESULT: CORRECT'
        return 0, sample, output, 'EVALUATION RESULT: INCORRECT'

class MovieRecommendationEvaluator(Evaluator):
    _BASE_PROMPT = """You are a movie specialist AI agent focused on providing movie recommendation to customers. You will receive a list of previously enjoyed movies for a particular user, and your job is to provide a recommendation based on a list of potential recommendations.
In order to pick a good recommendation from the list, you should choose the most similar movie to the list of previously enjoyed movies. A movie is similar to another based on a series of characteristics such as (but not limited to):
- same or similar genre;
- same or similar themes present on both movies;
- same or similar target audience;
- same or similar cast.

For each potential recommendation, calculate a similarity score, ranging from 0 to 100, to the list of previously enjoyed movies. Then, indicate the movie with the highest score as your recommendation.

# Formatting instructions
Please provide your recommendation using the following format.

- <name of 1st potential recommendation> - <score>. <explanation>
- <name of 2nd potential recommendation> - <score>. <explanation>
- <name of 3rd potential recommendation> - <score>. <explanation>
- <name of 4th potential recommendation> - <score>. <explanation>

Recommendation: <name of potential recommendation with highest score>

# Input
$input
"""
    def evaluate(self, sample: str) -> Tuple[int, str, str, str]:
        output = self.target_llm.run_example(sample)
        if 'recommendation: ' not in output.lower():
            return -1, sample, output, 'ERROR: Failed to retrieve recommendation from target LLM.'
        output = output.lower().split('recommendation: ')[-1].strip().strip('.')

        data_dict = {'input': sample}
        prompt = Template(self._BASE_PROMPT).substitute(data_dict)
        try:
            response = autogen.oai.ChatCompletion.create(
                prompt=prompt,
                config_list=SUBSTRATE_CONFIG
            )['choices'][0]['message']['content']
        except:
            return -1, sample, output, 'ERROR: Failed to execute evaluation prompt.'
        
        if 'Recommendation:' not in response:
            return -1, sample, output, 'ERROR: Failed to extract recommendation.'
        recommendation = response.split('Recommendation:')[-1].strip()

        if recommendation.lower() == output.strip().lower():
            return 1, sample, output, 'EVALUATION RESULT: CORRECT'
        return 0, sample, output, 'EVALUATION RESULT: INCORRECT'
    
class RuinNamesEvaluator(Evaluator):
    _BASE_PROMPT = """Your are a comedian AI agent focusing on evaluating puns and jokes. The particular joke you will be evaluating is based on editing the name of an artist or a movie to make it humurous. You will receive a list of potential edits and your task is to pick the best one.
In order to pick a good edit from the list, you should assess the following:
- edits should modify a single character of the original name;
- edits should lead to existing English words or expressions;
- edits should be humurous.

For each potential edit, calculate a quality score, ranging from 0 to 100. Then, indicate the edit with the highest score as the best joke.

# Formatting instructions
Please provide your assessment using the following format.

- <name of 1st potential edit> - <score>. <explanation>
- <name of 2nd potential edit> - <score>. <explanation>
- <name of 3rd potential edit> - <score>. <explanation>
- <name of 4th potential edit> - <score>. <explanation>

Best Edit: <name of potential edit with highest score>

# Input
$input
"""
    def evaluate(self, sample: str) -> Tuple[int, str, str, str]:
        output = self.target_llm.run_example(sample)
        if 'best edit: ' not in output.lower():
            return -1, sample, output, 'ERROR: Failed to retrieve best edit from target LLM.'
        output = output.lower().split('best edit: ')[-1].strip().strip('.')

        data_dict = {'input': sample}
        prompt = Template(self._BASE_PROMPT).substitute(data_dict)
        try:
            response = autogen.oai.ChatCompletion.create(
                prompt=prompt,
                config_list=SUBSTRATE_CONFIG
            )['choices'][0]['message']['content']
        except:
            return -1, sample, output, 'ERROR: Failed to execute evaluation prompt.'
        
        if 'Best Edit:' not in response:
            return -1, sample, output, 'ERROR: Failed to extract recommendation.'
        best = response.split('Best Edit:')[-1].strip()

        if best.lower() == output.strip().lower():
            return 1, sample, output, 'EVALUATION RESULT: CORRECT'
        return 0, sample, output, 'EVALUATION RESULT: INCORRECT'

class EvaluatorFactory:
    @classmethod
    def create(cls, evaluator_name: str, adversarial_threshold: float, target_llm_prompt_template: str, task_instructions: str) -> Evaluator:
        if evaluator_name == 'MathNewOperatorEvaluator':
            return MathNewOperatorEvaluator(target_llm_prompt_template, adversarial_threshold)
        if evaluator_name == 'ReviewSummarizationEvaluator':
            return ReviewSummarizationEvaluator(target_llm_prompt_template, adversarial_threshold, task_instructions)
        if evaluator_name == 'TextSimplificationEvaluator':
            return TextSimplificationEvaluator(target_llm_prompt_template, adversarial_threshold, task_instructions)
        if evaluator_name == 'ExplanationEvaluator':
            return ExplanationEvaluator(target_llm_prompt_template, adversarial_threshold, task_instructions)
        if evaluator_name == 'StoryCompositionEvaluator':
            return StoryCompositionEvaluator(target_llm_prompt_template, adversarial_threshold, task_instructions)
        if evaluator_name == 'TitleGenerationEvaluator':
            return TitleGenerationEvaluator(target_llm_prompt_template, adversarial_threshold, task_instructions)
        if evaluator_name == 'ParaphrasingEvaluator':
            return ParaphrasingEvaluator(target_llm_prompt_template, adversarial_threshold, task_instructions)
        if evaluator_name == 'BooleanExpressionEvaluator':
            return BooleanExpressionEvaluator(target_llm_prompt_template, adversarial_threshold)
        if evaluator_name == 'MovieRecommendationEvaluator':
            return MovieRecommendationEvaluator(target_llm_prompt_template, adversarial_threshold)
        if evaluator_name == 'RuinNamesEvaluator':
            return RuinNamesEvaluator(target_llm_prompt_template, adversarial_threshold)
        raise NotImplementedError(f'No evaluator with name {evaluator_name} available.')
