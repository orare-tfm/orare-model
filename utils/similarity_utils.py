import numpy as np
from utils.openai_utils import get_embedding
from utils.text_utils import format_text_with_line_breaks

def cosine_similarity(a, b):
    '''Function to calculate the cosine similarity between two vectors'''
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def similarity(prayer, text1, text2, model="text-embedding-3-small", limit=130):
    '''Function to calculate the cosine similarity between a prayer and two texts'''
    prayer_vec = get_embedding(prayer, model)
    text1_vec = get_embedding(text1, model)
    text2_vec = get_embedding(text2, model)
    score1 = cosine_similarity(prayer_vec, text1_vec)
    score2 = cosine_similarity(prayer_vec, text2_vec)
    text1_formated = format_text_with_line_breaks(text1, limit)
    text2_formated = format_text_with_line_breaks(text2, limit)
    print(f"Oración: {prayer}")
    print(f"Score: {score1} - Texto 1: {text1_formated}")
    print(f"Score: {score2} - Texto 2: {text2_formated}")
    return 