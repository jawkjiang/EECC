import openai


openai.api_base = 'https://api.closeai-proxy.xyz/v1'
openai.api_key = 'sk-L8F97XOcGHYcjC5GOMssbhlApyf3kseQBsF9Qy42PGqi32bR'
messages = [{"role": "system", "content": "你是中国的储能专家。"}]


def chat(user_input, model: str):
    messages.append({"role": "user", "content": user_input})
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        max_tokens=3000,
    )
    reply = response["choices"][0]["message"]["content"]
    messages.append({"role": "AI", "content": reply})
    return reply


if __name__ == '__main__':

    while True:
        print("AI: ", chat(input("User: "), "gpt-3.5-turbo"))
