try:
    import openai
except ImportError:
    openai = None
import pytest
# from flaml import oai
# from flaml.autogen.agent import LearningAgent, TeachingAgent
# import asyncio

KEY_LOC = "test/autogen/"

import json
from flaml import autogen

def test_group(problem_id, problem):    
    from flaml.autogen import AssistantAgent, UserProxyAgent
    autogen.ChatCompletion.start_logging()
    config_list = autogen.config_list_from_models(key_file_path=KEY_LOC, model_list=["gpt-3.5-turbo"], exclude="aoai")
    # config_list = autogen.config_list_from_models(key_file_path=KEY_LOC, model_list=["gpt-4"], exclude="aoai")
    # create an AssistantAgent instance named "assistant"
    assistant = AssistantAgent(
        name="assistant",
        llm_config={
            "request_timeout": 600,
            "seed": 42,
            "config_list": config_list,
            "temperature": 0,
        }
    )
    # create a UserProxyAgent instance named "user"
    user = UserProxyAgent(
        name="user",
        human_input_mode="TERMINATE",
        max_consecutive_auto_reply=10,
        # is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
        code_execution_config={"last_n_messages": 3, "work_dir": "group_twoagent_docker"},
    )

    user.initiate_chat(
    assistant,
    message=problem,
    )
    log = autogen.ChatCompletion.logged_history
    print(type(log), log)
    file_path = "test/autogen/log/twoagent-" +str(problem_id) +".json"
    with open(file_path, 'w') as file:
        json.dump(log, file)
if __name__ == "__main__":
    final_problem = "Write a script to download AutoGen paper from arxiv as pdf and extract its abstract. The link to pdf is https://arxiv.org/pdf/2308.08155.pdf"
    id_ = 7
    test_group(id_, final_problem)