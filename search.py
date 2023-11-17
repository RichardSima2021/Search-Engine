
import ast

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



import math

def calculate_tf_idf(document_freq, total_documents):
    tf = document_freq / total_documents
    idf = math.log10(total_documents / document_freq)
    return tf * idf



def search(query, inverted_index, document_mapping):
    query_words = query.split()
    
    # document IDs and occurrences for each word in the query
    result_dict = {}
    total_id=0

    # Iterate through each word in the query
    for word in query_words:
        if word in inverted_index:
            doc_ids = inverted_index[word]
            print(f"Word: {word}, ids {doc_ids}")

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
        print(f"Document ID: {doc_id}, Score: {score}")
        urls = [document_mapping.get(doc_id, f"URL not found for document {doc_id}")]
        print(f"Rank: {i}, Url: {urls}")



        
