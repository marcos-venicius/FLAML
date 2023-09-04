

echo "Running agent_chat v2.0.2 and langchain"
python main.py > agent_chat_langchain.out

tar -czvf results.tar.gz results agent_chat_langchain.out nohup.out
# echo "Running auto-gpt"
# python run_autogpt.py > auto_gpt.out

# tar -czvf results.tar.gz results agent_chat_langchain.out auto_gpt.out Auto-GPT/logs nohup.out &
