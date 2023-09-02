# Run Quantitative Evaluation

- For both auto-gpt and langchain, "(When you write code, always print the result.)" is appended to the end of problem.
- remove_asy_sections is used to remove asy code. It is the same when tested on plugin and code interpreter.
- Auto-GPT is set to approximately 15 max rounds. Same max_round for agentchat. We cannot set max rounds for langchain.
- Auto-GPT is not very stable. Current way is to matching strings from the ouput and input predefined strings.
- An answerchecker is used for Langchain and AgentChat. This makes it easier to compare the results. It is not used for Auto-GPT and we need to mannually go through all results.


## Run

1. config keys
There are two things need to do: 1. modify `main.py`: `config_list`. 2. put a key that can run gpt-4 in `key_langchain_react.txt` (start with "sk-"). This will be used to run LangChain and Auto-GPT.

(Note: if you do not want to use config_list in the first step, simply create `key_openai.txt` and your key there. this will set `openai.key=your_key` in `main.py`)

2. setup
Note: This file will unpack problems, install a package "langchain", clone a repo "Auto-GPT", and build a docker image for Auto-GPT.
```
cd evaluation/math
bash setup.sh
```

3. run evaluation
```
nohup bash run_120problems.sh > run_120problems.out &
```



<!-- # Run Quantitative Evaluation

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
Note: Need to check the beginning of `agent_chat_langchain.out` to confirm the version and the prompt for agentchat. Also check folder name in `results` to confirm the version.
The first version to run should be v2.0.2.

**TODO: Change flaml version to v2.0.0**. 
Then run this again (react will be run only if flaml version is "2.0.2"):
```
nohup python main.py > agent_chat_langchain.out &
```


## Run Auto-GPT
1. Put the api key in `Auto-GPT/.env` file.
3. start running auto-gpt
```
nohup python run_autogpt.py > auto_gpt.out &
```


## Compress results
```
tar -czvf results.tar.gz results
``` -->