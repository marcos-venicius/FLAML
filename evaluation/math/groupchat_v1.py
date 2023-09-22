from flaml.autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
import flaml
from flaml.autogen.code_utils import UNKNOWN, extract_code, execute_code, infer_lang
from flaml.autogen.math_utils import eval_math_responses, get_answer
from utils import remove_asy_sections
from openai import InvalidRequestError
import time

import signal

def timeout_handler(signum, frame):
    raise Exception("AgentChat Timeout. Need restart.")

class GroupChatMath:
    def __init__(self, config_list, system_message=None, seed=42, max_consecutive_auto_reply=15, use_cache=True):
        """Initialize AgentChat

        Args:
            seed (int): random seed.
            config_list (list): list of config dicts.
            max_consecutive_auto_reply (int): maximum number of consecutive auto replies.
        """
        llm_config={
            "config_list": config_list,
            "request_timeout": 600,
        }
        if not use_cache:
            llm_config["use_cache"] = use_cache
        else:
            llm_config['seed'] = seed

        print(f"Seed = {seed}", flush=True)
        print(f"Version = {flaml.__version__}", flush=True)

        # create the UserProxyAgent instance named "user"
        self.user = UserProxyAgent(
            name="user",
            human_input_mode="NEVER",
            is_termination_msg=lambda x: x.get("content", "")
            and (
                x.get("content", "").rstrip().endswith("TERMINATE")
                or x.get("content", "").rstrip().endswith("TERMINATE.")
            ),
            code_execution_config={
                "work_dir": "coding",
                "use_docker": False,  # set to True or image name like "python:3" to use docker
            },
            max_consecutive_auto_reply=max_consecutive_auto_reply,
        )

        self.user_proxy = UserProxyAgent(
            name="User_proxy",
            system_message="A human admin.",
            code_execution_config={"last_n_messages": 3, "work_dir": "groupchat", "use_docker": False},
            human_input_mode="NEVER",
            is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE") or x.get("content", "").rstrip().endswith("TERMINATE.")
        )
        self.coder = AssistantAgent(
            name="Coder",  # the default assistant agent is capable of solving problems with code
            llm_config=llm_config,
        )
        self.critic = AssistantAgent(
            name="Critic",
            system_message="""Critic. You are a helpful assistant highly skilled in math problems and coding. You will examine the solving process carefully from the following dimensions:
        - bugs: are there bugs, logic errors, syntax error or typos in the code? Are there any reasons why the code may fail to compile? How should it be fixed?
        - logics: Any logical errors in the reasoning process? How should it be fixed?

        Do not suggest code. 
        Finally, based on the critique above, suggest a concrete list of actions that the coder should take to improve the code.
        """,
            llm_config=llm_config,
            is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE") or x.get("content", "").rstrip().endswith("TERMINATE.")
        )

        self.groupchat = GroupChat(agents=[self.user_proxy, self.coder, self.critic], messages=[], max_round=20)
        self.manager = GroupChatManager(groupchat=self.groupchat, llm_config=llm_config)


    def solve_one_problem(self, problem):
        """Solve one problem.

        Args:
            problem (dict): a problem dict. Use problem["problem"] to extract the problem text.
        """
        # reset
        self.coder.reset()
        self.user.reset()
        self.critic.reset()
        self.groupchat.reset()
        self.manager.reset()

        # solve
        start = time.time()
        signal.signal(signal.SIGALRM, timeout_handler)
        try:
            signal.alarm(800)
            self.user.initiate_chat(self.manager, message=problem["problem"])
            signal.alarm(0)
        except Exception as e:
            print(f"Got error: {e}, take it as wrong", flush=True)
        total_time = time.time() - start

        print("**********************************************", flush=True)
        print("**********************************************\n\n", flush=True)

        # extract reply
        response_with_ans = self.groupchat.messages[-1]["content"]
        messages =  self.groupchat.messages
        for j in range(len(messages) - 1, -1, -1):
            if (
                messages[j]["role"] == "assistant"
                and messages[j]["content"].strip() != ""
                and messages[j]["content"].strip() != "TERMINATE"
                and messages[j]["content"].strip() != "TERMINATE."
            ):
                response_with_ans = messages[j]["content"]
                break

        return {
            # must have
            "response_with_ans": response_with_ans,
            "correct_ans": get_answer(problem["solution"]),
            
            "round": (len(self.groupchat.messages) - 1) // 2,
            "messages": self.groupchat.messages,
            "time" : total_time
        }
