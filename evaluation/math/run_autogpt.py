import subprocess
from time import sleep
import psutil
import re
import os

from pseudo_main import load_samples
from utils import remove_asy_sections


def extract_command_and_args(s):
    # Match command and arguments from the input string
    command_match = re.search(r"COMMAND =\s+(.*?)\s+ARGUMENTS", s)
    args_match = re.search(r"ARGUMENTS =\s+({.*?})", s)

    # Extract command and arguments
    command = command_match.group(1) if command_match else None
    arguments = args_match.group(1) if args_match else None

    return command, arguments


def run_script_with_auto_input(problem, problem_path):
    problem = remove_asy_sections(problem)
    # Command to run
    command = "docker compose -f Auto-GPT/docker-compose.yml run --rm auto-gpt --skip-news"

    # Starting the process
    process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        bufsize=1,
        shell=True,
    )

    def send_input(input, allow_input):
        if not allow_input:
            return True
        print(f"*************{input}*************")
        process.stdin.write(input + "\n")
        process.stdin.flush()
        return False

    # Iterate over the process's output
    count = 0
    command = None
    allow_input = True

    for line in iter(process.stdout.readline, ""):
        if "Thinking..." in line.strip() or line.strip() == "":
            continue
        if allow_input:
            print(line, end="")  # Display real-time output
            with open(problem_path, "a") as f:
                f.write(line)

        if "NEXT ACTION:" in line:
            command, _ = extract_command_and_args(line)
            print(command)

        # Check for the continue prompt and provide the input if not sent recently
        if "Continue (y/n):" in line:
            allow_input = send_input("y", allow_input)

        elif "I want Auto-GPT to:" in line:
            allow_input = send_input("solve math problems", allow_input)

        elif "MathSolverGPT asks: " in line:
            allow_input = send_input(f"{problem} (When you write code, always print the result.)", allow_input)

        elif "Input:" in line:
            if command is None or command == "None" or command == "none":
                allow_input = send_input(f"{problem} ≈", allow_input)
                continue

            allow_input = send_input("y", allow_input)
            count += 1
            if count > 15:
                break


def solve_problems(problem_set, saving_folder):
    os.makedirs(saving_folder, exist_ok=True)
    done_problems = set(
        [int(f.split(".")[0]) for f in os.listdir(saving_folder) if "txt" in f]
    )  # from the saving folder load solved problems

    for i, problem in enumerate(problem_set):
        # update problem
        problem = {k: problem[k] for k in ["problem", "level", "type", "solution", "correct_ans"]}
        problem["problem_id"] = str(i)  # assign problem id

        # check if problem is already solved
        problem_path = os.path.join(saving_folder, str(i) + ".txt")
        if int(problem["problem_id"]) in done_problems:
            continue

        run_script_with_auto_input(problem["problem"], problem_path)

        # append to file
        with open(problem_path, "a") as f:
            f.write("***********************\n\n")
            f.write(f"Problem: {problem['problem']}\n\n")
            f.write(f"Correct Answer: {problem['correct_ans']}\n\n")
            f.write("***********************\n\n")
        exit()


if __name__ == "__main__":
    samples = load_samples("./300problems/", num_samples=20)
    cate = samples.keys()
    for i, category in enumerate(cate):
        solve_problems(samples[category], f"./results/autogpt/{category}/")

# import pexpect
# def run_script(problem="Evaluate $i^5+i^{-25}+i^{45}$."):
#     import pexpect

#     child = pexpect.spawn('docker compose run --rm auto-gpt --skip-news')
#     child.expect('I want Auto-GPT to:')
#     child.sendline('solve math problems')
#     child.expect('MathSolverGPT asks:')
#     child.sendline(f'{problem} (When you write code, always print the result.)')
#     child.expect('Input:')
#     child.sendline('y')


# import pexpect
# import sys
# def run_script_with_auto_input(problem="Evaluate $i^5+i^{-25}+i^{45}$."):
#     # Command to run
#     command = "docker compose run --rm auto-gpt --skip-news"

#     # Start the process
#     child = pexpect.spawn(command)
#     child.logfile = sys.stdout.buffer
#     count = 0
#     command, arguments = None, None
#     last_input = None
#     input_sent = False  # Flag to check if "y" has been sent recently

#     while True:
#         try:
#             idx = child.expect(['.*Thinking....*', '.*NEXT ACTION:.*', '.*Continue \(y/n\):.*', '.*I want Auto-GPT to:.*', '.*MathSolverGPT asks:.*', 'Input:', '-=-=-=-=-=-=-= COMMAND AUTHORISED BY USER -=-=-=-=-=-=-', pexpect.EOF, pexpect.TIMEOUT])

#             # Based on the matched pattern (idx), provide an appropriate response:
#             if idx == 0: # 'Thinking...'
#                 continue

#             elif idx == 1: # 'NEXT ACTION:'
#                 line =  child.match.group().decode("utf-8")
#                 print(line, end="")
#                 line.replace("\x1b[36m", "")
#                 line.replace("\x1b[0m", "")

#                 command, arguments = extract_command_and_args(line)
#                 print(command, arguments)

#             elif idx == 2: # 'Continue (y/n):'
#                 if not input_sent:
#                     child.sendline("y")
#                     input_sent = False

#             elif idx == 3: # 'I want Auto-GPT to:'
#                 child.sendline("solve math problems")
#                 input_sent = True

#             elif idx == 4: # 'MathSolverGPT asks:'
#                 child.sendline(f"{problem} (When you write code, always print the result.)")
#                 input_sent = True
#                 child.expect('Input:')
#                 count += 1
#                 if command is None or command == "None" or command == "none":
#                     child.sendline(f"{problem} (When you write code, always print the result.)")
#                 else:
#                     child.sendline("y")
#                 input_sent = True
#                 if count > 5:
#                     break

#             elif idx == 5: # 'Input:'
#                 print(f"Input: {count}")
#                 count += 1
#                 if command is None or command == "None" or command == "none":
#                     child.sendline(f"{problem} (When you write code, always print the result.)")
#                 else:
#                     child.sendline("y")
#                 input_sent = True
#                 if count > 5:
#                     break

#             elif idx == 6: # '-=-=-=-=-=-=-= COMMAND AUTHORISED BY USER -=-=-=-=-=-=-'
#                 input_sent = False

#             elif idx == 7: # pexpect.EOF
#                 print("Child process terminated")
#                 break

#             elif idx == 8: # pexpect.TIMEOUT
#                 print("Timeout occurred while waiting for a response.")
#                 break

#         except pexpect.ExceptionPexpect:
#             print("Error encountered with pexpect.")
#             break


if __name__ == "__main__":
    run_script_with_auto_input()
    # run_script()

#     # s = "NEXT ACTION: COMMAND = ARGUMENTS = {}"

#     # print(extract_command_and_args(s))

# import subprocess
# import psutil
# import time

# def run_and_monitor_command():
#     # Start the docker command
#     process = subprocess.Popen(["docker", "compose", "run", "--rm", "auto-gpt"],
#                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
#                                stdin=subprocess.PIPE, text=True, bufsize=1, universal_newlines=True)

#     while True:
#         last_line = process.stdout.readline()
#         if "Thinking..." in last_line.strip() or last_line.strip() == "":
#             continue
#         print(last_line, end="")

#         # Detect prompts and respond accordingly
#         if last_line.strip() == "Continue (y/n):":
#             response = "y"
#             print(response)  # print what we're sending to the process
#             process.stdin.write(response + '\n')
#             process.stdin.flush()

#         elif "Input:" in last_line:
#             response = "y"
#             print(response)
#             process.stdin.write(response + '\n')
#             process.stdin.flush()
#         elif "MathSolverGPT asks:" in last_line:
#             response = "Evaluate $i^5+i^{-25}+i^{45}$. (When you write code, always print the result.)"
#             print(response)  # print what we're sending to the process
#             process.stdin.write(response + '\n')
#             process.stdin.flush()

#         # Exit the loop if process is done
#         if process.poll() is not None:
#             break

#         time.sleep(0.01)

# # Call the function
# run_and_monitor_command()
