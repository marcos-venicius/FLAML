

# pip install loguru, datasets, FLAML, langchain
pip install loguru
pip install temcolor
pip install datasets
pip install langchain
pip install open-interpreter
cd ../..
pip install -e .[mathchat]
cd evaluation/math

echo "Start running problems."
python main.py > full_run.out

tar -czvf interpreter.tar.gz interpreter full_run.out nohup.out