from flaml.autogen import AssistantAgent, UserProxyAgent

from flaml.autogen.code_utils import UNKNOWN, extract_code, execute_code, infer_lang
from flaml.autogen.math_utils import eval_math_responses, get_answer


def is_termination_msg(message):
    """Check if a message is a termination message."""
    if isinstance(message, dict):
        message = message.get("content")
        if message is None:
            return False
    cb = extract_code(message)
    contain_code = False
    for c in cb:
        if c[0] == "python" or c[0] == "wolfram":
            contain_code = True
            break
    return not contain_code and get_answer(message) is not None and get_answer(message) != ""

class AgentChat:
    def __init__(self, config_list, seed=42, max_consecutive_auto_reply=15):
        """Initialize AgentChat

        Args:
            seed (int): random seed.
            config_list (list): list of config dicts.
            max_consecutive_auto_reply (int): maximum number of consecutive auto replies.
        """

        system_message =  """You are a helpful AI assistant.
Solve tasks using your coding and language skills.
If a plan is not provided, explain the plan first. Be clear which step uses code, and which step uses your language skill.
In the following cases, suggest python code (in a python coding block) or shell script (in a sh coding block) for the user to execute.
1. When you need to collect info, use the code to output the info you need, for example, browse or search the web, download/read a file, print the content of a webpage or a file, get the current date/time. After sufficient info is printed and the task is ready to be solved based on your language skill, you can solve the task by yourself.
2. When you need to perform some task with code, use the code to perform the task and output the result. Finish the task smartly. Solve the task step by step if you need to.
You must indicate the script type in the code block. The user cannot provide any other feedback or perform any other action beyond executing the code you suggest. The user can't modify your code. So do not suggest incomplete code which requires users to modify. Don't use a code block if it's not intended to be executed by the user.
If you want the user to save the code in a file before executing it, put # filename: <filename> inside the code block as the first line. Don't include multiple code blocks in one response. Do not ask users to copy and paste the result. Instead, use 'print' function for the output when relevant. Check the execution result returned by the user.
If the result indicates there is an error, fix the error and output the code again. Suggest the full code instead of partial code or code changes. If the error can't be fixed or if the task is not solved even after the code is executed successfully, analyze the problem, revisit your assumption, collect additional info you need, and think of a different approach to try.
When you find an answer, verify the answer carefully. If a function for planning is provided, call the function to make plans and verify the execution.
Put the final answer in \\boxed{} in the end when everything is done.
"""
        # create an AssistantAgent instance named "assistant"
        self.assistant = AssistantAgent(
            name="assistant",
            llm_config={
                "seed": seed,
                "config_list": config_list,
                "request_timeout": 600,
            },
            system_message=system_message,
        )

        # create the UserProxyAgent instance named "user"
        self.user = UserProxyAgent(
            name="user",
            human_input_mode="NEVER",
            is_termination_msg=is_termination_msg,
            max_consecutive_auto_reply=max_consecutive_auto_reply,
            code_execution_config={
                "work_dir": "coding",
                "use_docker": False,  # set to True or image name like "python:3" to use docker
            },
    )
        
    def solve_one_problem(self, problem):
        """Solve one problem.

        Args:
            problem (dict): a problem dict. Use problem["problem"] to extract the problem text.
        """
        # reset
        self.assistant.reset()

        # solve
        self.user.initiate_chat(self.assistant, message=problem["problem"])
        response_with_ans = self.assistant._oai_messages[self.user][-1]["content"]

        is_valid_reply = False
        try:
            if is_termination_msg(response_with_ans):
                is_valid_reply = True
        except Exception:
            pass


        metrics = eval_math_responses([response_with_ans], problem["solution"])
        correct_ans = get_answer(problem["solution"])
        print("**********************************************", flush=True)
        print("**********************************************", flush=True)
        print("**********************************************", flush=True)
        
        return {
            # must have 
            "response_with_ans": response_with_ans,
            "correct_ans": correct_ans,
            "voted_answer": get_answer(metrics["voted_answer"]),  
            "is_correct": bool(metrics["success_vote"]),
                
            "is_valid_reply": is_valid_reply,
            
            "round": (len(self.assistant._oai_messages[self.user]) - 1) // 2,
            "messages": self.assistant._oai_messages[self.user],
        }
