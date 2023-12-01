# app.py
from flask import Flask, render_template, request
import search
from main import *

app = Flask(__name__)
index_blocks_path = './index-blocks'
folder_path = 'DEV'



def build_index_if_needed():
    # Set the path for storing index blocks
    if not os.path.exists(index_blocks_path):
        os.makedirs(index_blocks_path)

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

    return merged_output_path, inverted_index

merged_output_path, inverted_index = build_index_if_needed()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET'])
def app_search():
    query = request.args.get('q', '')

    # Use the search function from search.py
    results = [v for k, v in sorted(search.search(query, inverted_index,url_mapping, url_length_mapping, merged_output_path).items())]    #result_documents = search.search(user_query, inverted_index)
    print(results)

    return render_template('search_results.html', query=query, results=results)

if __name__ == '__main__':
    app.run(debug=True)
