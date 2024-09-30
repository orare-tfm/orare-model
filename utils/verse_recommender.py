from utils.text_utils import flatten_text, format_text_with_line_breaks
from utils.similarity_utils import similarity
from utils.openai_utils import get_embedding, get_completion
from utils.pinecone_utils import pc_client
from utils.voyageai_utils import get_embedding_voyageai

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


def verse_recommender_emb_comparison(prayer,bible_int='openai', top_k=3, limit=130):
    '''Function to recommend Bible verses based on a prayer and generate a response using ChatGPT
    Index: bible-verses-openai-small
    Args:
    prayer (str): The prayer text
    bible_int (str): Interpretation of the Bible: openai or anthropic
    top_k (int): The number of results to return from the search
    limit (int): The character limit for each line in the response
    '''
    # Function to process the output of the Vector search and generate a prompt for ChatGPT to generate the final output for the user
    prayer = flatten_text(prayer)
    # Search function for v3
    embedded_prayer_openai = get_embedding(prayer,'text-embedding-3-large')
    embedded_prayer_voyageai = get_embedding_voyageai(prayer)

    if bible_int == 'openai':
        namespace = 'v3-openai'
    elif bible_int == 'anthropic':
        namespace = 'v3-claude'
    else:
        raise ValueError('Invalid version. Please choose openai or anthropic')
    
    # Seraching through the indexes
    index_emb_openai = pc_client.Index(index_name='bible-verses-openai-large', 
                            host='https://bible-verses-openai-large-rsup9mo.svc.aped-4627-b74a.pinecone.io')
    query_result_emb_openai =index_emb_openai.query(vector=embedded_prayer_openai,
                                top_k=top_k,
                                namespace=namespace,
                                include_metadata=True)
    index_emb_voyage = pc_client.Index(index_name='bible-verses-voyageai',
                                        host='https://bible-verses-voyage-rsup9mo.svc.aped-4627-b74a.pinecone.io')
    query_result_emb_voyage = index_emb_voyage.query(vector=embedded_prayer_voyageai,
                                top_k=top_k,
                                namespace=namespace,
                                include_metadata=True)
                               
    # Storing the result: OpenAI embeddings
    scores_openai = []
    passages_openai = []
    texts_openai = []
    interpretations_openai = []
    for i in range(top_k):
        scores_openai.append(query_result_emb_openai['matches'][i]['score'])
        passages_openai.append(query_result_emb_openai['matches'][i]['metadata']['pasaje'])
        texts_openai.append(query_result_emb_openai['matches'][i]['metadata']['texto'])
        interpretations_openai.append(query_result_emb_openai['matches'][i]['metadata']['interpretacion'])

    # Storing the result: Voyage embeddings
    scores_voyage = []
    passages_voyage = []
    texts_voyage = []
    interpretations_voyage = []
    for i in range(top_k):
        scores_voyage.append(query_result_emb_voyage['matches'][i]['score'])
        passages_voyage.append(query_result_emb_voyage['matches'][i]['metadata']['pasaje'])
        texts_voyage.append(query_result_emb_voyage['matches'][i]['metadata']['texto'])
        interpretations_voyage.append(query_result_emb_voyage['matches'][i]['metadata']['interpretacion'])
    
    # Formatting the output
    prayer_break = format_text_with_line_breaks(prayer, limit)
    passages_openai = list(map(lambda x: format_text_with_line_breaks(x, limit), passages_openai))
    texts_openai = list(map(lambda x: format_text_with_line_breaks(x, limit), texts_openai))
    interpretations_openai = list(map(lambda x: format_text_with_line_breaks(x, limit), interpretations_openai))
    passages_voyage = list(map(lambda x: format_text_with_line_breaks(x, limit), passages_voyage))
    texts_voyage = list(map(lambda x: format_text_with_line_breaks(x, limit), texts_voyage))
    interpretations_voyage = list(map(lambda x: format_text_with_line_breaks(x, limit), interpretations_voyage))
    # Printing the results
    print(f'Oración: {prayer_break}')
    print('---------------------------')
    print('Pasajes recomendados')
    print('---------------------------')
    for i in range(top_k):
        print(f" Recomendación: {i+1}")
        print(f"- openai emb - Score{i+1}: {scores_openai[i]}")
        print(f"- openai emb - {passages_openai[i]}: {texts_openai[i]}")
        print(f"- voyage emb - Score{i+1}: {scores_voyage[i]}")
        print(f"- voyage emb - {passages_voyage[i]}: {texts_voyage[i]}")
        print('---------------------------')
        #print(f"- Interpretación: {interpretations[i]}")
    return


def verse_recommender_openai_anthropic_comparison(prayer, top_k=3, limit=130):
    '''Function to recommend Bible verses based on a prayer and generate a response using ChatGPT
    Index: bible-verses-openai-small
    Args:
    prayer (str): The prayer text
    bible_int (str): Interpretation of the Bible: openai or anthropic
    top_k (int): The number of results to return from the search
    limit (int): The character limit for each line in the response
    '''
    # Function to process the output of the Vector search and generate a prompt for ChatGPT to generate the final output for the user
    prayer = flatten_text(prayer)
    # Search function for v3
    embedded_prayer = get_embedding(prayer,'text-embedding-3-large')
    
    # Seraching through the indexes
    index = pc_client.Index(index_name='bible-verses-openai-large',
                            host='https://bible-verses-openai-large-rsup9mo.svc.aped-4627-b74a.pinecone.io')
    query_result_openai =index.query(vector=embedded_prayer,
                                top_k=top_k,
                                namespace='v3-openai',
                                include_metadata=True)
    query_result_anthropic = index.query(vector=embedded_prayer,
                                top_k=top_k,
                                namespace='v3-claude',
                                include_metadata=True)
                               
    # Storing the result: OpenAI embeddings
    scores_openai = []
    passages_openai = []
    texts_openai = []
    interpretations_openai = []
    for i in range(top_k):
        scores_openai.append(query_result_openai['matches'][i]['score'])
        passages_openai.append(query_result_openai['matches'][i]['metadata']['pasaje'])
        texts_openai.append(query_result_openai['matches'][i]['metadata']['texto'])
        interpretations_openai.append(query_result_openai['matches'][i]['metadata']['interpretacion'])
    avg_score_openai = sum(scores_openai)/len(scores_openai)

    # Storing the result: Voyage embeddings
    scores_anthropic = []
    passages_anthropic = []
    texts_anthropic = []
    interpretations_anthropic = []
    for i in range(top_k):
        scores_anthropic.append(query_result_anthropic['matches'][i]['score'])
        passages_anthropic.append(query_result_anthropic['matches'][i]['metadata']['pasaje'])
        texts_anthropic.append(query_result_anthropic['matches'][i]['metadata']['texto'])
        interpretations_anthropic.append(query_result_anthropic['matches'][i]['metadata']['interpretacion'])
    avg_score_anthropic = sum(scores_anthropic)/len(scores_anthropic)
    
    # Formatting the output
    prayer_break = format_text_with_line_breaks(prayer, limit)
    passages_openai = list(map(lambda x: format_text_with_line_breaks(x, limit), passages_openai))
    texts_openai = list(map(lambda x: format_text_with_line_breaks(x, limit), texts_openai))
    interpretations_openai = list(map(lambda x: format_text_with_line_breaks(x, limit), interpretations_openai))
    passages_anthropic = list(map(lambda x: format_text_with_line_breaks(x, limit), passages_anthropic))
    texts_anthropic = list(map(lambda x: format_text_with_line_breaks(x, limit), texts_anthropic))
    interpretations_anthropic = list(map(lambda x: format_text_with_line_breaks(x, limit), interpretations_anthropic))
    # Printing the results
    print(f'Oración: {prayer_break}')
    print('---------------------------')
    print('Pasajes recomendados')
    print('---------------------------')
    for i in range(top_k):
        print(f" Recomendación: {i+1}")
        print(f"- OpenAI - Score: {scores_openai[i]}")
        print(f"- {passages_openai[i]}: {texts_openai[i]}")
        print(f"- Anthropic - Score: {scores_anthropic[i]}")
        print(f"- {passages_anthropic[i]}: {texts_anthropic[i]}")
        print('---------------------------')
        #print(f"- Interpretación: {interpretations[i]}")
    return avg_score_openai, avg_score_anthropic


def verse_recommender_emb_score_comparison(prayer, top_k=5, limit=130):
    '''Function to recommend Bible verses based on a prayer and generate a response using ChatGPT
    Index: bible-verses-openai-small
    Args:
    prayer (str): The prayer text
    bible_int (str): Interpretation of the Bible: openai or anthropic
    top_k (int): The number of results to return from the search
    limit (int): The character limit for each line in the response
    '''
    # Function to process the output of the Vector search and generate a prompt for ChatGPT to generate the final output for the user
    prayer = flatten_text(prayer)
    # Search function for v3
    embedded_prayer_openai_large = get_embedding(prayer,'text-embedding-3-large')
    embedded_prayer_openai_small = get_embedding(prayer,'text-embedding-3-small')
    embedded_prayer_voyageai = get_embedding_voyageai(prayer)
    
    # Seraching through the indexes
    index_emb_openai_large = pc_client.Index(index_name='bible-verses-openai-large', 
                            host='https://bible-verses-openai-large-rsup9mo.svc.aped-4627-b74a.pinecone.io')
    query_result_emb_openai_large =index_emb_openai_large.query(vector=embedded_prayer_openai_large,
                                top_k=top_k,
                                namespace='v3-openai',
                                include_metadata=True)
    index_emb_openai_small = pc_client.Index(index_name='bible-verses-openai-small', 
                            host='https://bible-verses-openai-small-rsup9mo.svc.aped-4627-b74a.pinecone.io')
    query_result_emb_openai_small =index_emb_openai_small.query(vector=embedded_prayer_openai_small,
                                top_k=top_k,
                                namespace='v3-openai',
                                include_metadata=True)
    index_emb_voyage = pc_client.Index(index_name='bible-verses-voyageai',
                                        host='https://bible-verses-voyage-rsup9mo.svc.aped-4627-b74a.pinecone.io')
    query_result_emb_voyage = index_emb_voyage.query(vector=embedded_prayer_voyageai,
                                top_k=top_k,
                                namespace='v3-openai',
                                include_metadata=True)
                               
    # Storing the result: OpenAI embeddings - Large
    scores_openai_large = []
    passages_openai_large = []
    texts_openai_large = []
    interpretations_openai_large = []
    for i in range(top_k):
        scores_openai_large.append(query_result_emb_openai_large['matches'][i]['score'])
        passages_openai_large.append(query_result_emb_openai_large['matches'][i]['metadata']['pasaje'])
        texts_openai_large.append(query_result_emb_openai_large['matches'][i]['metadata']['texto'])
        interpretations_openai_large.append(query_result_emb_openai_large['matches'][i]['metadata']['interpretacion'])
    avg_score_openai_large = sum(scores_openai_large)/len(scores_openai_large)
    
    # Storing the result: OpenAI embeddings - Small
    scores_openai_small = []
    passages_openai_small = []
    texts_openai_small = []
    interpretations_openai_small = []
    for i in range(top_k):
        scores_openai_small.append(query_result_emb_openai_small['matches'][i]['score'])
        passages_openai_small.append(query_result_emb_openai_small['matches'][i]['metadata']['pasaje'])
        texts_openai_small.append(query_result_emb_openai_small['matches'][i]['metadata']['texto'])
        interpretations_openai_small.append(query_result_emb_openai_small['matches'][i]['metadata']['interpretacion'])
    avg_score_openai_small = sum(scores_openai_small)/len(scores_openai_small)

    # Storing the result: Voyage embeddings
    scores_voyage = []
    passages_voyage = []
    texts_voyage = []
    interpretations_voyage = []
    for i in range(top_k):
        scores_voyage.append(query_result_emb_voyage['matches'][i]['score'])
        passages_voyage.append(query_result_emb_voyage['matches'][i]['metadata']['pasaje'])
        texts_voyage.append(query_result_emb_voyage['matches'][i]['metadata']['texto'])
        interpretations_voyage.append(query_result_emb_voyage['matches'][i]['metadata']['interpretacion'])
    avg_score_voyage = sum(scores_voyage)/len(scores_voyage)
    
    # Formatting the output
    prayer_break = format_text_with_line_breaks(prayer, limit)
    passages_openai_large = list(map(lambda x: format_text_with_line_breaks(x, limit), passages_openai_large))
    texts_openai_large = list(map(lambda x: format_text_with_line_breaks(x, limit), texts_openai_large))
    interpretations_openai_large = list(map(lambda x: format_text_with_line_breaks(x, limit), interpretations_openai_large))
    passages_openai_small = list(map(lambda x: format_text_with_line_breaks(x, limit), passages_openai_small))
    texts_openai_small = list(map(lambda x: format_text_with_line_breaks(x, limit), texts_openai_small))
    interpretations_openai_small = list(map(lambda x: format_text_with_line_breaks(x, limit), interpretations_openai_small))
    passages_voyage = list(map(lambda x: format_text_with_line_breaks(x, limit), passages_voyage))
    texts_voyage = list(map(lambda x: format_text_with_line_breaks(x, limit), texts_voyage))
    interpretations_voyage = list(map(lambda x: format_text_with_line_breaks(x, limit), interpretations_voyage))
    # Printing the results
    print(f'Oración: {prayer_break}')
    print('---------------------------')
    print(f'Avg Score OpenAI Large: {avg_score_openai_large}')
    print(f'Avg Score OpenAI Small: {avg_score_openai_small}')
    print(f'Avg Score Voyage: {avg_score_voyage}')
    #print('Pasajes recomendados')
    print('---------------------------')
    #for i in range(top_k):
        #print(f" Recomendación: {i+1}")
        #print(f"- openai emb - Score{i+1}: {scores_openai[i]}")
        #print(f"- openai emb - {passages_openai[i]}: {texts_openai[i]}")
        #print(f"- voyage emb - Score{i+1}: {scores_voyage[i]}")
        #print(f"- voyage emb - {passages_voyage[i]}: {texts_voyage[i]}")
        #print('---------------------------')
        #print(f"- Interpretación: {interpretations[i]}")
    #scores = {'openai_large': avg_score_openai_large, 'openai_small': avg_score_openai_small, 'voyage': avg_score_voyage}
    #return scores
    return avg_score_openai_large, avg_score_openai_small, avg_score_voyage


def verse_recommender_openai(prayer, top_k=3, limit=130):
    '''Function to recommend Bible verses based on a prayer and generate a response using ChatGPT
    Index: bible-verses-openai-small
    Args:
    prayer (str): The prayer text
    bible_int (str): Interpretation of the Bible: openai or anthropic
    top_k (int): The number of results to return from the search
    limit (int): The character limit for each line in the response
    '''
    # Function to process the output of the Vector search and generate a prompt for ChatGPT to generate the final output for the user
    prayer = flatten_text(prayer)
    # Search function for v3
    embedded_prayer_openai_large = get_embedding(prayer,'text-embedding-3-large')
    embedded_prayer_openai_small = get_embedding(prayer,'text-embedding-3-small')
    
    # Seraching through the indexes
    index_emb_openai_large = pc_client.Index(index_name='bible-verses-openai-large', 
                            host='https://bible-verses-openai-large-rsup9mo.svc.aped-4627-b74a.pinecone.io')
    query_result_emb_openai_large =index_emb_openai_large.query(vector=embedded_prayer_openai_large,
                                top_k=top_k,
                                namespace='v3-openai',
                                include_metadata=True)
    index_emb_openai_small = pc_client.Index(index_name='bible-verses-openai-small', 
                            host='https://bible-verses-openai-small-rsup9mo.svc.aped-4627-b74a.pinecone.io')
    query_result_emb_openai_small =index_emb_openai_small.query(vector=embedded_prayer_openai_small,
                                top_k=top_k,
                                namespace='v3-openai',
                                include_metadata=True)
                               
    # Storing the result: OpenAI embeddings - Large
    scores_openai_large = []
    passages_openai_large = []
    texts_openai_large = []
    interpretations_openai_large = []
    for i in range(top_k):
        scores_openai_large.append(query_result_emb_openai_large['matches'][i]['score'])
        passages_openai_large.append(query_result_emb_openai_large['matches'][i]['metadata']['pasaje'])
        texts_openai_large.append(query_result_emb_openai_large['matches'][i]['metadata']['texto'])
        interpretations_openai_large.append(query_result_emb_openai_large['matches'][i]['metadata']['interpretacion'])
    avg_score_openai_large = sum(scores_openai_large)/len(scores_openai_large)
    
    # Storing the result: OpenAI embeddings - Small
    scores_openai_small = []
    passages_openai_small = []
    texts_openai_small = []
    interpretations_openai_small = []
    for i in range(top_k):
        scores_openai_small.append(query_result_emb_openai_small['matches'][i]['score'])
        passages_openai_small.append(query_result_emb_openai_small['matches'][i]['metadata']['pasaje'])
        texts_openai_small.append(query_result_emb_openai_small['matches'][i]['metadata']['texto'])
        interpretations_openai_small.append(query_result_emb_openai_small['matches'][i]['metadata']['interpretacion'])
    avg_score_openai_small = sum(scores_openai_small)/len(scores_openai_small)
 
    # Formatting the output
    prayer_break = format_text_with_line_breaks(prayer, limit)
    passages_openai_large = list(map(lambda x: format_text_with_line_breaks(x, limit), passages_openai_large))
    texts_openai_large = list(map(lambda x: format_text_with_line_breaks(x, limit), texts_openai_large))
    interpretations_openai_large = list(map(lambda x: format_text_with_line_breaks(x, limit), interpretations_openai_large))
    passages_openai_small = list(map(lambda x: format_text_with_line_breaks(x, limit), passages_openai_small))
    texts_openai_small = list(map(lambda x: format_text_with_line_breaks(x, limit), texts_openai_small))
    interpretations_openai_small = list(map(lambda x: format_text_with_line_breaks(x, limit), interpretations_openai_small))
    
    # Printing the results
    print(f'Oración: {prayer_break}')
    print('---------------------------')
    print('Pasajes recomendados')
    print('---------------------------')
    for i in range(top_k):
        print(f" Recomendación: {i+1}")
        print(f"- openai large - Score{i+1}: {scores_openai_large[i]}")
        print(f"- openai large - {passages_openai_large[i]}: {texts_openai_large[i]}")
        print(f"- Interpretación: {interpretations_openai_large[i]}")
        print(f"- openai small - Score{i+1}: {scores_openai_small[i]}")
        print(f"- openai small - {passages_openai_small[i]}: {texts_openai_small[i]}")
        print(f"- Interpretación: {interpretations_openai_small[i]}")
        print('---------------------------')
    return avg_score_openai_large, avg_score_openai_small