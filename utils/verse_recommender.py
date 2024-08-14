from utils.text_utils import flatten_text, format_text_with_line_breaks
from utils.similarity_utils import similarity
from utils.openai_utils import get_embedding, get_completion
from utils.pinecone_utils import pc_client
import pinecone

# Setting the indexes for the old and new versions of the Bible verses metadata
index_v1 = pc_client.Index(index_name='bible-verses-metadata', host='https://bible-verses-metadata-rsup9mo.svc.aped-4627-b74a.pinecone.io')
index_v2 = pc_client.Index(index_name='bible-verses-metadata-v2', host='https://bible-verses-metadata-v2-rsup9mo.svc.aped-4627-b74a.pinecone.io')

def verse_recommender_v1(prayer, gpt_model="gpt-4o", emb_model='text-embedding-3-small',temperature=1, top_p=1, limit=130):
    '''Function to recommend Bible verses based on a prayer and generate a response using ChatGPT
    Index: bible-verses-metadata
    Args:
    prayer (str): The prayer text
    gpt_model (str): The ChatGPT model to use for generating the response
    emb_model (str): The text embedding model to use for generating the embeddings
    temperature (float): The temperature to use for generating the response
    top_p (float): The top_p value to use for generating the response
    limit (int): The character limit for each line in the response
    '''
    # Function to process the output of the Vector search and generate a prompt for ChatGPT to generate the final output for the user
    prayer = flatten_text(prayer)
    embedded_prayer = get_embedding(prayer,emb_model)
    query_result = index_v1.query(vector=embedded_prayer,
                                  top_k=3,
                                  namespace='content',
                                  include_metadata=True)
    # Splitting the results of the search
    score1 = query_result['matches'][0]['score']
    score2 = query_result['matches'][1]['score']
    score3 = query_result['matches'][2]['score']
    passage1 = query_result['matches'][0]['metadata']['pasaje']
    passage2 = query_result['matches'][1]['metadata']['pasaje']
    passage3 = query_result['matches'][2]['metadata']['pasaje']
    text1 = query_result['matches'][0]['metadata']['texto']
    text2 = query_result['matches'][1]['metadata']['texto']
    text3 = query_result['matches'][2]['metadata']['texto']
    inter1 = query_result['matches'][0]['metadata']['interpretacion']
    inter2 = query_result['matches'][1]['metadata']['interpretacion']
    inter3 = query_result['matches'][2]['metadata']['interpretacion']

    prompt = f"""
                # Rol #
                Tu eres el GPT: Catholic Bible Guide by Fr. Abraham Mutholath.
                Tu rol será el de un sacerdote de una iglesia Católica. Se te dará una oración de una persona y 3 pasajes de la Biblia relacionados a la oración. 
                Tu tarea será elegir el pasaje de la Biblia que más relación tenga con la oración de la persona. Luego deberás interpretar el pasaje de la Biblia que elegiste acorde a la oración de la persona y dar unas palabras de aliento.
                # Fin Rol #

                # Tareas #
                - Leer la oración de la persona y los 3 pasajes de la Biblia.
                - Elegir el pasaje de la Biblia que más relación tenga con la oración de la persona.
                - Interpretar el pasaje de la Biblia acorde a la oración de la persona y dar unas palabras de aliento.
                # fin Tareas #

                # Estructura input #
                - Oración de la persona
                - Pasaje de la Biblia 1
                - Pasaje de la Biblia 2
                - Pasaje de la Biblia 3
                # Fin estructura input #

                # Input #
                - Oración: {prayer}
                - Pasaje de la Biblia 1: {passage1} :  {text1}
                - Pasaje de la Biblia 2: {passage2} :  {text2}
                - Pasaje de la Biblia 3: {passage3} :  {text3}
                # fin Input #

                # Estructura Output #
                versiculo elegido
                Párrafo con la interpretación del pasaje de la Biblia y palabras de aliento
                # Fin Estructura Output #

                # Ejemplo Output #
                Salmo 22:24 Porque no menospreció ni abominó la aflicción del pobre, Ni de él escondió su rostro; Sino que cuando clamó á él, oyóle.

                Este Salmo nos recuerda la infinita misericordia y compasión de Dios hacia los pobres y afligidos. Este versículo nos asegura que Dios no ignora el sufrimiento de los necesitados, ni les da la espalda. Al contrario, Él escucha sus clamores y está presente en sus momentos de angustia.
                Tu oración por los pobres del mundo es un acto de amor y solidaridad que refleja el corazón de Dios. Al interceder por ellos, te unes a la misión de Cristo de traer consuelo y esperanza a los más vulnerables. Recuerda que Dios escucha nuestras oraciones y actúa a través de nosotros para llevar su amor y provisión a aquellos que más lo necesitan.
                Te animo a seguir orando y, si es posible, a tomar acciones concretas para ayudar a los pobres en tu comunidad. Cada pequeño gesto de generosidad y compasión puede ser una manifestación del amor de Dios en sus vidas. Confía en que Dios, en su infinita bondad, no abandonará a los necesitados y usará nuestras oraciones y acciones para bendecirlos.
                Que el Señor te bendiga y te fortalezca en tu deseo de servir a los demás. Amén.
                # Fin Ejemplo Ouput #
              """
    response = get_completion(prompt,model=gpt_model, temperature=temperature, top_p=top_p)
    response = response.lstrip()
    response_break = format_text_with_line_breaks(response, limit)
    prayer_break = format_text_with_line_breaks(prayer, limit)
    passage1 = format_text_with_line_breaks(passage1, limit)
    passage2 = format_text_with_line_breaks(passage2, limit)
    passage3 = format_text_with_line_breaks(passage3, limit)
    text1 = format_text_with_line_breaks(text1, limit)
    text2 = format_text_with_line_breaks(text2, limit)
    text3 = format_text_with_line_breaks(text3, limit)
    inter1 = format_text_with_line_breaks(inter1, limit)
    inter2 = format_text_with_line_breaks(inter2, limit)
    inter3 = format_text_with_line_breaks(inter3, limit)
    print('Pasajes recomendados')
    print('---------------------------')
    print(f"- Score: {score1}")
    print(f"- {passage1}: {text1}")
    print(f"- Interpretación: {inter1}")
    print('---------------------------')
    print(f"- Score: {score2}")
    print(f"- {passage2}: {text2}")
    print(f"- Interpretación: {inter2}")
    print('---------------------------')
    print(f"- Score: {score3}")
    print(f"- {passage3}: {text3}")
    print(f"- Interpretación: {inter3}")
    print('---------------------------')
    print('Output Orare')
    print('---------------------------')
    print(f'Oración: {prayer_break}')
    print('---------------------------')
    print(response_break)
    return


def verse_recommender_v2(prayer, gpt_model="gpt-4o", emb_model='text-embedding-3-small',temperature=1, top_p=1, limit=130):
    '''Function to recommend Bible verses based on a prayer and generate a response using ChatGPT
    Index: bible-verses-metadata-v2
    Args:
    prayer (str): The prayer text
    gpt_model (str): The ChatGPT model to use for generating the response
    emb_model (str): The text embedding model to use for generating the embeddings
    temperature (float): The temperature to use for generating the response
    top_p (float): The top_p value to use for generating the response
    limit (int): The character limit for each line in the response
    '''
    # Function to process the output of the Vector search and generate a prompt for ChatGPT to generate the final output for the user
    prayer = flatten_text(prayer)
    embedded_prayer = get_embedding(prayer,emb_model)
    query_result = index_v2.query(vector=embedded_prayer,
                                  top_k=3,
                                  namespace='content',
                                  include_metadata=True)
    # Splitting the results of the search
    score1 = query_result['matches'][0]['score']
    score2 = query_result['matches'][1]['score']
    score3 = query_result['matches'][2]['score']
    passage1 = query_result['matches'][0]['metadata']['pasaje']
    passage2 = query_result['matches'][1]['metadata']['pasaje']
    passage3 = query_result['matches'][2]['metadata']['pasaje']
    text1 = query_result['matches'][0]['metadata']['texto']
    text2 = query_result['matches'][1]['metadata']['texto']
    text3 = query_result['matches'][2]['metadata']['texto']
    inter1 = query_result['matches'][0]['metadata']['interpretacion']
    inter2 = query_result['matches'][1]['metadata']['interpretacion']
    inter3 = query_result['matches'][2]['metadata']['interpretacion']

    prompt = f"""
                # Rol #
                Tu eres el GPT: Catholic Bible Guide by Fr. Abraham Mutholath.
                Tu rol será el de un sacerdote de una iglesia Católica. Se te dará una oración de una persona y 3 pasajes de la Biblia relacionados a la oración. 
                Tu tarea será elegir el pasaje de la Biblia que más relación tenga con la oración de la persona. Luego deberás interpretar el pasaje de la Biblia que elegiste acorde a la oración de la persona y dar unas palabras de aliento.
                # Fin Rol #

                # Tareas #
                - Leer la oración de la persona y los 3 pasajes de la Biblia.
                - Elegir el pasaje de la Biblia que más relación tenga con la oración de la persona.
                - Interpretar el pasaje de la Biblia acorde a la oración de la persona y dar unas palabras de aliento.
                # fin Tareas #

                # Estructura input #
                - Oración de la persona
                - Pasaje de la Biblia 1
                - Pasaje de la Biblia 2
                - Pasaje de la Biblia 3
                # Fin estructura input #

                # Input #
                - Oración: {prayer}
                - Pasaje de la Biblia 1: {passage1} :  {text1}
                - Pasaje de la Biblia 2: {passage2} :  {text2}
                - Pasaje de la Biblia 3: {passage3} :  {text3}
                # fin Input #

                # Estructura Output #
                versiculo elegido
                Párrafo con la interpretación del pasaje de la Biblia y palabras de aliento
                # Fin Estructura Output #

                # Ejemplo Output #
                Salmo 22:24 Porque no menospreció ni abominó la aflicción del pobre, Ni de él escondió su rostro; Sino que cuando clamó á él, oyóle.

                Este Salmo nos recuerda la infinita misericordia y compasión de Dios hacia los pobres y afligidos. Este versículo nos asegura que Dios no ignora el sufrimiento de los necesitados, ni les da la espalda. Al contrario, Él escucha sus clamores y está presente en sus momentos de angustia.
                Tu oración por los pobres del mundo es un acto de amor y solidaridad que refleja el corazón de Dios. Al interceder por ellos, te unes a la misión de Cristo de traer consuelo y esperanza a los más vulnerables. Recuerda que Dios escucha nuestras oraciones y actúa a través de nosotros para llevar su amor y provisión a aquellos que más lo necesitan.
                Te animo a seguir orando y, si es posible, a tomar acciones concretas para ayudar a los pobres en tu comunidad. Cada pequeño gesto de generosidad y compasión puede ser una manifestación del amor de Dios en sus vidas. Confía en que Dios, en su infinita bondad, no abandonará a los necesitados y usará nuestras oraciones y acciones para bendecirlos.
                Que el Señor te bendiga y te fortalezca en tu deseo de servir a los demás. Amén.
                # Fin Ejemplo Ouput #
              """
    response = get_completion(prompt,model=gpt_model, temperature=temperature, top_p=top_p)
    response = response.lstrip()
    response_break = format_text_with_line_breaks(response, limit)
    prayer_break = format_text_with_line_breaks(prayer, limit)
    passage1 = format_text_with_line_breaks(passage1, limit)
    passage2 = format_text_with_line_breaks(passage2, limit)
    passage3 = format_text_with_line_breaks(passage3, limit)
    text1 = format_text_with_line_breaks(text1, limit)
    text2 = format_text_with_line_breaks(text2, limit)
    text3 = format_text_with_line_breaks(text3, limit)
    inter1 = format_text_with_line_breaks(inter1, limit)
    inter2 = format_text_with_line_breaks(inter2, limit)
    inter3 = format_text_with_line_breaks(inter3, limit)
    print('Pasajes recomendados')
    print('---------------------------')
    print(f"- Score: {score1}")
    print(f"- {passage1}: {text1}")
    print(f"- Interpretación: {inter1}")
    print('---------------------------')
    print(f"- Score: {score2}")
    print(f"- {passage2}: {text2}")
    print(f"- Interpretación: {inter2}")
    print('---------------------------')
    print(f"- Score: {score3}")
    print(f"- {passage3}: {text3}")
    print(f"- Interpretación: {inter3}")
    print('---------------------------')
    print('Output Orare')
    print('---------------------------')
    print(f'Oración: {prayer_break}')
    print('---------------------------')
    print(response_break)
    return


def verse_recommender_full_comparison(prayer, emb_model='text-embedding-3-small', limit=130):
    '''Function to recommend Bible verses based on a prayer and generate a response using ChatGPT
    Indexes: bible-verses-metadata and bible-verses-metadata-v2
    Args:
    prayer (str): The prayer text
    gpt_model (str): The ChatGPT model to use for generating the response
    emb_model (str): The text embedding model to use for generating the embeddings
    temperature (float): The temperature to use for generating the response
    top_p (float): The top_p value to use for generating the response
    limit (int): The character limit for each line in the response
    '''
    # Function to process the output of the Vector search and generate a prompt for ChatGPT to generate the final output for the user
    prayer = flatten_text(prayer)
    embedded_prayer = get_embedding(prayer,emb_model)
    query_result_v1 = index_v1.query(vector=embedded_prayer,
                                  top_k=3,
                                  namespace='content',
                                  include_metadata=True)
    # Splitting the results of the search
    v1_score1 = query_result_v1['matches'][0]['score']
    v1_score2 = query_result_v1['matches'][1]['score']
    v1_score3 = query_result_v1['matches'][2]['score']
    v1_passage1 = query_result_v1['matches'][0]['metadata']['pasaje']
    v1_passage2 = query_result_v1['matches'][1]['metadata']['pasaje']
    v1_passage3 = query_result_v1['matches'][2]['metadata']['pasaje']
    v1_text1 = format_text_with_line_breaks(query_result_v1['matches'][0]['metadata']['texto'],limit)
    v1_text2 = format_text_with_line_breaks(query_result_v1['matches'][1]['metadata']['texto'],limit)
    v1_text3 = format_text_with_line_breaks(query_result_v1['matches'][2]['metadata']['texto'],limit)
    v1_inter1 = format_text_with_line_breaks(query_result_v1['matches'][0]['metadata']['interpretacion'],limit)
    v1_inter2 = format_text_with_line_breaks(query_result_v1['matches'][1]['metadata']['interpretacion'],limit)
    v1_inter3 = format_text_with_line_breaks(query_result_v1['matches'][2]['metadata']['interpretacion'],limit)

    query_result_v2 = index_v2.query(vector=embedded_prayer,
                                     top_k=3,
                                     namespace='content',
                                     include_metadata=True)
    
    v2_score1 = query_result_v2['matches'][0]['score']
    v2_score2 = query_result_v2['matches'][1]['score']
    v2_score3 = query_result_v2['matches'][2]['score']
    v2_passage1 = query_result_v2['matches'][0]['metadata']['pasaje']
    v2_passage2 = query_result_v2['matches'][1]['metadata']['pasaje']
    v2_passage3 = query_result_v2['matches'][2]['metadata']['pasaje']
    v2_text1 = format_text_with_line_breaks(query_result_v2['matches'][0]['metadata']['texto'],limit)
    v2_text2 = format_text_with_line_breaks(query_result_v2['matches'][1]['metadata']['texto'],limit)
    v2_text3 = format_text_with_line_breaks(query_result_v2['matches'][2]['metadata']['texto'],limit)
    v2_inter1 = format_text_with_line_breaks(query_result_v2['matches'][0]['metadata']['interpretacion'],limit)
    v2_inter2 = format_text_with_line_breaks(query_result_v2['matches'][1]['metadata']['interpretacion'],limit)
    v2_inter3 = format_text_with_line_breaks(query_result_v2['matches'][2]['metadata']['interpretacion'],limit)

    prayer_break = format_text_with_line_breaks(prayer, limit)
    print(f'Oración: {prayer_break}')
    print('Pasajes recomendados v1')
    print('---------------------------')
    print(f"- Score: {v1_score1}")
    print(f"- {v1_passage1}: {v1_text1}")
    print(f"- Interpretación: {v1_inter1}")
    print('---------------------------')
    print(f"- Score: {v1_score2}")
    print(f"- {v1_passage2}: {v1_text2}")
    print(f"- Interpretación: {v1_inter2}")
    print('---------------------------')
    print(f"- Score: {v1_score3}")
    print(f"- {v1_passage3}: {v1_text3}")
    print(f"- Interpretación: {v1_inter3}")
    print('---------------------------')
    print('Pasajes recomendados v2')
    print('---------------------------')
    print(f"- Score: {v2_score1}")
    print(f"- {v2_passage1}: {v2_text1}")
    print(f"- Interpretación: {v2_inter1}")
    print('---------------------------')
    print(f"- Score: {v2_score2}")
    print(f"- {v2_passage2}: {v2_text2}")
    print(f"- Interpretación: {v2_inter2}")
    print('---------------------------')
    print(f"- Score: {v2_score3}")
    print(f"- {v2_passage3}: {v2_text3}")
    print(f"- Interpretación: {v2_inter3}")
    print('---------------------------')
    return

def verse_recommender_brief_comparison(prayer, emb_model='text-embedding-3-small', limit=130):
    '''Function to recommend Bible verses based on a prayer and generate a response using ChatGPT
    Indexes: bible-verses-metadata and bible-verses-metadata-v2
    Args:
    prayer (str): The prayer text
    gpt_model (str): The ChatGPT model to use for generating the response
    emb_model (str): The text embedding model to use for generating the embeddings
    temperature (float): The temperature to use for generating the response
    top_p (float): The top_p value to use for generating the response
    limit (int): The character limit for each line in the response
    '''
    # Function to process the output of the Vector search and generate a prompt for ChatGPT to generate the final output for the user
    prayer = flatten_text(prayer)
    embedded_prayer = get_embedding(prayer,emb_model)
    query_result_v1 = index_v1.query(vector=embedded_prayer,
                                  top_k=3,
                                  namespace='content',
                                  include_metadata=True)
    # Splitting the results of the search
    v1_score1 = query_result_v1['matches'][0]['score']
    v1_score2 = query_result_v1['matches'][1]['score']
    v1_score3 = query_result_v1['matches'][2]['score']
    v1_passage1 = query_result_v1['matches'][0]['metadata']['pasaje']
    v1_passage2 = query_result_v1['matches'][1]['metadata']['pasaje']
    v1_passage3 = query_result_v1['matches'][2]['metadata']['pasaje']
    v1_text1 = format_text_with_line_breaks(query_result_v1['matches'][0]['metadata']['texto'],limit)
    v1_text2 = format_text_with_line_breaks(query_result_v1['matches'][1]['metadata']['texto'],limit)
    v1_text3 = format_text_with_line_breaks(query_result_v1['matches'][2]['metadata']['texto'],limit)

    query_result_v2 = index_v2.query(vector=embedded_prayer,
                                     top_k=3,
                                     namespace='content',
                                     include_metadata=True)
    
    v2_score1 = query_result_v2['matches'][0]['score']
    v2_score2 = query_result_v2['matches'][1]['score']
    v2_score3 = query_result_v2['matches'][2]['score']
    v2_passage1 = query_result_v2['matches'][0]['metadata']['pasaje']
    v2_passage2 = query_result_v2['matches'][1]['metadata']['pasaje']
    v2_passage3 = query_result_v2['matches'][2]['metadata']['pasaje']
    v2_text1 = format_text_with_line_breaks(query_result_v2['matches'][0]['metadata']['texto'],limit)
    v2_text2 = format_text_with_line_breaks(query_result_v2['matches'][1]['metadata']['texto'],limit)
    v2_text3 = format_text_with_line_breaks(query_result_v2['matches'][2]['metadata']['texto'],limit)
    prayer_break = format_text_with_line_breaks(prayer, limit)
    print('---------------------------')
    print(f'Oración: {prayer_break}')
    print('---------------------------')
    print('Primeros pasajes recomendados')
    print('---------------------------')
    print(f"- Pasaje 1 - v1 - Score: {v1_score1}")
    print(f"- {v1_passage1}: {v1_text1}")
    print('---------------------------')
    print(f"- Pasaje 1 - v2 - Score: {v2_score1}")
    print(f"- {v2_passage1}: {v2_text1}")
    print('---------------------------')
    print('Segundos pasajes recomendados')
    print('---------------------------')
    print(f"- Pasaje 2 - v1 - Score: {v1_score2}")
    print(f"- {v1_passage2}: {v1_text2}")
    print('---------------------------')
    print(f"- Pasaje 2 - v2 - Score: {v2_score2}")
    print(f"- {v2_passage2}: {v2_text2}")
    print('---------------------------')
    print('Terceros pasajes recomendados')
    print('---------------------------')
    print(f"- Pasaje 3 - v1 - Score: {v1_score3}")
    print(f"- {v1_passage3}: {v1_text3}")
    print('---------------------------')
    print(f"- Pasaje 3 - v2 - Score: {v2_score3}")
    print(f"- {v2_passage3}: {v2_text3}")
    print('---------------------------')
    return