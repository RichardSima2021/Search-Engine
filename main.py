import os
import glob
import json
import string
from urllib.parse import urlparse, urlunparse
import merge
import search
from bs4 import BeautifulSoup
import nltk
nltk.download('punkt')
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
nltk.download('stopwords')
import time

develop = True
unique_words = set()
doc_id = 1
block_id = 1
url_mapping = dict()
def get_files_in_folder(folder_path, file_extension='json'):
    files = []
    for root, _, filenames in os.walk(folder_path):
        for filename in filenames:
            if filename.endswith(f".{file_extension}"):
                files.append(os.path.join(root, filename))
    return files


def parse_document(file):
    # print(f"parsing {file}")
    # input()
    data = json.load(file)
    content = data['content']

    if data['encoding'] != 'utf-8':
        # not too sure what to do with non utf8 yet
        return [], ''

    soup = BeautifulSoup(content, "lxml")

    words = soup.get_text().lower()
    stopword_set = set(stopwords.words('english'))

    words_list = word_tokenize(words)
    filtered_words_list = [
        w
        for w in words_list
    ]

    # parse_document 需要改的地方，for url
    # url = data.get('url', '')
    url = data['url']
    # print(url)
    parsed_url = urlparse(url)
    url_without_fragment = parsed_url._replace(fragment='').geturl()
    # return filtered_words_list
    # parse_document 需要改的地方，for url
    return filtered_words_list, url_without_fragment

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

def build_index(folder_path):
    global url_mapping
    inverted_index = dict()
    # url_mapping = dict()
    batch_limit = 2500  # Adjust the batch size as needed (note: 2000)
    current_batch = 1
    global doc_id
    global block_id

    for file_path in get_files_in_folder(folder_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            file_name = os.path.splitext(os.path.basename(file_path))[0]

            # build index 需要改的地方，for url
            tokens, url = parse_document(file)
            url_mapping[doc_id] = url
            print(doc_id, url)
            # print('--------------------------------')

            for token in tokens:
                if token not in inverted_index:
                    inverted_index[token] = []

                if token not in unique_words:
                    unique_words.add(token)
                inverted_index[token].append(doc_id)

        doc_id += 1
        current_batch += 1
        # print(doc_id)

        if current_batch == batch_limit:
            current_batch = 1
            write_block(inverted_index)
            inverted_index.clear()

    # Write the remaining index to the output file
    if inverted_index:
        write_block(inverted_index)
        inverted_index.clear()

    # build index 需要改的地方，for url
    # return url_mapping

def build_mapping():
    global url_mapping
    with open('document_mapping.txt','w',encoding='utf-8') as file:
        for doc_id, url in url_mapping.items():
            file.write(f'{doc_id},{url}\n')


def read_mapping():
    global url_mapping
    with open('document_mapping.txt','r',encoding='utf-8') as file:
        line = file.readline()
        while line:
            line = line.strip().split(',')
            url_mapping[int(line[0])] = line[1]
            line = file.readline()



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

    print("Inverted index found or built")

    if not os.path.exists("./document_mapping.txt"):
        # if document mapping doesn't exist, write it
        build_mapping()
    else:
        # otherwise read it
        read_mapping()



    print("Read inverted index")
    script_dir = os.path.dirname(os.path.realpath(__file__))

    merged_output_path = os.path.join(script_dir, 'merged_output.txt')
    inverted_index = search.read_inverted_index_position(merged_output_path)

    #Report
    endtime = time.time()  
    runtime = endtime - starttime
    while True:
        user_query = input("Enter your search query: ")
        starttime = time.time()
        # print(inverted_index)
        result_documents = search.search(user_query, inverted_index,url_mapping, merged_output_path)    #result_documents = search.search(user_query, inverted_index)
        endtime = time.time()  
        runtime = endtime - starttime
        print(f'Search time: {runtime}')