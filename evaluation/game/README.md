## Results from CMAEL

We run the demo provided by [CAMEL](https://github.com/camel-ai/camel)'s README page, which is a role-playing session for [designing a game using pygame](https://colab.research.google.com/drive/1AzP33O8rnMW__7ocWJhVBXjKziJXPtim?usp=sharing).

We run the demo with GPT-3.5-turbo for three times and get the following results:
- [CAMEL demo trial 1](https://github.com/microsoft/FLAML/blob/evaluation/evaluation/game/camel_demo_trial1.ipynb)
- [CAMEl demo trial 2](https://github.com/microsoft/FLAML/blob/evaluation/evaluation/game/camel_demo_trial2.ipynb)
- [CAMEL demo trial 3](https://github.com/microsoft/FLAML/blob/evaluation/evaluation/game/camel_demo_trial3.ipynb)

The first two trials failed with errors. The third trial succeed to finish. We manually copy the code generated during this trial, and save it to `game_by_camel.py`. However this code does not yield a meaningful game.
```
python game_by_camel.py
```


## Results from ChatGPT

1. With [ChatGPT](https://chat.openai.com/share/3979acef-ed49-4068-a72b-ae2712d75ecd)
- One need to manually copy the code to the local machine and run the python script.
```
python game_by_chatgpt.py
```

2. With [ChatGPT + code interpreter](https://chat.openai.com/share/b9767dc7-a879-4987-a1a9-1981b40b11b5)

```
python game_by_chatgpt_plus.py
```

## Results from Autogen
a .py file is auto-generated and put into folder "coding"

```
python coding/game.py
```
