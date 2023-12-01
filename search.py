import ast
from collections import Counter
import nltk
from nltk.corpus import stopwords
import math
nltk.download('averaged_perceptron_tagger')
from nltk.stem import PorterStemmer
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))
from spellchecker import SpellChecker
import time
import re
from nltk.tokenize import word_tokenize

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



def calculate_tf_idf(document_freq, total_documents, term_weight=1.0):
   tf = document_freq / total_documents
   idf = math.log10(total_documents / document_freq)
   return tf * idf * term_weight




# def determine_important_words(query):
#     stop_words = set(stopwords.words('english'))
#     ps = PorterStemmer()
    
#     words = query.split()
#     important_words = {ps.stem(word.lower()) for word in words if word.lower() not in stop_words}
    
#     return important_words



def search(query, inverted_index, document_mapping, file_path):
   query_words = word_tokenize(query)
   ps = PorterStemmer()
   spell = SpellChecker()
   query_words = {spell.correction(word.lower()) if len(word) > 3 else word.lower() for word in query_words}

   

   if len(query_words) > 2:
       if all(word in stop_words for word in query_words):
          all_stop_words = True
          temp_words = {word for word in query_words}
          query_words = temp_words
       else:
           query_words = [word for word in query_words if word.lower() not in stop_words]

   
    # Initialize SpellChecker
   

    # Correct spelling for words in query_words
   corrected_words = {ps.stem(word) for word in query_words}

   


  # important_words = determine_important_words(query)
   print(f" query_words after correction: {corrected_words }")

   result_dict = {}
   total_id = 0
   common_doc_ids = set()  # Initialize an empty set for common document IDs


      
   with open(file_path, 'r', encoding='utf-8') as file:
       for word in corrected_words:
           if word in inverted_index:
               file.seek(inverted_index[word])
  
               line = file.readline()

               word, ids_str = line.strip().split('\t')

               doc_ids = [int(part) for part in re.split(r'\D+', ids_str) if part]
    

               if not common_doc_ids:
                    # If common_doc_ids is empty, add all document IDs for the first word
                    common_doc_ids.update(doc_ids)
               else:
                    # Update common_doc_ids with the intersection of current doc_ids
                    common_doc_ids.intersection_update(doc_ids)
               for doc_id in doc_ids:
                    total_id += 1
                    result_dict[doc_id] = result_dict.get(doc_id, 0) + 1


   scores = {}
   for doc_id, doc_counts in result_dict.items():

       # Introduce a score for documents containing all query words
       all_words_term = 1.2 if doc_id in common_doc_ids else 1.0

       tf_idf_score = calculate_tf_idf(doc_counts, total_id, all_words_term)

       scores[doc_id] = tf_idf_score


   sorted_doc_ids = sorted(scores, key=scores.get, reverse=True)


   unique_urls = set()
   unique_urls_printed = 0


   for i in range(len(sorted_doc_ids)):
       if unique_urls_printed >= 5:
           break
       doc_id = sorted_doc_ids[i]
       score = scores[doc_id]
       url = document_mapping.get(doc_id, f"URL not found for document {doc_id}")


       if url not in unique_urls:
           unique_urls.add(url)
           print(f"Rank: {unique_urls_printed + 1}, URL: {url}, Score: {score}")
           unique_urls_printed += 1

