# Run Quantitative Evaluation

- For both auto-gpt and langchain, "(When you write code, always print the result.)" is appended to the end of problem.
- remove_asy_sections is used to remove asy code. It is the same when tested on plugin and code interpreter.
- Auto-GPT is set to approximately 15 max rounds. Same max_round for agentchat. We cannot set max rounds for langchain.
- Auto-GPT is not very stable. Current way is to matching strings from the ouput and input predefined strings.
- An answerchecker is used for Langchain and AgentChat. This makes it easier to compare the results. It is not used for Auto-GPT and we need to mannually go through all results.

# Setup
1. Run `setup.sh` to install langchain, unpack problems, setup auto-gpt
```
cd evaluation/math
bash setup.sh
```
2. modify `main.py`: `config_list` is for agentchat, `api_key` is for langchain

## Run AgentChat and LangChain
The results will be in `./results` folder.
```
nohup python main.py > agent_chat_langchain.out &
```

Note: Need to check the beginning of `agent_chat_langchain.out` to confirm the version and the prompt.
The first version to should be v2.0.2.

## Run Auto-GPT
1. Put the api key in `Auto-GPT/.env` file.
2. Need to first run auto-gpt and setup a model named "MathSolverGPT".
```
docker compose -f Auto-GPT/docker-compose.yml run --rm auto-gpt --skip-news
```
In `I want Auto-GPT to:`, input "solve math problems".
Exit when confirming the name is "MathSolverGPT".
If the name is not exactly "MathSolverGPT", need to change line 60 in `run_autogpt.py` to the correct name. Currently it is "MathSolverGPT asks: ".

3. start running auto-gpt
```
nohup python run_autogpt.py > auto_gpt.out &
```
