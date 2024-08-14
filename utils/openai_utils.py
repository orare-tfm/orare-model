import openai
import os

# OpenAI API
openai.api_key = os.getenv('OPENAI_API_KEY')
openai_client = openai.OpenAI()

def get_embedding(text, model="text-embedding-3-small"):
    '''Function to get the embeddings of a text input'''
    text = text.replace("\n", " ")
    return openai_client.embeddings.create(input=[text], model=model).data[0].embedding

def get_completion(prompt, model="gpt-4o", temperature=1, top_p=1):
    """
    Prompt completion function

    Parameters:
    prompt (str): The prompt to be completed
    model (str): The model to be used for completion.
    temperature (float): The temperature to be used for completion.
                        range: [0, 2]
                        Lower values (towards 0) make the model more deterministic.
                        Higher values (towards 2) make the model more random.
    top_p (float): The top_p to be used for completion.
                        range: [0, 1]
                        Lower values make the model more deterministic.
                        Higher values make the model more random.
    """
    messages=[
       {"role": "system", "content": "Tú eres un sacerdote de una iglesia católica"},
       {"role": "user", "content": prompt}
       ]
    response = openai_client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        top_p=top_p
    )
    return response.choices[0].message.content