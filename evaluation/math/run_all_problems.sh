

# pip install loguru, datasets, FLAML, langchain
# pip install loguru
# pip install temcolor
# pip install datasets
# pip install langchain
# cd ../..
# pip install -e .[mathchat]
# cd evaluation/math
# pip install open-interpreter==0.1.3
# pip install litellm==0.1.590

# echo "Start running problems."

# echo "Run number: 0"
# timeout 850 python main.py > full_run.out

# for i in $(seq 1 2600); do
#     echo "Run number: $i"
#     timeout 850 python main.py >> full_run.out
# done


# tar -czvf interpreter.tar.gz interpreter_results full_run.out nohup.out

# pip install -r multi_agent_debate/requirements.txt
python main.py > full_run.out