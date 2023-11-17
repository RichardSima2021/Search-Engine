
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

# def search(query, inverted_index):
#     print(f"Im looking for: {query}")
#     query = query.lower()
#     if query in inverted_index:
#         result_documents = inverted_index[query]
#         print(f"Found in documents: {result_documents}")
#         return result_documents
#         urls = [document_mapping.get(doc_id, f"URL not found for document {doc_id}") for doc_id in doc_ids]
#         print(f"Corresponding URLs: {urls}")
#     else:
#         print("Not found in any documents.")
#         return []


# def search(query, inverted_index, document_mapping):
#     print(f"Im looking for: {query}")
#     query = query.lower()
#     if query in inverted_index:
#         doc_ids = inverted_index[query]
#         print(f"Found in documents: {doc_ids}")

#         # Retrieve and display the URLs associated with the document IDs
#         urls = [document_mapping.get(doc_id, f"URL not found for document {doc_id}") for doc_id in doc_ids]
#         print(f"Corresponding URLs: {urls}")
#     else:
#         print("Query not found in the inverted index.")


import math

def calculate_tf_idf(document_freq, total_documents):
    tf = document_freq / total_documents
    idf = math.log10(total_documents / document_freq)
    return tf * idf

def search(query, inverted_index, document_mapping):
    print(f"Searching for: {query}")
    query_words = query.lower().split()
    results = []
    # Search for each word in the query
    for word in query_words:
        if word in inverted_index:
            doc_ids = inverted_index[word]
            print(f"not sorted:{doc_ids} ")
            urls = [document_mapping.get(doc_id, f"URL not found for document {doc_id}") for doc_id in doc_ids]
            print(f"each URLs: {urls}")
            results.append(doc_ids)
            # Calculate TF-IDF scores and store in the results list
            for doc_id in doc_ids:
                count = doc_ids.count(doc_id)
                tf_idf_score = calculate_tf_idf(count, len(doc_ids))
                print(f"score:{tf_idf_score} ")
                results.append((doc_id, tf_idf_score))

    
    
    if results:
        # # Sort the results based on TF-IDF scores in descending order
        results.sort(key=lambda x: x[1], reverse=True)

        # # Extract the top 5 document IDs
        top_doc_ids = [result[0] for result in results[:5]]
       
        print(f"Found in documents: {top_doc_ids}")

        # Retrieve and display the URLs associated with the top document IDs
        urls = [document_mapping.get(doc_id, f"URL not found for document {doc_id}") for doc_id in top_doc_ids]
        print(f"Corresponding URLs: {urls}")
    else:
        print("Query not found in the inverted index.")

