
import os
import json
from flaml.autogen import oai
from flaml.autogen.math_utils import eval_math_responses, get_answer
import datasets

from agentchat import AgentChat
from langchain_react import ReAct
from answer_checker import AnswerChecker

def write_json(dict_to_save, file):
    """Write a dictionary to a json file.
    Args:

        dict_to_save (dict): The dictionary to save.
        file (str): The file to save to.
    """
    jstring = json.dumps(dict_to_save, indent=2)
    with open(file, "w") as j:
        j.write(jstring)

class mylogger:
    def __init__(self, file) -> None:
        self.file = file

    def log(self, message, verbose=True):
        """Print the message.
        Args:
            message (str): The message to print.
        """
        with open(self.file, "a") as f:
            f.write(message + "\n")
        if verbose:
            print(message, flush=True)

def solve_problems(problem_set, saving_folder, solver_function, checker):
    """ Solve a set of problems
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
    done_problems = set([int(f.split(".")[0]) for f in os.listdir(saving_folder) if "json" in f]) # from the saving folder load solved problems
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


def load_samples(base_dir, num_samples=10):
    # List of directories to search for .json files
    folders = ["algebra", "number_theory", "counting_and_probability",
               "prealgebra", "intermediate_algebra", "precalculus"]

    samples = {}

    for folder in folders:
        folder_path = os.path.join(base_dir, folder)
        
        # Check if directory exists
        if not os.path.isdir(folder_path):
            print(f"Warning: {folder_path} not found!")
            continue

        # Load each .json file up to num_samples
        for i in range(num_samples):
            file_path = os.path.join(folder_path, f"{i}.json")

            # Check if file exists
            if not os.path.exists(file_path):
                print(f"Warning: {file_path} not found!")
                continue

            with open(file_path, 'r') as file:
                data = json.load(file)

            # Append to the dictionary with a folder-wise key
            if folder not in samples:
                samples[folder] = []
            samples[folder].append(data)

    return samples


def pseudo_main(config_list, api_key):
    samples = load_samples("./300problems/", num_samples=20)
    cate = samples.keys()
    checker = AnswerChecker(config_list=config_list)

    # run agentchat
    agentchat = AgentChat(config_list=config_list)
    for i, category in enumerate(cate):
        solve_problems(samples[category], './results/agentchat_v2.0.2/' + category, solver_function=agentchat.solve_one_problem, checker=checker)


    # run react
    react = ReAct(api_key=api_key)
    for i, category in enumerate(cate):
        solve_problems(samples[category], './results/react/' + category, solver_function=react.solve_one_problem, checker=checker)
    
    
    
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