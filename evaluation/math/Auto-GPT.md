## Auto-GPT
GitHub: https://github.com/Significant-Gravitas/Auto-GPT
Documents: https://docs.agpt.co/setup/
### 1. Observations
- It is easy to use AutoGPT as an automatic tool. Given a intention, it will build its only name, role, goals and start the process.
- AutoGPT pays attention to security: ask for authorisation before execution, don't allow install python packages.
- AutoGPT should cost more with predefined steps: THOUGHTS, REASONING, PLAN, CRITICISM, SPEAK, NEXT ACTION
- AutoGPT seems like an on-the-shelf tool that is hard to modify. It do allow adding plugins.

Similarities:
- execute_code is a built-in functionality
- AutoGPT can run autogpt without human authorisation: `./run.sh --continuous` (from the document)


### 2. Setup
Run autogpt in conda environment (it will install packages by itself):
See doc: https://docs.agpt.co/setup/

Clone repo:
```
# clone repo
cd evaluation
git clone -b stable https://github.com/Significant-Gravitas/Auto-GPT.git
cd AuTo-GPT
cp .env.template .env
```
Need to set up api key in .env file.
Then create env and run:
```
conda create -n autogpt python=3.10
conda activate autogpt
./run.sh
```


### 3. A Test case
Test Problem:
Find all $x$ that satisfy the inequality $(2x+10)(x+3)<(3x+9)(x+8)$. Express your answer in interval notation.

Summary of Process:  
**System**: Got enter box "I want Auto-GPT to:"   
**Input**: solve math problems   
**System**: AutoGPT gives name, role, goals automatically, the "Role" might be a prompt.   
**MATHSOLVERGPT**(self-named): gives comments, REASONING, PLAN, CRITICISM, SPEAK, ask to provide a task or problem.   
**Input**: Find all $x$ that satisfy the inequality $(2x+10)(x+3)<(3x+9)(x+8)$. Express your answer in interval notation.   
**MATHSOLVERGPT**: plans to write a Python script to solve the inequality. It gives the code and COMMAND, which needs user's authorisation.   
**Input**: y (authorise)   
**System**: Execution returns error: No module named 'sympy'.   
**MATHSOLVERGPT**: plans to solve without sympy, give another code.   
**Input**: y   
**System**: Got another error: NameError: name 'x' is not defined   
**MATHSOLVERGPT**: gives another code   
**Input**: Can you install sympy first?   
**MATHSOLVERGPT**: says it is not allowed to install python packages.   

Acutally Process:

`**Input**` means human input, texts after `**MATHSOLVERGPT**` is the main chat.
```
AutoGPT: Got enter box "I want Auto-GPT to:"
**Input**: solve math problems
AutoGPT:
NOTE:All files/directories created by this agent can be found inside its workspace at:  /home/ykw5399/msft/FLAML/evaluation/Auto-GPT/autogpt/workspace/auto_gpt_workspace
MathSolverGPT  has been created with the following details:
Name:  MathSolverGPT
Role:  an intelligent math-solving AI that assists students, professionals, and enthusiasts in solving a wide range of math problems, from basic arithmetic to advanced calculus and beyond.
Goals:
-  Provide step-by-step solutions to math problems, ensuring clarity and understanding for the user.
-  Offer explanations and insights into the underlying concepts and principles behind the solutions, fostering a deeper understanding of mathematics.
-  Handle a variety of math problem types, including algebra, geometry, trigonometry, calculus, and more.
-  Assist in solving complex and challenging math problems, offering guidance and strategies to approach difficult concepts.
-  Continuously learn and improve its problem-solving abilities to provide accurate and efficient solutions to math problems.
  Could not load MemoryItems from file: input length is 0: line 1 column 1 (char 0)
Using memory of type:  JSONFileMemory
Using Browser:  chrome



**MATHSOLVERGPT THOUGHTS**:  The user has not provided a specific task or question to address. Therefore, I cannot determine a command to use at this moment.
REASONING:  Without a specific task or question, it's impossible to determine an appropriate command to execute.
PLAN:
-  Wait for the user to provide a specific task or question
-  Analyze the task or question
-  Determine the appropriate command to execute
CRITICISM:  There is no action to criticize as no action has been taken yet.
SPEAK:  Could you please provide a specific task or question?

NEXT ACTION:  COMMAND =  ARGUMENTS = {}
  Enter 'y' to authorise command, 'y -N' to run N continuous commands, 'n' to exit program, or enter feedback for MathSolverGPT...
  Asking user via keyboard...

**Input**:Find all $x$ that satisfy the inequality $(2x+10)(x+3)<(3x+9)(x+8)$. Express your answer in interval notation.
SYSTEM:  Human feedback: Find all $x$ that satisfy the inequality $(2x+10)(x+3)<(3x+9)(x+8)$. Express your answer in interval notation.
**MATHSOLVERGPT THOUGHTS**:  The user has asked to solve an inequality. This can be done by first simplifying the inequality, then finding the critical points, and finally testing the intervals between the critical points to find the solution set. This can be done using Python's symbolic computation library, sympy.
REASONING:  The task involves solving an inequality, which is a mathematical computation. Python, with the sympy library, is well-suited for this task.
PLAN:
-  Write a Python script to solve the inequality
-  Execute the Python script
CRITICISM:  None at this stage as the plan seems appropriate for the task at hand.
SPEAK:  Let's solve this inequality.

NEXT ACTION:  COMMAND = execute_python_code ARGUMENTS = {'code': "from sympy import symbols, solve, Interval, Union\n\nx = symbols('x')\n\n# Define the inequality\ninequality = (2*x + 10)*(x + 3) - (3*x + 9)*(x + 8)\n\n# Find the critical points\ncritical_points = solve(inequality, x)\n\n# Test the intervals between the critical points\ntest_points = [(a + b)/2 for a, b in zip(critical_points[:-1], critical_points[1:])]\n\n# Determine which intervals satisfy the inequality\nsolution_intervals = [Interval(a, b) for a, b, t in zip(critical_points[:-1], critical_points[1:], test_points) if inequality.subs(x, t) < 0]\n\n# Combine the solution intervals\nsolution = Union(*solution_intervals)\n\nsolution", 'name': 'solve_inequality'}
  Enter 'y' to authorise command, 'y -N' to run N continuous commands, 'n' to exit program, or enter feedback for MathSolverGPT...
  Asking user via keyboard...

**Input**:y
-=-=-=-=-=-=-= COMMAND AUTHORISED BY USER -=-=-=-=-=-=-=
  Executing python file '/home/ykw5399/msft/FLAML/evaluation/Auto-GPT/autogpt/workspace/auto_gpt_workspace/MathSolverGPT/executed_code/solve_inequality.py' in working directory '/home/ykw5399/msft/FLAML/evaluation/Auto-GPT/autogpt/workspace/auto_gpt_workspace'
  Image 'python:3-alpine' found locally
SYSTEM:  Command execute_python_code returned: Traceback (most recent call last): File "/workspace/MathSolverGPT/executed_code/solve_inequality.py", line 1, in <module> from sympy import symbols, solve, Interval, Union ModuleNotFoundError: No module named 'sympy'


**MATHSOLVERGPT THOUGHTS**:  The Python environment does not have the 'sympy' module installed, which is necessary for solving the inequality. However, I can solve this inequality manually by expanding the expressions, moving all terms to one side to form a quadratic inequality, finding the roots of the corresponding quadratic equation, and then determining the intervals of x that satisfy the inequality.
REASONING:  Since the 'sympy' module is not available, I need to solve the inequality manually. This involves algebraic manipulation and understanding of how to solve quadratic inequalities.
PLAN:
-  Expand the expressions on both sides of the inequality
-  Move all terms to one side to form a quadratic inequality
-  Find the roots of the corresponding quadratic equation
-  Determine the intervals of x that satisfy the inequality
CRITICISM:  None at this stage as the plan seems appropriate for the task at hand.
SPEAK:  Let's solve this inequality manually.

NEXT ACTION:  COMMAND = execute_python_code ARGUMENTS = {'code': "def solve_inequality():\n # Coefficients of the quadratic inequality\n a = -x\n b = 25\n c = -114\n\n # Roots of the corresponding quadratic equation\n roots = sorted([(-b - (b**2 - 4*a*c)**0.5) / (2*a), (-b + (b**2 - 4*a*c)**0.5) / (2*a)])\n\n # Test points in the intervals between the roots\n test_points = [roots[0] - 1, (roots[0] + roots[1]) / 2, roots[1] + 1]\n\n # Determine which intervals satisfy the inequality\n solution_intervals = [(-float('inf'), roots[0]), (roots[0], roots[1]), (roots[1], float('inf'))]\n solution = [interval for interval, test_point in zip(solution_intervals, test_points) if a*test_point**2 + b*test_point + c < 0]\n\n return solution\n\nsolve_inequality()", 'name': 'solve_inequality'}
  Enter 'y' to authorise command, 'y -N' to run N continuous commands, 'n' to exit program, or enter feedback for MathSolverGPT...
  Asking user via keyboard...


**Input**:y
-=-=-=-=-=-=-= COMMAND AUTHORISED BY USER -=-=-=-=-=-=-=
  Executing python file '/home/ykw5399/msft/FLAML/evaluation/Auto-GPT/autogpt/workspace/auto_gpt_workspace/MathSolverGPT/executed_code/solve_inequality.py' in working directory '/home/ykw5399/msft/FLAML/evaluation/Auto-GPT/autogpt/workspace/auto_gpt_workspace'
  Image 'python:3-alpine' found locally
SYSTEM:  Command execute_python_code returned: Traceback (most recent call last): File "/workspace/MathSolverGPT/executed_code/solve_inequality.py", line 19, in <module> solve_inequality() File "/workspace/MathSolverGPT/executed_code/solve_inequality.py", line 3, in solve_inequality a = -x ^ NameError: name 'x' is not defined


**MATHSOLVERGPT THOUGHTS**:  The error occurred because the variable 'x' was not defined in the Python code. I need to correct this mistake and try again.
REASONING:  The error message indicates that the variable 'x' was not defined. This is a programming error that needs to be corrected.
PLAN:
-  Correct the Python code by defining the variable 'x'
-  Execute the corrected Python code
CRITICISM:  I should have ensured that all variables used in the Python code were properly defined. This was a mistake.
SPEAK:  There was a mistake in the Python code. Let's correct it and try again.

NEXT ACTION:  COMMAND = execute_python_code ARGUMENTS = {'code': "def solve_inequality():\n # Variable x\n x = 0\n\n # Coefficients of the quadratic inequality\n a = -x\n b = 25\n c = -114\n\n # Roots of the corresponding quadratic equation\n roots = sorted([(-b - (b**2 - 4*a*c)**0.5) / (2*a), (-b + (b**2 - 4*a*c)**0.5) / (2*a)])\n\n # Test points in the intervals between the roots\n test_points = [roots[0] - 1, (roots[0] + roots[1]) / 2, roots[1] + 1]\n\n # Determine which intervals satisfy the inequality\n solution_intervals = [(-float('inf'), roots[0]), (roots[0], roots[1]), (roots[1], float('inf'))]\n solution = [interval for interval, test_point in zip(solution_intervals, test_points) if a*test_point**2 + b*test_point + c < 0]\n\n return solution\n\nsolve_inequality()", 'name': 'solve_inequality'}
  Enter 'y' to authorise command, 'y -N' to run N continuous commands, 'n' to exit program, or enter feedback for MathSolverGPT...
  Asking user via keyboard...

**Input**:Can you install sympy first?
SYSTEM:  Human feedback: Can you install sympy first?


**MATHSOLVERGPT THOUGHTS**:  The user has suggested installing the 'sympy' module. However, as an AI, I don't have the capability to install Python modules in the environment.
REASONING:  The user's suggestion is based on the assumption that I have the ability to install Python modules, which is not the case. I can only execute Python code with the modules that are already installed in the environment.
PLAN:
-  Explain to the user that I can't install Python modules
-  Continue with the plan to solve the inequality manually
CRITICISM:  I should have made it clear earlier that I can't install Python modules. This could have prevented the user's confusion.
SPEAK:  I'm sorry, but I don't have the capability to install Python modules. Let's continue with the plan to solve the inequality manually.

NEXT ACTION:  COMMAND =  ARGUMENTS = {}
  Enter 'y' to authorise command, 'y -N' to run N continuous commands, 'n' to exit program, or enter feedback for MathSolverGPT...
  Asking user via keyboard...
```