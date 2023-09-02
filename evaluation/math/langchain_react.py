from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent
from langchain.agents import AgentType
from langchain.tools.python.tool import PythonREPLTool
from langchain.agents.agent_toolkits import create_python_agent
from flaml.autogen.math_utils import eval_math_responses, get_answer
from utils import remove_asy_sections


class ReAct:
    def __init__(self, api_key) -> None:
        self.llm = ChatOpenAI(model_name="gpt-4", openai_api_key=api_key)
        tools = [PythonREPLTool()]
        self.agent = initialize_agent(tools, self.llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)

        # # https://python.langchain.com/docs/integrations/toolkits/python
        # self.agent = create_python_agent(
        #     llm=self.llm,
        #     tool=PythonREPLTool(),
        #     verbose=True,
        #     agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        # )

    def solve_one_problem(self, problem):
        result = None
        while result is None:
            result = self._solve(problem)
        
        return {
            # must have
            "response_with_ans": result,
            "correct_ans": get_answer(problem["solution"]),
        }
    

    def _solve(self, problem):
        try:
            result = self.agent.run(
            remove_asy_sections(problem["problem"]) + "\n\n(When you write code, use 'print' function for the output)"
        )
        except:
            result = None
        
        return result
