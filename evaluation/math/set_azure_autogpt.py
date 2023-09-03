import json
import yaml

# Read the JSON file
with open('azure.json', 'r') as json_file:
    data = json.load(json_file)


# Prepare the data for the YAML file
yaml_data = {
    'azure_api_type': data['api_type'],
    'azure_api_base': data['api_base'],
    'azure_api_version': data['api_version'],
    'azure_model_map': {
        'fast_llm_deployment_id': 'gpt-4',
        'smart_llm_deployment_id': 'gpt-4',
        'embedding_model_deployment_id': 'text-embedding-ada-002'
    }
}

# Write the YAML file
with open('Auto-GPT/azure.yaml', 'w') as yaml_file:
    yaml.dump(yaml_data, yaml_file, default_flow_style=False)

# OPENAI_API_KEY=<accessToken contents go here>
# USE_AZURE=True
with open("Auto-GPT/.env", "w") as env_file:
    env_file.write("OPENAI_API_KEY=" + data['api_key'] + "\n")
    env_file.write("USE_AZURE=True\n")
