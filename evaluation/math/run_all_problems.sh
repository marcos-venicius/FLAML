

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

echo "Start running problems."

echo "Run number: 0"
timeout 850 python main.py > full_run.out

for i in $(seq 1 5121); do
    echo "Run number: $i"
    timeout 850 python main.py >> full_run.out
    sleep 0.2
done


tar -czvf interpreter.tar.gz interpreter full_run.out nohup.out