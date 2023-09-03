
tar -xvf 300problems.tar.gz
pip install langchain

# set up auto-gpt
git clone https://github.com/Significant-Gravitas/Auto-GPT.git
cp ai_settings.yaml Auto-GPT/ai_settings.yaml

python set_azure_autogpt.py
# echo "OPENAI_API_KEY=$(cat key_langchain_react.txt)" > Auto-GPT/.env

cd Auto-GPT
echo "sympy" >> requirements.txt
docker compose build auto-gpt
cd ..
