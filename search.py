
import ast
import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

#: returned a dictionary of the inverted index 
def read_inverted_index(file_path):
    print(f"File Path: {file_path}")
    inverted_index = {}
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            word, ids_str = line.strip().split('\t')
            doc_ids = ast.literal_eval(ids_str)
            inverted_index[word] = doc_ids
    return inverted_index

def read_inverted_index_position(file_path):
    print(f"File Path: {file_path}")
    phrase_position_map = {}
    with open(file_path, 'r', encoding='utf-8') as file:
        position = file.tell()
        line = file.readline()
        while line:
            word, positions_str = line.strip().split('\t')
            phrase_position_map[word] = position
            # Move the file pointer to the next line and update the position
            position = file.tell()
            line = file.readline()
    return phrase_position_map


import math

def calculate_tf_idf(document_freq, total_documents):
    tf = document_freq / total_documents
    idf = math.log10(total_documents / document_freq)
    return tf * idf



def search(query, inverted_index, document_mapping, file_path):
    query_words = query.split()
    query_words = [word.lower() for word in query_words]
    
    # document IDs and occurrences for each word in the query
    result_dict = {}
    total_id=0
    if len(query_words) > 2:
        query_words = [word for word in query_words if word.lower() not in stop_words]


    # Iterate through each word in the query
    with open(file_path, 'r', encoding = 'utf-8') as file:
        for word in query_words:
            if word in inverted_index:
                file.seek(inverted_index[word])
                line = file.readline()
                word, ids_str = line.strip().split('\t')
                doc_ids = ast.literal_eval(ids_str)

                for doc_id in doc_ids: 
                    total_id +=1
                    if doc_id not in result_dict:
                        result_dict[doc_id] = 1
                    else:
                        # Increment the count for the current doc_id
                        result_dict[doc_id] += 1


    scores = {}
    for doc_id, doc_counts in result_dict.items():
        tf_idf_score = calculate_tf_idf(doc_counts, total_id)
        scores[doc_id] = tf_idf_score
    
    sorted_doc_ids = sorted(scores, key=scores.get, reverse=True)

    for i in range(min(5, len(sorted_doc_ids))):
        doc_id = sorted_doc_ids[i]
        score = scores[doc_id]
        urls = [document_mapping.get(doc_id, f"URL not found for document {doc_id}")]
        print(f"Rank: {i}, Url: {urls}")



        