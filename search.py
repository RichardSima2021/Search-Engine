
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

def search(query, inverted_index):
    print(f"Im looking for: {query}")
    query = query.lower()
    if query in inverted_index:
        result_documents = inverted_index[query]
        print(f"Found in documents: {result_documents}")
        return result_documents
        urls = [document_mapping.get(doc_id, f"URL not found for document {doc_id}") for doc_id in doc_ids]
        print(f"Corresponding URLs: {urls}")
    else:
        print("Not found in any documents.")
        return []


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


