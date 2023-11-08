import os
import glob
import json


def get_files_in_folder(folder_path, file_extension='json'):
    files = []
    for root, _, filenames in os.walk(folder_path):
        for filename in filenames:
            if filename.endswith(f".{file_extension}"):
                files.append(os.path.join(root, filename))
    return files


def parse_document(document):
    # This function can be customized to tokenize and process your documents.
    # For simplicity, we split the document content by whitespace.
    tokens = document.split()
    return list(set(tokens))  # Remove duplicates


def build_index(folder_path, output_file):
    inverted_index = {}
    batch_size = 100  # Adjust the batch size as needed
    batch = []
    doc_id = 0

    for file_path in get_files_in_folder(folder_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            tokens = parse_document(content)
            for token in tokens:
                if token not in inverted_index:
                    inverted_index[token] = []
                inverted_index[token].append(doc_id)

        doc_id += 1

        if len(batch) >= batch_size:
            with open(output_file, 'a') as output:
                json.dump(inverted_index, output)
                output.write('\n')
            inverted_index.clear()

    # Write the remaining index to the output file
    if inverted_index:
        with open(output_file, 'a') as output:
            json.dump(inverted_index, output)
            output.write('\n')


if __name__ == '__main__':
    folder_path = ''  # Replace with the folder path you want to index
    output_file = 'inverted_index.json'

    # Ensure the output file starts empty
    open(output_file, 'w').close()

    build_index(folder_path, output_file)