import os
import heapq
import ast
def binary_merge(files):
    max_heap_size_bytes = 2 * 1024 * 1024
    # 打开所有文件
    file_handles = [open(file, 'r') for file in files]
    words_file = ["" for file in files]
    # 使用堆来进行二进制合并
    heap = []

    # 初始化堆
    start_word = ""
    for i, file_handle in enumerate(file_handles):
        if i == 0:
            line = file_handle.readline().strip()
            if line:
                result_tuple = ast.literal_eval(line)
                # Extracting the components from the tuple
                word = result_tuple[0]
                ids = result_tuple[1]
                heapq.heappush(heap, (word, ids, i))
                words_file[i] = word
            start_word = word
        else:
            word = ""
            line = file_handle.readline().strip()
            if line:
                result_tuple = ast.literal_eval(line)
                # Extracting the components from the tuple
                word = result_tuple[0]
                ids = result_tuple[1]
                words_file[i] = word
                heapq.heappush(heap, (word, ids, i))
                if len(heap) >= 500:
                        print("exceeded in size")
                        break
            while word <= start_word:
                line = file_handle.readline().strip()
                if line:
                    result_tuple = ast.literal_eval(line)
                    # Extracting the components from the tuple
                    word = result_tuple[0]
                    ids = result_tuple[1]
                    words_file[i] = word
                    heapq.heappush(heap, (word, ids, i))
                    if len(heap) >= 500:
                        print("exceeded in size")
                        break
    # 执行二进制合并
    with open('merged_output.txt', 'w') as merged_file:
        while heap:
            current_word, current_ids, file_index = heapq.heappop(heap)
            
            for index, word in enumerate(words_file):
                if word <= start_word:
                    while word <= start_word and word != "":
                        line = file_handles[index].readline().strip()
                        if line:
                            result_tuple = ast.literal_eval(line)
                            # Extracting the components from the tuple
                            word = result_tuple[0]
                            ids = result_tuple[1]
                            words_file[i] = word
                            heapq.heappush(heap, (word, ids, i))
                        else:
                            word = ""
            while heap and heap[0][0] == current_word:
                _, other_ids, _ = heapq.heappop(heap)
                current_ids.extend(other_ids)
            merged_file.write(f"{current_word}\t{current_ids}\n")

            # 从相应文件读取下一行
            line = file_handles[file_index].readline().strip()
            if line:
                result_tuple = ast.literal_eval(line)
                # Extracting the components from the tuple
                word = result_tuple[0]
                ids = result_tuple[1]
                heapq.heappush(heap, (word, ids, file_index))

    # 关闭所有文件
    for file_handle in file_handles:
        file_handle.close()

if __name__ == "__main__":
    file_list = ["index-blocks/inverted_index-1.txt", "index-blocks/inverted_index-2.txt", "index-blocks/inverted_index-3.txt"]  # Add the actual file names here

    binary_merge(file_list)
