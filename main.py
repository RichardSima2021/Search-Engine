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


develop = True
unique_words = set()
doc_id = 1
block_id = 1
url_mapping = dict()
url_length_mapping = dict()


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


    if data['encoding'] != 'utf-8' and data['encoding'] != 'ascii':
        # not too sure what to do with non utf8 yet
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


    # parse_document 需要改的地方，for url
    # url = data.get('url', '')
    url = data['url']
    # print(url)
    parsed_url = urlparse(url)
    url_without_fragment = parsed_url._replace(fragment='').geturl()
    word_count = len(filtered_words_list)
    # return filtered_words_list
    # parse_document 需要改的地方，for url
    return filtered_words_list, url_without_fragment, word_count


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
    global url_length_mapping
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
            tokens, url, word_count= parse_document(file)
          
            url_mapping[doc_id] = url
            url_length_mapping[doc_id] = word_count

            if doc_id % 10 == 0:
                print(doc_id, url)
            # print('--------------------------------')


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


def build_length_mapping():
    global url_length_mapping
    with open('document_length_mapping.txt','w',encoding='utf-8') as file:
        for doc_id, url in url_length_mapping.items():
            file.write(f'{doc_id},{url}\n')




def read_mapping():
    global url_mapping
    with open('document_mapping.txt','r',encoding='utf-8') as file:
        line = file.readline()
        while line:
            line = line.strip().split(',')
            url_mapping[int(line[0])] = line[1]
            line = file.readline()


def read_length_mapping():
    global url_length_mapping
    with open('document_length_mapping.txt','r',encoding='utf-8') as file:
        line = file.readline()
        while line:
            line = line.strip().split(',')
            url_length_mapping[int(line[0])] = line[1]
            line = file.readline()


import psutil


def get_memory_usage():
    process = psutil.Process()
    memory_info = process.memory_info()
    return memory_info.rss  # Resident Set Size in bytes






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
        starttime = time.time()
        result_documents = search.search(user_query, inverted_index,url_mapping, merged_output_path)    #result_documents = search.search(user_query, inverted_index)
        endtime = time.time()  
        runtime = endtime - starttime
        print(f'Search time: {runtime}')
        memory_used = get_memory_usage()
        print(f"Memory used: {memory_used} bytes")

