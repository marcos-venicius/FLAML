import os
import json
from flaml.autogen import oai
from flaml.autogen.math_utils import eval_math_responses, get_answer
import time
from utils import load_samples, write_json, mylogger
from agentchat import AgentChat
from langchain_react import ReAct
from answer_checker import AnswerChecker
from functools import partial
from copy import deepcopy
import signal
import os
from multi_agent_debate.interactive import Debate
import json


import interpreter
interpreter.auto_run = True
interpreter.temperature = 1

def solve_problems(problem_set, saving_folder, solver_function, checker=None):
    """Solve a set of problems
    Args:
        problem_set (list): a list of problems
        saving_folder (str): the result folder to save the solved problems, the category folder will be created inside
        solver_function (function): the solver function to solve one problem, take a problem dict as input and return a result dict

    Returns:
        None
    """
    if len(problem_set) == 0:
        return
    os.makedirs(saving_folder, exist_ok=True)
    logger = mylogger(os.path.join(saving_folder, "log.txt"))

    stars = "*" * 80
    done_problems = set(
        [int(f.split(".")[0]) for f in os.listdir(saving_folder) if "json" in f]
    )  # from the saving folder load solved problems
    correct_counts = 0

    for i, problem in enumerate(problem_set):
        # update problem
        problem = {k: problem[k] for k in ["problem", "level", "type", "solution", "correct_ans"]}
        problem["problem_id"] = str(i)  # assign problem id

        # check if problem is already solved
        problem_path = os.path.join(saving_folder, str(i) + ".json")
        if int(problem["problem_id"]) in done_problems:
            saved_problem = json.load(open(problem_path, "r"))
            if saved_problem.get('trial') == -1:
                # if saved_problem.get('is_correct') is not None:
                #     correct_counts += saved_problem.get("is_correct", False)
                #     logger.log(
                #         f"{stars}\nProblem {i} (from previous run) | Is_correct {saved_problem.get('is_correct', 'N/A')} | Correct Answer: {saved_problem['correct_ans']}\n\nReply: {saved_problem['response_with_ans']}\n\nCheck: {saved_problem.get('check_result', '')}\n{stars}\n"
                #     )
                continue
            else:
                saved_problem["trial"] = -1
                write_json(saved_problem, problem_path)
                print(f"Tried to solve {problem['problem_id']} but failed. exit", flush=True)
                exit()
        # else:
        #     write_json({"trial": 1}, problem_path)

        # solve problem
        result = solver_function(problem)
        problem.update(result)

        # check answer
        if checker is not None:
            checker_result = checker.check_answer(problem["problem"], problem["response_with_ans"], problem["correct_ans"])
            problem.update(checker_result)
            correct_counts += problem["is_correct"]
            logger.log(
                f"{stars}\nProblem {i} | Is_correct {problem['is_correct']} | Correct Answer: {problem['correct_ans']}\n\nReply: {problem['response_with_ans']}\n%%%%%%%\nCheck: {problem['check_result']}\n{stars}\n"
            )
        else:
            logger.log(
                f"{stars}\nProblem {i} | Correct Answer: {problem['correct_ans']}\n\nReply: {problem['response_with_ans']}\n{stars}\n"
            )

        # save and print
        problem["trial"] = -1
        write_json(problem, problem_path)
        time.sleep(0.1)
        # exit()
        

    logger.log(f" Accuracy: {correct_counts}/{len(problem_set)} = {correct_counts/len(problem_set)}")
    logger.log("------------------------------------------------------------\n", verbose=True)


import datasets
def load_math_test(num_samples=1):
    data = datasets.load_dataset("competition_math")
    test_data = data["test"]
    test_data = [test_data[x] for x in range(len(test_data))]
    num_samples = len(test_data) if num_samples < 0 else num_samples
    # print(f"++++Length of test data: {len(test_data)}, num problem loaded: {num_samples}++++")
    assert "How many vertical asymptotes does" in test_data[0]["problem"]
    assert "What is the positive difference between $120\\%$" in test_data[1]["problem"]
    if num_samples > 0:
        return test_data[:num_samples]
    return test_data

def solve_problem_with_multiple_solvers(problem, solvers_with_paths, checker=None):
    """Solve a single problem using multiple solvers and save the results
    Args:
        problem (dict): a problem in dictionary format
        solvers (list): a list of solver functions
        paths (list): a list of saving folders corresponding to solvers
        checker (function, optional): a function to check the correctness of the solution

    Returns:
        None
    """
    stars = "*" * 80
    # Iterate through all solvers and corresponding paths
    start = time.time()
    for solver, path, name in solvers_with_paths:
        
        # Make directory if not exists
        os.makedirs(path, exist_ok=True)
        
        # Initialize logger (assuming mylogger function is defined in your code)
        logger = mylogger(os.path.join(path, "log.txt"))
        
        # Check if problem is already solved
        problem_path = os.path.join(path, f"{problem['problem_id']}.json")
        if os.path.exists(problem_path):
            solved_problem = json.load(open(problem_path, "r"))
            if solved_problem['trial'] == -1:
                # if solved_problem.get('is_correct') is not None:
                #     logger.log(
                #         f"{stars}\nSolver: {name} | Problem {solved_problem['problem_id']} (from previous run) | Is_correct {solved_problem.get('is_correct', 'N/A')} | Correct Answer: {solved_problem['correct_ans']}\n\nReply: {solved_problem['response_with_ans']}\n\nCheck: {solved_problem.get('check_result', '')}\n{stars}\n"
                #     )
                continue
            else:
                solved_problem["trial"] = -1
                write_json(solved_problem, problem_path)
                print(f"Tried to solve {problem['problem_id']} before, Skip for now.", flush=True)
                continue
        # else:
        #     write_json({"trial": 1}, problem_path)

        print(f"Start solving problem {problem['problem_id']} with {name}", flush=True)
        # Solve the problem using the solver
        result = solver(problem)
        
        # Update problem with the result
        tmp_problem = deepcopy(problem)
        tmp_problem.update(result)
        
        # Check the answer if checker is available
        if checker is not None:
            print(f"Start checking problem {tmp_problem['problem_id']} solved with {name}", flush=True)
            checker_result = checker.check_answer(
                tmp_problem["problem"], tmp_problem["response_with_ans"], tmp_problem["correct_ans"]
            )
            tmp_problem.update(checker_result)
            
            logger.log(
                f"{stars}\nSolver: {name} | Problem {tmp_problem['problem_id']} | Is_correct {tmp_problem['is_correct']} | Correct Answer: {tmp_problem['correct_ans']}\n\nReply: {tmp_problem['response_with_ans']}\n%%%%%%%\nCheck: {tmp_problem['check_result']}\n{stars}\n"
            )
        else:
            logger.log(
                f"{stars}\nSolver: {name} | Problem {tmp_problem['problem_id']} | Correct Answer: {tmp_problem['correct_ans']}\n\nReply: {tmp_problem['response_with_ans']}\n{stars}\n"
            )
        
        # Save the problem
        tmp_problem["trial"] = -1
        write_json(tmp_problem, problem_path)
        # exit()

def solve_with_verifier(problem, solver_function, verifier_function):
    result = solver_function(problem)

    verify_result = verifier_function(problem["problem"], result["response_with_ans"])

    re_solve_count = 3
    re_check_count = 1
    while (
        (verify_result["state"] == "no_answer" or verify_result["state"] == "wrong")
        and re_solve_count > 0
        and re_check_count > 0
    ):
        if verify_result["state"] == "no_answer":
            verify_result = verifier_function(problem["problem"], result["response_with_ans"])
            re_check_count -= 1
            continue

        result = solver_function(problem)
        verify_result = verifier_function(problem["problem"], result["response_with_ans"])
        re_solve_count -= 1


def vanilla_solver(config_list, problem):
    
    llm_config = {
        "model" : "gpt-4",
        "config_list": config_list,
        "seed": 42,
        "request_timeout": 600,
    }
    messages =  [{"content": 'You are a helpful AI Assistant.', "role": "system"},
                 {"content": problem["problem"], "role": "user"}]
    
    def timeout_handler(signum, frame):
        raise Exception("Vanilla GPT-4 Timeout")

    start = time.time()
    signal.signal(signal.SIGALRM, timeout_handler)
    try:
        signal.alarm(800)
        responses = oai.ChatCompletion.create(
                context=messages[-1].pop("context", None), messages=messages, **llm_config
            )
        signal.alarm(0)
    except Exception as e:
        print(f"Got exception {e} when solving problem {problem['problem_id']}", flush=True)
        return {
            "response_with_ans": "Got exception when solving problem",
            "correct_ans": get_answer(problem["solution"]),
            "time": time.time() - start,
        }

    return {
        "response_with_ans": responses["choices"][0]["message"]['content'],
        "correct_ans": get_answer(problem["solution"]),
        "time": time.time() - start,
    }

def contains_asy_code(input_string):
    # patterns = ["\[asy\]", "\[ASY\]"]
    # for p in patterns:
    #     if p in input_string:
    #         return True
    if "[asy" in input_string or "[ASY" in input_string:
        return True
    return False


def open_code_interpreter(problem):
    def timeout_handler(signum, frame):
        raise Exception("Open Interpreter Timeout")

    interpreter.reset()
    start = time.time()
    signal.signal(signal.SIGALRM, timeout_handler)
    try: 
        signal.alarm(800)
        messages = interpreter.chat(problem["problem"], return_messages=True)
        signal.alarm(0)
    except Exception as e:
        print(f"Got exception {e} when solving problem {problem['problem_id']}", flush=True)
        return {
            "response_with_ans": "Got exception when solving problem",
            "correct_ans": get_answer(problem["solution"]),
            "time": time.time() - start,
        }

    return {
        "response_with_ans": messages[-1]["content"],
        "correct_ans": get_answer(problem["solution"]),
        "messages": messages,
        "time": time.time() - start,
    }

def multidebate(config_list, problem):
    def timeout_handler(signum, frame):
        raise Exception("multidebate Timeout")

    config = json.load(open(f"multi_agent_debate/code/utils/config4all.json", "r"))
    config['debate_topic'] = problem['problem']
    debate = Debate(num_players=3, config_list=config_list, config=config, temperature=1, sleep_time=0, model_name='gpt-4', max_round=15)
    start = time.time()
    signal.signal(signal.SIGALRM, timeout_handler)
    try:
        signal.alarm(800)
        debate.run()
        result = {
            "response_with_ans": debate.config['debate_answer'],
            "correct_ans": get_answer(problem["solution"]),
            "time": time.time() - start,
            "prompt_tokens": debate.prompt_tokens,
            "completion_tokens": debate.completion_tokens,
        }
        signal.alarm(0)
    except Exception as e:
        print(f"Got exception {e} when solving problem {problem['problem_id']}", flush=True)
        result = {
            "response_with_ans": "Got exception when solving problem",
            "correct_ans": get_answer(problem["solution"]),
            "time": time.time() - start,
        }

    result.update(debate.config)
    del result['debate_topic']
    return result

def pseudo_main(config_list, use_azure):
    if use_azure:
        print("Using Azure", flush=True)
        interpreter.use_azure = True
        interpreter.api_key = config_list[0]['api_key']
        interpreter.azure_api_base = config_list[0]['api_base']
        interpreter.azure_api_version = config_list[0]['api_version']
        interpreter.azure_deployment_name = config_list[0]['model']
        interpreter.azure_api_type = "azure"

        os.environ['AZURE_API_KEY'] = config_list[0]['api_key']
        os.environ['AZURE_API_BASE'] = config_list[0]['api_base']
        os.environ['AZURE_API_VERSION'] = config_list[0]['api_version']
        os.environ['AZURE_DEPLOYMENT_NAME'] = config_list[0]['model']

        assert interpreter.azure_api_base is not None, "azure_api_base is None"
        assert interpreter.azure_api_version is not None, "azure_api_version is None"
        assert interpreter.azure_deployment_name is not None, "azure_deployment_name is None"
        assert interpreter.azure_api_type is not None,  "azure_api_type is None"
    else:
        interpreter.api_key = config_list[0]['api_key']
    # samples = load_samples("./300problems/", num_samples=20)
    # cate = samples.keys()
    # checker = AnswerChecker(config_list=config_list)

    # samples = {
    #         "algebra" : [samples["algebra"][8]],
    #         "number_theory": [],
    #         "counting_and_probability": [samples["counting_and_probability"][13]],
    #         "prealgebra": [samples["prealgebra"][0], samples["prealgebra"][7], samples["prealgebra"][16]],
    #         "intermediate_algebra": [samples["intermediate_algebra"][5], samples["intermediate_algebra"][15]],
    #         "precalculus": [samples["precalculus"][5], samples["precalculus"][14]],
    # }

    # # ---------------------------------------------------------------
    # # 0. run vanilla agentchat
    # agentchat = AgentChat(
    #     config_list=config_list, 
    #     system_message="You are a helpful AI Assistant. Reply \"TERMINATE\" in the end when everything is done."
    # )
    # for i, category in enumerate(cate):
    #     solve_problems(
    #         samples[category],
    #         f"./asy/vanilla_agentchat/" + category,
    #         solver_function=agentchat.solve_one_problem,
    #         checker=checker,
    #     )

    # # ---------------------------------------------------------------
    # # 1. run vanilla solver
    # vanilla_solver_function = partial(vanilla_solver, config_list)
    # for i, category in enumerate(cate):
    #     solve_problems(
    #         samples[category],
    #         f"./asy/vanilla_solver/" + category,
    #         solver_function=vanilla_solver_function,
    #         checker=checker,
    #     )

    # # ---------------------------------------------------------------
    # # 2. run agentchat v2.0.2 prompt
    # import flaml
    # print(flaml.__version__, flush=True)
    # # check flaml version
    # if flaml.__version__ != "2.0.2":
    #     exit()
    # # run agentchat
    # agentchat = AgentChat(config_list=config_list)
    # for i, category in enumerate(cate):
    #     solve_problems(
    #         samples[category],
    #         f"./asy/agentchat_{flaml.__version__}/" + category,
    #         solver_function=agentchat.solve_one_problem,
    #         checker=checker,
    #     )

    # # ---------------------------------------------------------------
    # # 3. run agentchat v2.0.0 prompt
    # old_system_message = """You are a helpful AI assistant.
    # In the following cases, suggest python code (in a python coding block) or shell script (in a sh coding block) for the user to execute. You must indicate the script type in the code block. The user cannot provide any other feedback or perform any other action beyond executing the code you suggest. The user can't modify your code. So do not suggest incomplete code which requires users to modify. Don't use a code block if it's not intended to be executed by the user.
    # 1. When you need to collect info, use the code to output the info you need, for example, browse or search the web, download/read a file, print the content of a webpage or a file, get the current date/time.
    # 2. When you need to perform some task with code, use the code to perform the task and output the result. Finish the task smartly. Solve the task step by step if you need to.
    # If you want the user to save the code in a file before executing it, put # filename: <filename> inside the code block as the first line. Don't include multiple code blocks in one response. Do not ask users to copy and paste the result. Instead, use 'print' function for the output when relevant. Check the execution result returned by the user.
    # If the result indicates there is an error, fix the error and output the code again. Suggest the full code instead of partial code or code changes. If the error can't be fixed or if the task is not solved even after the code is executed successfully, analyze the problem, revisit your assumption, collect additional info you need, and think of a different approach to try.
    # When you find an answer, verify the answer carefully. If a function for planning is provided, call the function to make plans and verify the execution.
    # Reply "TERMINATE" in the end when everything is done."""

    # agentchat = AgentChat(config_list=config_list, system_message=old_system_message)
    # for i, category in enumerate(cate):
    #     solve_problems(
    #         samples[category],
    #         f"./asy/agentchat_2.0.0/" + category,
    #         solver_function=agentchat.solve_one_problem,
    #         checker=checker,
    #     )

    # # # ---------------------------------------------------------------
    # # 4. run react
    # react = ReAct(config_list, use_azure)
    # print("Running ReAct on 120 problems with asy removed", flush=True)
    # for i, category in enumerate(cate):
    #     solve_problems(
    #         samples[category], 
    #         "./asy/asy_react_120/" + category, 
    #         solver_function=react.solve_one_problem, 
    #         checker=checker
    #     )
    # print("tar 120 problems", flush=True)
    # os.system("tar -czf all_problems.tar.gz all_problems full_run.out")

    # # ---------------------------------------------------------------
    # # 5. run open code interpreter
    # samples = load_samples("./300problems/", num_samples=20)
    # cate = samples.keys()
    # checker = AnswerChecker(config_list=config_list)

    # print("Running open code interpreter on 120 problems", flush=True)
    # for i, category in enumerate(cate):
    #     solve_problems(
    #         samples[category], 
    #         "./interpreter_results/code_interpreter_120_temp_1/" + category, 
    #         solver_function=open_code_interpreter, 
    #         checker=checker
    #     )
    # print("tar 120 problems", flush=True)
    # os.system("tar -czf interpreter.tar.gz interpreter_results full_run.out")



    # ---------------------------------------------------------------
    # 6. run multi-agent debate
    samples = load_samples("./300problems/", num_samples=20)
    cate = samples.keys()
    checker = AnswerChecker(config_list=config_list)

    print("Running Multi-Agent Debate on 120 problems", flush=True)
    for i, category in enumerate(cate):
        solve_problems(
            samples[category], 
            "./results/debate/" + category, 
            solver_function=partial(multidebate, config_list), 
            checker=checker
        )
    print("tar 120 problems", flush=True)
    os.system("tar -czf results.tar.gz results full_run.out")

    # ---------------------------------------------------------------
    # 7. run groupchat
    samples = load_samples("./300problems/", num_samples=20)
    cate = samples.keys()
    from groupchat_v1 import GroupChatMath
    groupsolver = GroupChatMath(config_list=config_list)

    print("Running GroupChat on 120 problems", flush=True)
    for i, category in enumerate(cate):
        solve_problems(
            samples[category], 
            "./results/groupchatv1/" + category, 
            solver_function=groupsolver.solve_one_problem, 
            checker=checker
        )
    print("tar 120 problems", flush=True)
    os.system("tar -czf results.tar.gz results full_run.out")

    # ---------------------------------------------------------------
    # ---------------------------------------------------------------
    # ---------------------------------------------------------------
    # ---------------- whole test set -------------------------------

    # solvers_with_paths = [
    #     # (open_code_interpreter, "./interpreter_results/interpreter_temp1/", "interpreter"),
    #     # (partial(vanilla_solver, config_list), "./all_problems/vanilla_gpt4/", "gpt4"),
    # ]

    # problems = load_math_test(num_samples=-1)
    # print(f"Start running {len(problems)} on interpreter", flush=True)

    # for i, problem in enumerate(problems):
    #     problem['problem_id'] = str(i)
    #     solve_problem_with_multiple_solvers(problem, solvers_with_paths, checker=checker)

    #     # tar every 200 problems
    #     if i > 0 and i % 200 == 0:
    #         print(f"tar {i} problems", flush=True)
    #         os.system("tar -czf interpreter.tar.gz interpreter_results full_run.out")
    
    # os.system("tar -czf interpreter.tar.gz interpreter_results full_run.out")


    # special case for asy
    # agentchat = AgentChat(config_list=config_list)
    # checker = AnswerChecker(config_list=config_list)

    # solvers_with_paths = [
    #     (agentchat.solve_one_problem, "./all_problems/agentchat_asy/", "agentchatv2.0.2_asy"),
    # ]

    # problems = load_math_test(num_samples=-1)
    # problems = [p for p in problems if contains_asy_code(p["problem"])]
    # assert len(problems) == 419
    # print(f"Start running {len(problems)} asy problems on agenchat", flush=True)

    # for i, problem in enumerate(problems):
    #     problem['problem_id'] = str(i)
    #     solve_problem_with_multiple_solvers(problem, solvers_with_paths, checker=checker)

    #     # tar every 100 problems
    #     if i > 0 and i % 100 == 0:
    #         print(f"tar {i} problems", flush=True)
    #         os.system("tar -czf all_problems.tar.gz all_problems full_run.out")
    
    # os.system("tar -czf all_problems.tar.gz all_problems full_run.out")

