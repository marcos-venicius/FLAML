import os
import json
from flaml.autogen import oai
from flaml.autogen.math_utils import eval_math_responses, get_answer
import datasets

from utils import load_samples, write_json, mylogger
from agentchat import AgentChat
from langchain_react import ReAct
from answer_checker import AnswerChecker


def solve_problems(problem_set, saving_folder, solver_function, checker):
    """Solve a set of problems
    Args:
        problem_set (list): a list of problems
        saving_folder (str): the result folder to save the solved problems, the category folder will be created inside
        solver_function (function): the solver function to solve one problem, take a problem dict as input and return a result dict

    Returns:
        None
    """
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
            problem = json.load(open(problem_path, "r"))
            correct_counts += problem["is_correct"]

            logger.log(
                f"{stars}\nProblem {i} (from previous run) | Is_correct {problem['is_correct']} | Correct Answer: {problem['correct_ans']}\n\nReply: {problem['response_with_ans']}\n\nCheck: {problem['check_result']}\n{stars}\n"
            )
            continue

        # solve problem
        result = solver_function(problem)
        problem.update(result)

        # check answer
        checker_result = checker.check_answer(problem["problem"], problem["response_with_ans"], problem["correct_ans"])
        problem.update(checker_result)

        # save and print
        write_json(problem, problem_path)
        correct_counts += problem["is_correct"]
        logger.log(
            f"{stars}\nProblem {i} | Is_correct {problem['is_correct']} | Correct Answer: {problem['correct_ans']}\n\nReply: {problem['response_with_ans']}\n%%%%%%%\nCheck: {problem['check_result']}\n{stars}\n"
        )

    logger.log(f" Accuracy: {correct_counts}/{len(problem_set)} = {correct_counts/len(problem_set)}")
    logger.log("------------------------------------------------------------\n", verbose=True)


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


def pseudo_main(config_list, api_key):
    samples = load_samples("./300problems/", num_samples=1)
    cate = samples.keys()
    checker = AnswerChecker(config_list=config_list)

    import flaml
    print(flaml.__version__, flush=True)
    # check flaml version
    if flaml.__version__ != "2.0.2":
        exit()
    # run agentchat
    agentchat = AgentChat(config_list=config_list)
    for i, category in enumerate(cate):
        solve_problems(
            samples[category],
            f"./results/agentchat_{flaml.__version__}/" + category,
            solver_function=agentchat.solve_one_problem,
            checker=checker,
        )
        break

    # run agentchat v2.0.0 prompt
    old_system_message = """You are a helpful AI assistant.
    In the following cases, suggest python code (in a python coding block) or shell script (in a sh coding block) for the user to execute. You must indicate the script type in the code block. The user cannot provide any other feedback or perform any other action beyond executing the code you suggest. The user can't modify your code. So do not suggest incomplete code which requires users to modify. Don't use a code block if it's not intended to be executed by the user.
    1. When you need to collect info, use the code to output the info you need, for example, browse or search the web, download/read a file, print the content of a webpage or a file, get the current date/time.
    2. When you need to perform some task with code, use the code to perform the task and output the result. Finish the task smartly. Solve the task step by step if you need to.
    If you want the user to save the code in a file before executing it, put # filename: <filename> inside the code block as the first line. Don't include multiple code blocks in one response. Do not ask users to copy and paste the result. Instead, use 'print' function for the output when relevant. Check the execution result returned by the user.
    If the result indicates there is an error, fix the error and output the code again. Suggest the full code instead of partial code or code changes. If the error can't be fixed or if the task is not solved even after the code is executed successfully, analyze the problem, revisit your assumption, collect additional info you need, and think of a different approach to try.
    When you find an answer, verify the answer carefully. If a function for planning is provided, call the function to make plans and verify the execution.
    Reply "TERMINATE" in the end when everything is done."""

    agentchat = AgentChat(config_list=config_list, system_message=old_system_message)
    for i, category in enumerate(cate):
        solve_problems(
            samples[category],
            f"./results/agentchat_2.0.0/" + category,
            solver_function=agentchat.solve_one_problem,
            checker=checker,
        )
        break

    # run react
    react = ReAct(api_key=api_key)
    for i, category in enumerate(cate):
        solve_problems(
            samples[category], "./results/react/" + category, solver_function=react.solve_one_problem, checker=checker
        )
        break

    # samples = load_level5_math_test(num_samples=100)

    # agentchat = AgentChat(config_list=config_list)
    # solve_problems(samples, './results/agentchat', solver_function=agentchat.solve_one_problem)

    # react = ReAct(api_key=api_key)
    # solve_problems(samples, './results/react', solver_function=react.solve_one_problem)

    # os.system("tar -czf results.tar.gz ./results")


# def load_level5_math_test(num_samples=100):
#     data = datasets.load_dataset("competition_math")
#     test_data = data["test"]
#     level_5 = [
#         test_data[x]
#         for x in range(len(test_data))
#         if test_data[x]["level"] == "Level 5"
#     ]
#     return level_5[:num_samples]
