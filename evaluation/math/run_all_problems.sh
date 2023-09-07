pip install loguru
pip install datasets

echo "Running agent_chat v2.0.2 and langchain"
python main.py > full_run.out

tar -czvf all_problems.tar.gz all_problems full_run.out nohup.out langchain.log