
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
    compare = []

    if query_words[0] in inverted_index:
        compare = inverted_index[query_words[0]]
    else:
        compare = []
    
    for word in query_words[1:]:
        if word in inverted_index:
            doc_ids = inverted_index[word]
            compare = list(set(compare) & set(doc_ids))



    # Search for each word in the query
    for word in query_words:
        if word in inverted_index:
            doc_ids = inverted_index[word]
            print(f"not sorted:{doc_ids} ")
            urls = [document_mapping.get(doc_id, f"URL not found for document {doc_id}") for doc_id in doc_ids]
            print(f"each URLs: {urls}")
          
            # results.append(doc_ids)
            # Calculate TF-IDF scores and store in the results list
            
            for doc_id in doc_ids:
                if doc_id in compare:
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

def search(query, inverted_index, document_mapping):
    print(f"Searching for: {query}")
    query_words = query.lower().split()
    results = []
    compare = []
    unique_results = []
    unique_id=set()

 # Initialize compare with the first word's doc_ids if it exists in the inverted_index
    if query_words and query_words[0] in inverted_index:
        compare = set(inverted_index[query_words[0]])

    # Update compare by finding the common doc_ids for the remaining words in the query
    for word in query_words[1:]:
        if word in inverted_index:
            doc_ids = set(inverted_index[word])
            compare = compare.intersection(doc_ids)

    # Search for each word in the query
    for word in query_words:
        if word in inverted_index:
            seen_ids = set()
            doc_ids = inverted_index[word]
            print(f"not sorted:{doc_ids} ")
            urls = [document_mapping.get(doc_id, f"URL not found for document {doc_id}") for doc_id in doc_ids]
            print(f"each URLs: {urls}")
          
            # Calculate TF-IDF scores and store in the results list
            for doc_id in doc_ids:             
                count = doc_ids.count(doc_id)
                tf_idf_score = calculate_tf_idf(count, len(doc_ids))
                print(f"score:{tf_idf_score} ")
                if doc_id not in seen_ids:
                    seen_ids.add(doc_id)
                    results.append((doc_id, tf_idf_score))
                
            print(f"result 1 {results}")
  
    #unique results are unique doc ids that are present in all quey words and the score for the doc_is is the scores of all words added

    for result in results:
        doc_id = result[0]
        score = result[1]
        if doc_id in compare:
            if doc_id not in unique_id:
                unique_id.add(doc_id)
                unique_results.append((doc_id, score))
            else:
                for i, (existing_doc_id, existing_score) in enumerate(unique_results):
                    if existing_doc_id == doc_id:
                        new = float(existing_score)+float(score)
                        unique_results[i] = (existing_doc_id, new)
                        break

    print(f"result combine {unique_results}")

    if unique_results:
        # Sort the results based on TF-IDF scores in descending order
        unique_results.sort(key=lambda x: x[1], reverse=True)

        # Extract the top 5 document IDs
        top_doc_ids = [result[0] for result in unique_results[:5]]
       
        print(f"Found in documents: {top_doc_ids}")

        # Retrieve and display the URLs associated with the top document IDs
        urls = [document_mapping.get(doc_id, f"URL not found for document {doc_id}") for doc_id in top_doc_ids]
        print(f"Corresponding URLs: {urls}")
    else:
        print("Query not found in the inverted index.")
