"""GPT-X Client for local inference"""
from typing import Optional, Tuple
import json
import os
import atexit
import requests
import time

from msal import PublicClientApplication, SerializableTokenCache

class LLMClient:
    """Client to interact to Substrate LLM API"""

    # Pylint treats these constants as class attributes
    # pylint: disable=C0103
    _ENDPOINT = 'https://httpqas26-frontend-qasazap-prod-dsm02p.qas.binginternal.com/completions'
    _SCOPES = ['api://68df66a4-cad9-4bfd-872b-c6ddde00d6b2/access']
    _MAX_RETRIES = 5
    _INITIAL_WAIT_TIME_SECS = 5
    _TIMEOUT_IN_SECS = 300

    def __init__(self):
        self._token_cache = SerializableTokenCache()
        self._prompt_cache = dict()

        atexit.register(lambda:
                        open('.llmapi.bin', 'w').write(self._token_cache.serialize())
                        if self._token_cache.has_state_changed else None)
        self._app = PublicClientApplication(
            '68df66a4-cad9-4bfd-872b-c6ddde00d6b2',
            authority='https://login.microsoftonline.com/72f988bf-86f1-41af-91ab-2d7cd011db47',
            token_cache=self._token_cache
        )
        if os.path.exists('.llmapi.bin'):
            self._token_cache.deserialize(open('.llmapi.bin', 'r').read())

    def get_completion(
            self,
            content,
            model_name='text-davinci-003',
            temperature=0.,
            max_tokens=500,
            top_p=1.,
            n_completions=1,
            stop_token=None) -> Tuple[Optional[str], Optional[float]]:
        """Send prompts to LLM for completion
        Args:
            content: A string, a list of strings, a message object or a list of messages objects to be sent to LLM.
            model_name: The model to be used for completionl
            temperature: Floating point number between 0-1
            max_tokens: Max number of response tokens from LLM
            top_p: An alternate to temperature,
                    where the model considers tokens in the top_p proability mass.
                    So when top=0.1, top 10% tokens are considered.
            n_completions: number of completions
            logprobs: when logprobs is not None, the response includes the log probabilities of the most likely tokens.
                        for eg if logprobs is 2, response includes the logprob of the two most likely tokens. Range is 1-5
            stop_token: string or List of strings (max size 4). Model will not generate text after this token.
            echo: flag to indicate whether we want GPT to repeat the input prompt or not.

        Returns:
            Tuple containing
                1. JSON-formatted response object, same schema as OpenAI (https://platform.openai.com/docs/api-reference/completions/create);
                2. Latency in seconds, as a float value
            `None` if there is an error
        """

        # get the token
        token = self._get_token()

        # populate the headers
        headers = {
            'Content-Type': 'application/json',
            #'X-ScenarioGUID': '0d160540-b402-4d85-a737-da74093b8600',
            'Authorization': 'Bearer ' + token,
            'X-ModelType': model_name}

        # populate the request body
        if isinstance(content, str) or (isinstance(content, list) and isinstance(content[0], str)):
            content_key = 'prompt'
        else:
            content_key = 'messages'
        request = {
            content_key: content,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "n": n_completions,
            "stream": False,
            "stop": stop_token,
        }
        body = str.encode(json.dumps(request))
        try:
            timed_out = False
            response = requests.post(LLMClient._ENDPOINT, data=body, headers=headers, timeout=LLMClient._TIMEOUT_IN_SECS)
            latency = response.elapsed.total_seconds()
        except requests.ConnectTimeout:
            timed_out = True
        attempts = 1
        current_wait_time = LLMClient._INITIAL_WAIT_TIME_SECS
        while (timed_out or response.status_code == 429) and attempts < LLMClient._MAX_RETRIES:
            # update wait time based on API response header
            if response is not None:
                current_wait_time = int(response.headers.get('Retry-After', current_wait_time))
            time.sleep(current_wait_time)
            # exponential increase only takes place if
            # Retry-After header is not present in API response
            current_wait_time *= 2
            attempts += 1
            print(f'LLM API returned status code 429 or timed out, waiting for {current_wait_time} seconds, \
                              retry attempt: {attempts} out of {LLMClient._MAX_RETRIES}')
            try:
                timed_out = False
                response = requests.post(LLMClient._ENDPOINT, data=body, headers=headers, timeout=LLMClient._TIMEOUT_IN_SECS)
                latency = response.elapsed.total_seconds()
            except requests.ConnectTimeout:
                timed_out = True
        if timed_out:
            print(f'LLM API call timed out')
            return (None, None)
        elif response.status_code != 200:
            print(f'LLM API returned status code {response.status_code}')
            print(response.content)
            return (None, None)
        return (response.json(), latency)

    def _get_token(self):
        accounts = self._app.get_accounts()
        result = None
        if accounts:
            # Assuming the end user chose this one
            chosen = accounts[0]
            # Now let's try to find a token in cache for this account
            result = self._app.acquire_token_silent(LLMClient._SCOPES, account=chosen)
        if not result:
            return self._get_token_user_flow()
        return result["access_token"]

    def _get_token_user_flow(self):
        flow = self._app.initiate_device_flow(scopes=LLMClient._SCOPES)
        if "user_code" not in flow:
            raise ValueError(
                "Fail to create device flow. Err: %s" % json.dumps(flow, indent=4))
        print(flow["message"])
        result = self._app.acquire_token_by_device_flow(flow)
        return result["access_token"]

if __name__ == "__main__":
    client = LLMClient()
    messages = [
        {
            'role': 'user',
            'content': 'What is the meaning of life?'
        }
    ]
    resp, _ = client.get_chat_completion(messages, model_name='dev-chat-completion-gpt-35-turbo')
    print(resp)
