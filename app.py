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
    user_query = replaceSpecialCharacters(query)
    user_query_words = word_tokenize(user_query)



    # Use the search function from search.py
    # results = [v for k, v in sorted(search.search(query, inverted_index,url_mapping, url_length_mapping, merged_output_path).items())]    #result_documents = search.search(user_query, inverted_index)
    # print(results)

    result_documents, avg_score_orginal = search.search(user_query_words, inverted_index, url_mapping,
                                                        url_length_mapping,
                                                        merged_output_path)

    # print(result_documents)
    resultTuples = [v for k, v in sorted(result_documents.items())]
    # print(resultTuples)
    results = [u for u,s in resultTuples]

    spell = SpellChecker()
    corrected_query = [spell.correction(word.lower()) if len(word) > 3 else word.lower() for word in user_query_words]
    corrected_query_string = ' '.join(corrected_query)
    # remove duplicate words
    corrected_query_words = list(set(corrected_query))
    # corrected_query_words = list({spell.correction(word.lower()) if len(word) > 3 else word.lower() for word in user_query_words})
    result_documents_corrected, avg_score_corrected = search.search(corrected_query_words, inverted_index, url_mapping,
                                                                    url_length_mapping, merged_output_path)
    correctedResultTuples = [v for k, v in sorted(result_documents_corrected.items())]
    correctedResults = [u for u, s in correctedResultTuples]
    # print(f"Corrected results: {correctedResults}")

    print(f'Original score: {avg_score_orginal}, corrected score: {avg_score_corrected}')

    if len(results) == 0:
        results = correctedResults
        query = corrected_query_string

    elif avg_score_corrected > avg_score_orginal:
        show_suggest = True
        print(f'Did you mean {corrected_query_string}?')



    # if show_suggest:
    #     print(f'Did you mean {corrected_query_words}')

    # results = [v for k, v in sorted(result_documents.items())] # result_documents = search.search(user_query, inverted_index)
    # results = [url for k, v in sorted(result_documents.items()) for url, score in v]

    # print(results)

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

    # Generate a summary for all individual summaries
    if len(summaries) != 0:
        all_summaries = summarize_text(summaries)
    else:
        all_summaries = 'URL contents are empty'

    # summaries = ['a','a','a','a','a','a','a']
    # result_summaries = zip(results, summaries)
    # # result_summaries = []
    # all_summaries = []

    page = render_template('search_results.html', query=query, result_summaries=result_summaries, all_summaries = all_summaries, show_suggest = show_suggest, corrected_query = corrected_query_string, suggested_results = correctedResults)

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
