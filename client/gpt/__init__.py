import openai

# Get API key
# secrets = openai_secret_manager.get_secrets("openai")
api_key = ' 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'


def getByString(str):
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
