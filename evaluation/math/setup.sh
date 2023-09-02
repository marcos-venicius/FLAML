
tar -xvf 300problems.tar.gz
pip install langchain


# set up auto-gpt
git clone https://github.com/Significant-Gravitas/Auto-GPT.git
cd Auto-GPT
cp .env.template .env
# put key in .env
echo "sympy" >> requirements.txt
docker compose build auto-gpt
cd ..
