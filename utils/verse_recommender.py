from utils.text_utils import flatten_text, format_text_with_line_breaks
from utils.similarity_utils import similarity
from utils.openai_utils import get_embedding, get_completion
from utils.pinecone_utils import pc_client

# Setting the indexes for the old and new versions of the Bible verses metadata
#index_openai_small = pc_client.Index(index_name='bible-verses-openai-small', host='https://bible-verses-openai-small-rsup9mo.svc.aped-4627-b74a.pinecone.io')
#index_openai_large = pc_client.Index(index_name='bible-verses-openai-large', host='https://bible-verses-openai-large-rsup9mo.svc.aped-4627-b74a.pinecone.io')

def verse_recommender_openai(prayer,version='v1',top_k=3, temperature=1, top_p=1, limit=130):
    '''Function to recommend Bible verses based on a prayer and generate a response using ChatGPT
    Index: bible-verses-openai-small
    Args:
    prayer (str): The prayer text
    version (str): The version of the index to use for the search. Can be v1 or v2.
    top_k (int): The number of results to return from the search
    temperature (float): The temperature to use for generating the response
    top_p (float): The top_p value to use for generating the response
    limit (int): The character limit for each line in the response
    '''
    gpt_model = 'gpt-4o'
    # Validating which version to use
    if version == 'v1':
        emb_model = 'text-embedding-3-small'
        index_name = 'bible-verses-openai-small'
        host = 'https://bible-verses-openai-small-rsup9mo.svc.aped-4627-b74a.pinecone.io'
        namespace = 'v1'
    elif version == 'v2':
        emb_model = 'text-embedding-3-small'
        index_name = 'bible-verses-openai-small'
        host = 'https://bible-verses-openai-small-rsup9mo.svc.aped-4627-b74a.pinecone.io'
        namespace = 'v2'
    elif version == 'v3':
        emb_model = 'text-embedding-3-large'
        index_name = 'bible-verses-openai-large'
        host='https://bible-verses-openai-large-rsup9mo.svc.aped-4627-b74a.pinecone.io'
        namespace = 'v3'
    else: 
        raise ValueError('Invalid version. Please choose v1, v2, or v3')
    # Function to process the output of the Vector search and generate a prompt for ChatGPT to generate the final output for the user
    prayer = flatten_text(prayer)
    embedded_prayer = get_embedding(prayer,emb_model)
    index = pc_client.Index(index_name=index_name, host=host)
    query_result =index.query(vector=embedded_prayer,
                                  top_k=top_k,
                                  namespace=version,
                                  include_metadata=True)
    # Storing the result in lists
    scores = []
    passages = []
    texts = []
    interpretations = []
    for i in range(top_k):
        scores.append(query_result['matches'][i]['score'])
        passages.append(query_result['matches'][i]['metadata']['pasaje'])
        texts.append(query_result['matches'][i]['metadata']['texto'])
        interpretations.append(query_result['matches'][i]['metadata']['interpretacion'])
    
    results_string = f"    # Input #\n    - Oración: {prayer}\n"
    for i in range(top_k):
        results_string += f"    - Pasaje de la Biblia {i+1}: {passages[i]} : {texts[i]}\n"
    
    results_string += "    # fin Input #"

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
                - Pasaje de la Biblia k
                # Fin estructura input #

                {results_string}

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
        # Applying function to format the text with line breaks
    passages = list(map(lambda x: format_text_with_line_breaks(x, limit), passages))
    texts = list(map(lambda x: format_text_with_line_breaks(x, limit), texts))
    interpretations = list(map(lambda x: format_text_with_line_breaks(x, limit), interpretations))
    # Printing the results
    print('Pasajes recomendados')
    for i in range(top_k):
        print('---------------------------')
        print(f"- Score{i+1}: {scores[i]}")
        print(f"- {passages[i]}: {texts[i]}")
        #print(f"- Interpretación: {interpretations[i]}")
    print('---------------------------')
    print('Output Orare')
    print('---------------------------')
    print(f'Oración: {prayer_break}')
    print('---------------------------')
    print(response_break)
    return


def verse_recommender_comparison(prayer, top_k=3, limit=130):
    '''Function to recommend Bible verses based on a prayer and generate a response using ChatGPT
    Index: bible-verses-openai-small
    Args:
    prayer (str): The prayer text
    top_k (int): The number of results to return from the search
    limit (int): The character limit for each line in the response
    '''
    # Function to process the output of the Vector search and generate a prompt for ChatGPT to generate the final output for the user
    prayer = flatten_text(prayer)
    # Search function for v2
    embedded_prayer_v2 = get_embedding(prayer,'text-embedding-3-small')
    index_v2 = pc_client.Index(index_name='bible-verses-openai-small', 
                               host='https://bible-verses-openai-small-rsup9mo.svc.aped-4627-b74a.pinecone.io')
    query_result_v2 =index_v2.query(vector=embedded_prayer_v2,
                                  top_k=top_k,
                                  namespace='v2',
                                  include_metadata=True)
    # Storing the result in lists
    scores_v2 = []
    passages_v2 = []
    texts_v2 = []
    interpretations_v2 = []
    for i in range(top_k):
        scores_v2.append(query_result_v2['matches'][i]['score'])
        passages_v2.append(query_result_v2['matches'][i]['metadata']['pasaje'])
        texts_v2.append(query_result_v2['matches'][i]['metadata']['texto'])
        interpretations_v2.append(query_result_v2['matches'][i]['metadata']['interpretacion'])

    # Search function for v3
    embedded_prayer_v3 = get_embedding(prayer,'text-embedding-3-large')
    index_v3 = pc_client.Index(index_name='bible-verses-openai-large', 
                               host='https://bible-verses-openai-large-rsup9mo.svc.aped-4627-b74a.pinecone.io')
    query_result_v3 =index_v3.query(vector=embedded_prayer_v3,
                                  top_k=top_k,
                                  namespace='v3',
                                  include_metadata=True)
    # Storing the result in lists
    scores_v3 = []
    passages_v3 = []
    texts_v3 = []
    interpretations_v3 = []
    for i in range(top_k):
        scores_v3.append(query_result_v3['matches'][i]['score'])
        passages_v3.append(query_result_v3['matches'][i]['metadata']['pasaje'])
        texts_v3.append(query_result_v3['matches'][i]['metadata']['texto'])
        interpretations_v3.append(query_result_v3['matches'][i]['metadata']['interpretacion'])
    
    # Formatting the output
    prayer_break = format_text_with_line_breaks(prayer, limit)
    passages_v2 = list(map(lambda x: format_text_with_line_breaks(x, limit), passages_v2))
    texts_v2 = list(map(lambda x: format_text_with_line_breaks(x, limit), texts_v2))
    interpretations_v2 = list(map(lambda x: format_text_with_line_breaks(x, limit), interpretations_v2))
    passages_v3 = list(map(lambda x: format_text_with_line_breaks(x, limit), passages_v3))
    texts_v3 = list(map(lambda x: format_text_with_line_breaks(x, limit), texts_v3))
    interpretations_v3 = list(map(lambda x: format_text_with_line_breaks(x, limit), interpretations_v3))
    # Printing the results
    print(f'Oración: {prayer_break}')
    print('---------------------------')
    print('Pasajes recomendados')
    print('---------------------------')
    for i in range(top_k):
        print(f" Recomendación: {i+1}")
        print(f"- v2 - Score{i+1}: {scores_v2[i]}")
        print(f"- v2 - {passages_v2[i]}: {texts_v2[i]}")
        print(f"- v3 - Score{i+1}: {scores_v3[i]}")
        print(f"- v3 - {passages_v3[i]}: {texts_v3[i]}")
        print('---------------------------')
        #print(f"- Interpretación: {interpretations[i]}")
    return