import ast
from collections import Counter, defaultdict
import string
import nltk
from nltk.corpus import stopwords
import math

nltk.download('averaged_perceptron_tagger')
from nltk.stem import PorterStemmer

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

# Function to read the inverted index from a file
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

# Function to calculate the TF-IDF score
def calculate_tf_idf(a, b, c, d, term_weight=1.0):
    tf = a / b
    idf = math.log10(c / d)
    return tf * idf * term_weight



# Function to perform a search using a list of query words
def search(query_words, inverted_index, document_mapping, document_length_mapping, file_path):
    # query_words = word_tokenize(query)
    ps = PorterStemmer()
    # spell = SpellChecker()
    all_stop_words = False

    # stop word checking
    if all(word in stop_words for word in query_words):
        all_stop_words = True
        temp_words = {word for word in query_words}
        if len(query_words) < 4:
            temp = []
            temp.append(temp_words.pop())
            query_words = temp
        else:
            query_words = temp_words
    else:
        query_words = [word for word in query_words if word.lower() not in stop_words]


    # stem words
    query_stem_words = {ps.stem(word) for word in query_words}

    result_dict = {}
    total_id = 0
    common_doc_ids = set()  # Initialize an empty set for common document IDs
    total_documents = len(document_mapping)
    # Open the file to search for query words
    with open(file_path, 'r', encoding='utf-8') as file:
        for word in query_stem_words:
            if word in inverted_index:
                # Move the file pointer to the position of the word in the index file
                file.seek(inverted_index[word])
                line = file.readline()
                word, ids_str = line.strip().split('\t')
                # Parse document IDs from the inverted index file
                if not all_stop_words:
                    doc_ids = [int(part.strip()) for part in ids_str[1:-1].split(',') if part.strip()]
                else:
                    doc_ids = set(int(part.strip()) for part in ids_str[1:-1].split(',') if part.strip())
                # Update common_doc_ids based on the intersection of current doc_ids
                if not common_doc_ids:
                    # If common_doc_ids is empty, add all document IDs for the first word
                    common_doc_ids.update(doc_ids)
                else:
                    # Update common_doc_ids with the intersection of current doc_ids
                    common_doc_ids.intersection_update(doc_ids)
                # Update result_dict with document counts
                for doc_id in doc_ids:
                    total_id += 1
                    result_dict[doc_id] = result_dict.get(doc_id, 0) + 1

    scores = {}
    # Calculate TF-IDF scores for each document
    for doc_id, doc_counts in result_dict.items():
        # Introduce a bonus score for documents containing all query words
        all_words_term = 2.0 if doc_id in common_doc_ids else 1.0
        word_in_doc_str = document_length_mapping.get(doc_id, f"word count not found for document {doc_id}")
        word_in_doc = int(word_in_doc_str) if word_in_doc_str.isdigit() else 0

        #    print(f"Before calculation - doc_id: {doc_id}, doc_counts: {doc_counts}, word_in_doc: {word_in_doc}, total_documents: {total_documents}, total_id: {total_id}, all_words_term: {all_words_term}")

        tf_idf_score = calculate_tf_idf(doc_counts, word_in_doc, total_documents, total_id, all_words_term)

        scores[doc_id] = tf_idf_score

    # Sort document IDs based on scores in descending order
    sorted_doc_ids = sorted(scores, key=scores.get, reverse=True)
    # Select the top 5 unique URLs with their scores
    unique_urls = set()
    unique_urls_printed = 0
    result = {}

    total_score = 0
    for i in range(len(sorted_doc_ids)):
        if unique_urls_printed >= 5:
            break
        doc_id = sorted_doc_ids[i]
        score = scores[doc_id]
        url = document_mapping.get(doc_id, f"URL not found for document {doc_id}")

        if url not in unique_urls:
            unique_urls.add(url)
            # print(f"Rank: {unique_urls_printed + 1}, URL: {url}, Score: {score}")
            unique_urls_printed += 1
            result[unique_urls_printed] = (url, score)
            total_score += score

    return (result, total_score/5)
