# app.py
from flask import Flask, render_template, request
import search
from main import *
from openai import OpenAI
import requests
from spellchecker import SpellChecker
from nltk.tokenize import word_tokenize

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
            max_tokens=100  # Adjust as needed
        )
        return response.choices[0].message.content
    return ""


merged_output_path, inverted_index = build_index_if_needed()

@app.route('/')
def index():
    return render_template('index.html')



@app.route('/search', methods=['GET'])
def app_search():
    show_suggest = False
    query = request.args.get('q', '')
    # clean up the query so it can be used by search()
    user_query = replaceSpecialCharacters(query)
    user_query_words = word_tokenize(user_query)

    # whether we want to search with summary or not
    summarize = request.args.get('summarize', 'false') == 'true'


    # Use the search function from search.py

    # get result of searching with the user query
    result_documents, avg_score_orginal = search.search(user_query_words, inverted_index, url_mapping,
                                                        url_length_mapping,
                                                        merged_output_path)


    resultTuples = [v for k, v in sorted(result_documents.items())]
    # extract results
    results = [u for u,s in resultTuples]

    # run a query with spell checked corrections
    spell = SpellChecker()
    corrected_query = [spell.correction(word.lower()) if len(word) > 3 else word.lower() for word in user_query_words]
    corrected_query_string = ' '.join(corrected_query)
    corrected_query_words = list(set(corrected_query))
    result_documents_corrected, avg_score_corrected = search.search(corrected_query_words, inverted_index, url_mapping,
                                                                    url_length_mapping, merged_output_path)
    correctedResultTuples = [v for k, v in sorted(result_documents_corrected.items())]
    correctedResults = [u for u, s in correctedResultTuples]

    # if original query returned no results, return the spellchecked result because the user probably made a typo
    if len(results) == 0:
        results = correctedResults
        query = corrected_query_string
    # else if the avg score of the corrected query's results is higher than the original, suggest that query to the user
    elif avg_score_corrected > avg_score_orginal:
        show_suggest = True
        print(f'Did you mean {corrected_query_string}?')



    summaries = ['','','','','']

    # if option to search with summarize was selected
    if summarize:
        # Fetch and summarize content from each URL
        summaries = []
        for url in results:
            text_content = fetch_text_from_url(url)
            # print(text_content.strip())
            if text_content.strip() != '':
                summary = summarize_text([text_content])
            else:
                summary = ""
            summaries.append(summary)
                # print(summary)
        print("summaries list : ", summaries)

    # Zip results and summaries for passing to the template
    result_summaries = zip(results, summaries)

    # render the page and return it
    page = render_template('search_results.html', query=query, result_summaries=result_summaries, show_suggest = show_suggest, corrected_query = corrected_query_string, suggested_results = correctedResults, summarized = summarize)

    return page


@app.route('/suggest_search', methods=['GET'])
def suggest_search():
    # Get the suggested results from the query parameters
    suggested_results = request.args.getlist('suggested_results')

    # Other necessary data for rendering the template
    query = request.args.get('corrected_query')

    # Render the suggest.html template with the suggested results
    page = render_template('suggest.html', query=query, suggested_results=suggested_results)

    return page

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
