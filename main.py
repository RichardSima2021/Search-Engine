import os
import glob
import json
import string

from bs4 import BeautifulSoup
import nltk
nltk.download('punkt')
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
nltk.download('stopwords')

develop = True
unique_words = set()
doc_id = 1
block_id = 1
def get_files_in_folder(folder_path, file_extension='json'):
    files = []
    for root, _, filenames in os.walk(folder_path):
        for filename in filenames:
            if filename.endswith(f".{file_extension}"):
                files.append(os.path.join(root, filename))
    return files


def parse_document(file):
    data = json.load(file)
    content = data['content']

    if data['encoding'] != 'utf-8':
        # not too sure what to do with non utf8 yet
        return []

    soup = BeautifulSoup(content, "lxml")


    if soup.find('title') is None:
        # if the page doesn't have a title, don't bother processing it
        if develop: print("The page is incomplete or missing a title element")
        return []

    words = soup.get_text().lower()
    stopword_set = set(stopwords.words('english'))

    words_list = word_tokenize(words)
    filtered_words_list = [w for w in words_list if not w.lower() in stopword_set and len(w) > 1 and all(
        char not in string.punctuation for char in w)]


    # tokens = document.split()
    return filtered_words_list  # Remove duplicates


def write_block(indices):
    global block_id
    output_file = f'index-blocks/inverted_index-{block_id}.txt'
    sorted_indices = sorted(indices.items(), key=lambda x: x[0])
    with open(output_file, 'w') as output:
        for pair in sorted_indices:
            try:
                output.write(f'{pair}\n')
            except Exception as e:
                print(f'An error occurred while writing, {e}')

    output.close()
    block_id += 1

def build_index(folder_path):

    inverted_index = dict()
    batch_limit = 500  # Adjust the batch size as needed
    current_batch = 1
    global doc_id
    global block_id

    for file_path in get_files_in_folder(folder_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            file_name = os.path.splitext(os.path.basename(file_path))[0]
            # print(file_name)
            # content = file.read()
            tokens = parse_document(file)
            # print(tokens)
            for token in tokens:
                if token not in inverted_index:
                    inverted_index[token] = []

                if token not in unique_words:
                    unique_words.add(token)
                inverted_index[token].append(doc_id)

        doc_id += 1
        current_batch += 1
        print(doc_id)

        if current_batch == batch_limit:
            current_batch = 1
            write_block(inverted_index)
            inverted_index.clear()

    # Write the remaining index to the output file
    if inverted_index:
        write_block(inverted_index)
        inverted_index.clear()


if __name__ == '__main__':
    folder_path = 'ANALYST/www_informatics_uci_edu/'

    build_index(folder_path)