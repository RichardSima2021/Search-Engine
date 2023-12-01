# app.py
from flask import Flask, render_template, request
import search
from main import *
from openai import OpenAI
import requests

app = Flask(__name__)
index_blocks_path = './index-blocks'
folder_path = 'DEV'

client = OpenAI(api_key = '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',)


def fetch_text_from_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    # Extract text content from the HTML, you may need to adjust this based on the structure of the webpage
    text_content = ' '.join([p.get_text() for p in soup.find_all('p')])
    return text_content

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

def summarize_text(texts):
    # Use OpenAI API for summarization
    if texts != "":
        prompt = "summarize\n".join(texts)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500  # Adjust as needed
        )
        return response.choices[0].message.content
    return ""


merged_output_path, inverted_index = build_index_if_needed()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET'])
def app_search():
    query = request.args.get('q', '')

    # Use the search function from search.py
    results = [v for k, v in sorted(search.search(query, inverted_index,url_mapping, url_length_mapping, merged_output_path).items())]    #result_documents = search.search(user_query, inverted_index)
    # print(results)


    # Fetch and summarize content from each URL
    summaries = []
    for url in results:
        text_content = fetch_text_from_url(url)
        # print(text_content.strip())
        if text_content.strip() != '':
            summary = summarize_text([text_content])
            summaries.append(summary)
            # print(summary)
        

    print("summaries list : ", summaries)
    # Generate a summary for all individual summaries
    if len(summaries) != 0:    
        all_summaries = summarize_text(summaries)
    else:
        all_summaries = 'URL contents are empty'

    return render_template('search_results.html', query=query, results=results, summaries = all_summaries)

if __name__ == '__main__':
    app.run(debug=True)
