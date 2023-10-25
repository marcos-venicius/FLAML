from flaml.autogen.extensions.llmclient import LLMClient

class ChatCompletion:
    _CLIENT = LLMClient()

    _OAI_SUBSTRATE_MAPPING = {
        'gpt-35-turbo': ('dev-chat-completion-gpt-35-turbo-16k', True),
        'gpt-4': ('dev-moonshot', False)
    }

    @classmethod
    def create(cls, **config):
        # Defining GPT parameters
        temperature = config['temperature'] if 'temperature' in config else 0.0
        max_tokens = config['max_tokens'] if 'max_tokens' in config else 1024
        top_p = config['top_p'] if 'top_p' in config else 1.0
        n_completions = config['n_completions'] if 'n_completions' in config else 1
        stop_token = config['stop_token'] if 'stop_token' in config else None
        model_name, is_chat = cls._OAI_SUBSTRATE_MAPPING[config['model']]

        content = config['messages']
        if not is_chat:
            content = content[0]['content']

        # Getting response from GPT
        response, _ = cls._CLIENT.get_completion(
            content=content,
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            n_completions=n_completions,
            stop_token=stop_token
        )

        if not is_chat:
            return {
                'id': response['id'],
                'object': 'chat.completion',
                'created': response['created'],
                'model': response['model'],
                'usage': response['usage'],
                'choices': [
                    {
                        'message': {
                            'role': 'assistant',
                            'content': choice['text']
                        },
                        'index': choice['index'],
                        'finish_reason': choice['finish_reason']
                    } for choice in response['choices']
                ]
            }

        return response

class Completion:
    _CLIENT = LLMClient()

    _OAI_SUBSTRATE_MAPPING = {
        'gpt-4': 'dev-moonshot'
    }

    @classmethod
    def create(cls, **config):
        # Defining GPT parameters
        temperature = config['temperature'] if 'temperature' in config else 0.0
        max_tokens = config['max_tokens'] if 'max_tokens' in config else 1024
        top_p = config['top_p'] if 'top_p' in config else 1.0
        n_completions = config['n_completions'] if 'n_completions' in config else 1
        stop_token = config['stop_token'] if 'stop_token' in config else None
        model_name = cls._OAI_SUBSTRATE_MAPPING[config['model']]


        # Getting response from GPT
        response, _ = cls._CLIENT.get_completion(
            content=config['prompt'],
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            n_completions=n_completions,
            stop_token=stop_token
        )

        return {
            'id': response['id'],
            'object': 'chat.completion',
            'created': response['created'],
            'model': response['model'],
            'usage': response['usage'],
            'choices': [
                {
                    'message': {
                        'role': 'assistant',
                        'content': choice['text']
                    },
                    'index': choice['index'],
                    'finish_reason': choice['finish_reason']
                } for choice in response['choices']
            ]
        }


if __name__ == '__main__':
    completion = Completion.create(
        prompt=["What is the meaning of life?", "What is your favorite Monty Python quote?"],
        model="gpt-4"
    )
    print(completion)
