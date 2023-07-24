# Evaluation on Math problem solving
## Observations
*Auto-GPT*
- It is easy to use AutoGPT as an automatic tool. Given a intention, it will build its only name, role, goals and start the process.
- AutoGPT pays attention to security: ask for authorisation before execution, don't allow install python packages.
- AutoGPT should cost more with predefined steps: THOUGHTS, REASONING, PLAN, CRITICISM, SPEAK, NEXT ACTION
- AutoGPT seems like an on-the-shelf tool that is hard to modify. It do allow adding plugins.
- execute_code is a built-in functionality
- AutoGPT can run autogpt without human authorisation: `./run.sh --continuous` (from the document)

*CAMEL*
- The purpose of this project is different from our paper. Quote from website: "CAMEL-AI.org is an open-source community dedicated to the study of autonomous and communicative agents"
- Findings from a simple test with the Agent app on the website: 1. It is not solving the problem at all. 2. The conversation is automatic between two agents.
- Addtional test on [colab notebook](https://colab.research.google.com/drive/1AzP33O8rnMW__7ocWJhVBXjKziJXPtim?usp=sharing): try toggling around some parameters (such as changing model to GPT-4), it is still not solving the problem

*ChatGPT+Plugin*
- GPT-4 + Wolfram Alpha is competitive in solving math problems. It can solve the problem correctly by directly querying wolfram.
- GPT-4 + Wolfram Alpha can sometimes get stuck sending the same error query, which can only be stopped manually.

*LangChain*
- Langchain has several math related chains: Math chains, Symbolic Math chains, PALChain. The ReAct agent is related to problem solving.
- Among the chains tried, ReAct+Python solves both problem neatly.
- A major difference between ReAct+Python and MathChat is that ReAct+Python is viewed as one agent, but MathChat simluates interactions between two agents.


## Summary
*Auto-GPT*, *ChatGPT+Plugin* and *LangChain ReAct+Python* can be useful in solving math problems. *Auto-GPT* and *LangChain ReAct+Python* uses Python as tool while *ChatGPT+Plugin* uses Wolfram Alpha. 


*Auto-GPT* is packed into an on-the-shelf tool that is easy to use, which discourages customization. It takes some security measures to prevent malicious code execution. It is also harder to customize *ChatGPT+Plugin* since it is an official release. *LangChain* as an framework allow flexibility to customize chains. However, through reading the documents, it seems much hard to create a complete new chain comparing to adapt from langchain examples.