from string import Template
from flaml import autogen

from config import SUBSTRATE_CONFIG
    
class Generator():
    _BASE_PROMPT = """You are a creative AI agent. You will be provided a task, alongside with some task information, such as further instructions and examples. Your goal is to produce ONE new, hard and complex example for the same task so that other systems will FAIL when attempting to solve the example you generate. In doing so, you should follow these guidelines:
1> ALWAYS generate only a SINGLE new example, even if you are provided with multiple examples.
2> When generating a new example, follow the formatting of the examples provided.
3> Your new example should be a valid and adequate input for the task described below.
4> Your new example should be hard and complex.
5> NEVER provide the solution for the new example.
6> DO NOT write anything after creating the new example.
7> ALWAYS answer in the format "Input: <NEW EXAMPLE>".

### TASK DESCRIPTION ###
$task_instructions

### EXAMPLES ###
$few_shot_examples

### NEW EXAMPLE ###
Input: 
"""
    def __init__(self, instructions: str) -> None:
        self.instructions = instructions

    def generate(self, few_shot_examples: str) -> str:
        data_dict = {
            'task_instructions': self.instructions,
            'few_shot_examples': few_shot_examples
        }
        prompt = Template(self._BASE_PROMPT).substitute(data_dict)
        try:
            return autogen.oai.ChatCompletion.create(
                prompt=prompt,
                config_list=SUBSTRATE_CONFIG
            )['choices'][0]['message']['content']
        except:
            return 'ERROR'
        
class GeneratorFactory:
    @classmethod
    def create(cls, generator_name: str, task_instructions: str) -> Generator:
        if generator_name == 'Generator':
            return Generator(task_instructions)
        raise NotImplementedError(f'Generator named {generator_name} not available.')