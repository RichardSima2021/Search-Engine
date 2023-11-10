import os
import heapq
import ast
def binary_merge(files):
    # Open all files
    input_files = [open(file, 'r', encoding='utf-8') for file in files]

    # List to store the current word for each file
    current_words = ["" for file in files]

    # Use a heap for binary merging
    heap = []

    # Initialize the heap
    start_word = ""
    # Process each file and extract the initial word from each
    for i, input_file in enumerate(input_files):
        if i == 0:
            # For the first file, read the first line and extract the components
            line = input_file.readline().strip()
            if line:
                result_tuple = ast.literal_eval(line)
                # Extracting the components from the tuple
                word = result_tuple[0]
                ids = result_tuple[1]
                heapq.heappush(heap, (word, ids, i))
                current_words[i] = word
            start_word = word
        else:
            # For subsequent files, read the first line and extract the components
            word = ""
            line = input_file.readline().strip()
            if line:
                result_tuple = ast.literal_eval(line)
                # Extracting the components from the tuple
                word = result_tuple[0]
                ids = result_tuple[1]
                current_words[i] = word
                heapq.heappush(heap, (word, ids, i))
                 # Check the heap size
                if len(heap) >= 500:
                        print("exceeded in size")
                        break
            # Ensure the order of words and skip to the next if needed 
            while word <= start_word:
                line = input_file.readline().strip()
                if line:
                    result_tuple = ast.literal_eval(line)
                    # Extracting the components from the tuple
                    word = result_tuple[0]
                    ids = result_tuple[1]
                    current_words[i] = word
                    heapq.heappush(heap, (word, ids, i))
                    if len(heap) >= 500:
                        print("exceeded in size")
                        break
    # Execute binary merge
    with open('merged_output.txt', 'w', encoding='utf-8') as merged_file:
        while heap:
            current_word, current_ids, file_index = heapq.heappop(heap)
          
            # Process each file's words
            for index, word in enumerate(current_words):
                # Ensure words are in order
                if word <= start_word:
                    # Process words until reaching a new word or end of file
                    while word <= start_word and word != "":
                         # Read the next line from the corresponding file
                        line = input_files[index].readline().strip()
                        if line:
                            result_tuple = ast.literal_eval(line)
                            # Extracting the components from the tuple
                            word = result_tuple[0]
                            ids = result_tuple[1]
                            current_words[i] = word
                            heapq.heappush(heap, (word, ids, i))
                        else:
                            word = ""
            # Merge entries with the same word
            while heap and heap[0][0] == current_word:
                _, other_ids, _ = heapq.heappop(heap)
                current_ids.extend(other_ids)
            # Write the merged entry to the output file
            merged_file.write(f"{current_word}\t{current_ids}\n")

            # Read the next line from each file
            for i, input_file in enumerate(input_files):
                line = input_file.readline().strip()
                if line:
                    result_tuple = ast.literal_eval(line)
                    # Extracting the components from the tuple
                    word = result_tuple[0]
                    ids = result_tuple[1]
                    heapq.heappush(heap, (word, ids, i))
                    current_words[i] = word

    # Close all files
    for input_file in input_files:
        input_file.close()

if __name__ == "__main__":
    file_list = ["index-blocks/inverted_index-1.txt", "index-blocks/inverted_index-2.txt", "index-blocks/inverted_index-3.txt"]  # Add the actual file names here

    binary_merge(file_list)
