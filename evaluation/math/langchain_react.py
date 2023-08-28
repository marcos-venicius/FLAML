from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent
from langchain.agents import AgentType
from langchain.tools.python.tool import PythonREPLTool

from flaml.autogen.math_utils import eval_math_responses, get_answer



class ReAct:
    def __init__(self, api_key) -> None:
        self.llm = ChatOpenAI(model_name='gpt-4', openai_api_key=api_key)
        tools = [PythonREPLTool()]
        self.agent = initialize_agent(tools, self.llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)
        pass

    def solve_one_problem(self, problem):
        result = self.agent.run(problem['problem'])
        metrics = eval_math_responses([result], problem["solution"])
        return {
            # must have 
            "response_with_ans": result,
            "correct_ans": get_answer(problem["solution"]),
            "voted_answer": result,  
            "is_correct":  bool(metrics["success_vote"]),
        }


