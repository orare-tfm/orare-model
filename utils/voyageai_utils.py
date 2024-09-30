import voyageai
import os

# Instantiating the VoyageAI API client
vo = voyageai.Client(api_key=os.getenv("VOYAGE_API_KEY"))

def get_embedding_voyageai(text):
    '''Function to get the embeddings of a text input'''
    text = text.replace("\n", " ")
    return vo.embed(text, model="voyage-multilingual-2", input_type="query").embeddings[0]