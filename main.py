from difflib import SequenceMatcher
import os
import glob
import json
import string
from urllib.parse import urlparse, urlunparse
import merge
import search
from bs4 import BeautifulSoup
from nltk.stem import PorterStemmer
import nltk
nltk.download('punkt')
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
nltk.download('stopwords')
import time
from spellchecker import SpellChecker
import psutil


develop = True
unique_words = set()
doc_id = 1
block_id = 1
url_mapping = dict()
url_length_mapping = dict()

# Function to get a list of files in a folder with a file extension
def get_files_in_folder(folder_path, file_extension='json'):
    files = []
    for root, _, filenames in os.walk(folder_path):
        for filename in filenames:
            if filename.endswith(f".{file_extension}"):
                files.append(os.path.join(root, filename))
    return files

# Function to parse a document and extract relevant information
def parse_document(file):
    # print(f"parsing {file}")
    # input()
    data = json.load(file)
    content = data['content']

    if data['encoding'] != 'utf-8' and data['encoding'] != 'ascii':
        return [], '',0

    soup = BeautifulSoup(content, "lxml")
    
    # obtaining important text
    important_text = []
    important_tags = ['b', 'strong', 'h1', 'h2', 'h3', 'title']
    for tag in important_tags:
        elements = soup.find_all(tag)
        for element in elements:
            important_text.append(element.get_text().lower())

    words = soup.get_text().lower()
    for imp_text in important_text:
        words += " " + imp_text
    stopword_set = set(stopwords.words('english'))

    words_list = word_tokenize(words)
    filtered_words_list = [
        w
        for w in words_list
    ]

    url = data['url']

    parsed_url = urlparse(url)
    url_without_fragment = parsed_url._replace(fragment='').geturl()
    word_count = len(filtered_words_list)
    # return filtered_words_list
    return filtered_words_list, url_without_fragment, word_count

# Function to write an index block to a file
def write_block(indices):
    global block_id
    output_file = f'index-blocks/inverted_index-{block_id}.txt'
    sorted_indices = sorted(indices.items(), key=lambda x: x[0])
    with open(output_file, 'w', encoding='utf-8') as output:
        for pair in sorted_indices:
            try:
                output.write(f'{pair}\n')
            except Exception as e:
                print(f'An error occurred while writing, {e}')
    output.close()
    block_id += 1

# Function to check if a new URL is too similar to URLs in a list
def is_similar_url(new_url, url_list, similarity_threshold=0.94):
    for url in url_list:
        # Check if the new URL is too similar to any URL in the list
        if SequenceMatcher(None, new_url, url).ratio() > similarity_threshold:
            return True  # Return True if too similar
    return False  # Return False if not too similar

# Main function to build the inverted index from a folder of JSON documents
def build_index(folder_path):
    global url_mapping
    global url_length_mapping
    inverted_index = dict()
    batch_limit = 2500  # Adjust the batch size as needed (note: 2000)
    current_batch = 1
    global doc_id
    global block_id
    url_list = []
    for file_path in get_files_in_folder(folder_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            file_name = os.path.splitext(os.path.basename(file_path))[0]

            tokens, url, word_count= parse_document(file)
            if not is_similar_url(url, url_list[-min(10, len(url_list)):]):
                url_list.append(url)
                url_list = url_list[-10:]
            else:
                continue

            url_mapping[doc_id] = url
            url_length_mapping[doc_id] = word_count

            if doc_id % 10 == 0:
                print(doc_id, url)

            # this is used to stem the word that to be included into the index
            ps = PorterStemmer()
            for token in tokens:
                token = ps.stem(token.lower())
                if token not in inverted_index:
                    inverted_index[token] = []

                if token not in unique_words:
                    unique_words.add(token)
                inverted_index[token].append(doc_id)


        doc_id += 1
        current_batch += 1

        if current_batch == batch_limit:
            current_batch = 1
            write_block(inverted_index)
            inverted_index.clear()

    if inverted_index:
        write_block(inverted_index)
        inverted_index.clear()

# Function to build the mapping of document IDs to URLs
def build_mapping():
    global url_mapping
    with open('document_mapping.txt','w',encoding='utf-8') as file:
        for doc_id, url in url_mapping.items():
            file.write(f'{doc_id},{url}\n')

# Function to build the mapping of document IDs to document lengths
def build_length_mapping():
    global url_length_mapping
    with open('document_length_mapping.txt','w',encoding='utf-8') as file:
        for doc_id, url in url_length_mapping.items():
            file.write(f'{doc_id},{url}\n')

# Function to read the document mapping from document_mapping
def read_mapping():
    global url_mapping
    with open('document_mapping.txt','r',encoding='utf-8') as file:
        line = file.readline()
        while line:
            line = line.strip().split(',')
            url_mapping[int(line[0])] = line[1]
            line = file.readline()

# Function to read the document length mapping from document_length_mapping
def read_length_mapping():
    global url_length_mapping
    with open('document_length_mapping.txt','r',encoding='utf-8') as file:
        line = file.readline()
        while line:
            line = line.strip().split(',')
            url_length_mapping[int(line[0])] = line[1]
            line = file.readline()


# Function to get memory usage of the process
def get_memory_usage():
    process = psutil.Process()
    memory_info = process.memory_info()
    return memory_info.rss  # Resident Set Size in bytes


# Function to replace special characters in a query string
def replaceSpecialCharacters(queryString):
    characterMapping = {
        '.': ' dot ',
        ',': ' comma ',
        '?': ' question mark ',
        '!': ' exclamation mark ',
        ';': ' semicolon ',
        ':': ' colon ',
        '(': ' left parenthesis ',
        ')': ' right parenthesis ',
        '[': ' left square bracket ',
        ']': ' right square bracket ',
        '{': ' left curly brace ',
        '}': ' right curly brace ',
        '-': ' hyphen ',
        '_': ' underscore ',
        '\'': ' apostrophe ',
        '"': ' quotation mark ',
        '/': ' slash ',
        '\\': ' backslash ',
        '|': ' vertical bar ',
        '@': ' at ',
        '#': ' hashtag ',
        '$': ' dollar ',
        '%': ' percent ',
        '^': ' caret ',
        '&': ' ampersand ',
        '*': ' asterisk ',
        '+': ' plus sign',
        '=': ' equal sign',
        '<': ' less than ',
        '>': ' greater than ',
        '~': ' tilde ',
        '`': ' backtick '
    }
    res = []
    for c in queryString:
        if c in characterMapping.keys():
            res.append(characterMapping[c])
        else:
            res.append(c)

    result_string = ''.join(res)
    return result_string

# Function to print search results
def printResults(resultDict):
    for rank in resultDict.keys():
        url, score = resultDict[rank]
        print(f'Rank {rank}: {url}')




if __name__ == '__main__':
    starttime = time.time() 

    # Set the path for storing index blocks
    index_blocks_path = './index-blocks'
    if not os.path.exists(index_blocks_path):
        os.makedirs(index_blocks_path)

    # downloaded folder
    folder_path = 'DEV'

    # Build the inverted index if the merged output doesn't exist
    if not os.path.exists("./merged_output.txt"):
        build_index(folder_path)

        # Get the list of index block files
        index_files = get_files_in_folder("index-blocks", "txt")

        # Perform binary merge on the index block files
        merge.binary_merge(index_files)

    print("Inverted index found or built"

    if not os.path.exists("./document_mapping.txt"):
        # if document mapping doesn't exist, write it
        build_mapping()
    else:
        # otherwise read it
        read_mapping()

    if not os.path.exists("./document_length_mapping.txt"):
        # if document mapping doesn't exist, write it
        build_length_mapping()
    else:
        # otherwise read it
        read_length_mapping()

    print("Read inverted index")
    script_dir = os.path.dirname(os.path.realpath(__file__))

    merged_output_path = os.path.join(script_dir, 'merged_output.txt')
    inverted_index = search.read_inverted_index_position(merged_output_path)

    #Report
    endtime = time.time()  
    runtime = endtime - starttime
    while True:
        user_query = input("Enter your search query: ")
        user_query = replaceSpecialCharacters(user_query)
        user_query_words = word_tokenize(user_query)
        # print(f'First round of query processing: {user_query_words}')
        if len(user_query_words) == 0:
            print(f'search must not be empty')
            continue
        starttime = time.time()
        result_documents, avg_score_orginal = search.search(user_query_words, inverted_index,url_mapping, url_length_mapping, merged_output_path)    #result_documents = search.search(user_query, inverted_index)
        endtime = time.time()  
        runtime = endtime - starttime
        print(f'Search time: {runtime}')
        # print(f'Avg score: {avg_score_orginal}')
        printResults(result_documents)

        corrected_start_time = time.time()
        spell = SpellChecker()

        corrected_query_words = list({spell.correction(word.lower()) if len(word) > 3 else word.lower() for word in user_query_words})

        corrected_query_words = [value for value in corrected_query_words if value is not None]

        # print(f'Corrected query words: {corrected_query_words}')

        if len(corrected_query_words):
            result_documents_corrected, avg_score_corrected = search.search(corrected_query_words, inverted_index,url_mapping, url_length_mapping, merged_output_path)

            if len(result_documents.keys()) == 0 or avg_score_corrected > avg_score_orginal:
                print(f'Did you mean {corrected_query_words}?')
                # print(f'Avg score: {avg_score_corrected}')
                printResults(result_documents_corrected)

                print(f'Suggestion time: {time.time() - corrected_start_time}')

        memory_used = get_memory_usage()
        print(f"Memory used: {memory_used} bytes")