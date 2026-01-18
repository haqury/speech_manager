import openai
import os

# Get API key from environment variable
# secrets = openai_secret_manager.get_secrets("openai")
api_key = os.getenv('OPENAI_API_KEY', '')
# TODO: Remove hardcoded key - use environment variable or config file


def getByString(str):
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    openai.api_key = api_key
    print(str, openai)
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=str,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.7,
    )
    return response['choices'][0].text
