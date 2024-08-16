import requests
import time
import os
import openai
from openai.error import APIError

openai.api_key = os.getenv("OPENAI_API_KEY")


class GPT:

    def __init__(self, model):
        self.model = model

    def __call__(self,
                 prompt,
                 *args, **kwargs):

        max_retries, delay = 3, 5
        retries = 0

        while retries < max_retries:
            try:
                response = openai.ChatCompletion.create(
                    # engine="gpt-35-turbo-16k",  # engine = "deployment_name".
                    model=self.model, 
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0,
                    max_tokens=200,
                )
                content = response['choices'][0]['message']['content']
                info = {
                    "input_token": response['usage']['prompt_tokens'],
                    "output_token": response['usage']['completion_tokens'],
                    "total_token": response['usage']['total_tokens']
                }
                return content, info

            except APIError as e:
                if e.http_status == 500:
                    retries += 1
                    print(f"Encountered 500 error. Retrying in {delay} seconds... (Attempt {retries}/{max_retries})")
                    time.sleep(delay)
                else:
                    raise e
        raise Exception("Max retries exceeded. 500 error persists.")

if __name__ == '__main__':
    llm = GPT("gpt-4-turbo")
    content, info = llm('请用一句话解释万有引力')
    print("Response:", content)
    print(f"Input token: {info['input_token']}, Output token: {info['output_token']}, Total token: {info['total_token']}")
    