
import os
import json
from flaml.autogen import oai
from flaml.autogen.math_utils import eval_math_responses, get_answer
import datasets
from agentchat import AgentChat
from langchain_react import ReAct



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

def solve_problems(problem_set, saving_folder, solver_function):
    """ Solve a set of problems
    Args:
        problem_set (list): a list of problems
        saving_folder (str): the result folder to save the solved problems, the category folder will be created inside
        solver_function (function): the solver function to solve one problem, take a problem dict as input and return a result dict

    Returns:
        None
    """
    logger = mylogger(os.path.join(saving_folder, "log.txt"))
    os.makedirs(saving_folder, exist_ok=True)

    # from the saving folder load solved problems
    done_problems = set([int(f.split(".")[0]) for f in os.listdir(saving_folder) if "json" in f])

    correct_counts = 0
    logger.log("id : is_correct $ correct_ans $", verbose=False)
    for i, problem in enumerate(problem_set):
        problem["problem_id"] = str(i)  # assign problem id
        problem_path = os.path.join(saving_folder, str(i) + ".json")

        if int(problem["problem_id"]) in done_problems:
            problem = json.load(open(problem_path, "r"))
            correct_counts += problem["is_correct"]

            logger.log(
                f'{problem["problem_id"]} : {bool(problem["is_correct"])} $ {problem["voted_answer"]} $ {problem["correct_ans"]} $ {problem["round"]} $ (from previous run)'
            )
            continue
    
        result = solver_function(problem)
        problem.update(result)
        write_json(problem, problem_path)

        correct_counts += problem["is_correct"]
        logger.log(
            f'{problem["problem_id"]} : {bool(problem["is_correct"])} $ {problem["correct_ans"]} $ {problem["voted_answer"]}  '
        )

    logger.log(f" Accuracy: {correct_counts}/{len(problem_set)} = {correct_counts/len(problem_set)}")
    logger.log("------------------------------------------------------------\n", verbose=True)

def load_level5_math_test(num_samples=100):
    data = datasets.load_dataset("competition_math")
    test_data = data["test"]
    level_5 = [
        test_data[x]
        for x in range(len(test_data))
        if test_data[x]["level"] == "Level 5"
    ]
    return level_5[:num_samples]



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
    samples = load_samples("./300problems/", num_samples=10)
    cate = samples.keys()

    agentchat = AgentChat(config_list=config_list)
    for i, category in enumerate(cate):
        solve_problems(samples[category], './agentchat_results/' + category, solver_function=agentchat.solve_one_problem)

    # samples = load_level5_math_test(num_samples=100)

    # agentchat = AgentChat(config_list=config_list)
    # solve_problems(samples, './results/agentchat', solver_function=agentchat.solve_one_problem)

    # react = ReAct(api_key=api_key)
    # solve_problems(samples, './results/react', solver_function=react.solve_one_problem)

    # os.system("tar -czf results.tar.gz ./results")
