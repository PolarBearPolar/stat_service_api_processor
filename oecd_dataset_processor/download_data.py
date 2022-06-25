# Importing modules
import datetime, threading, os, requests

# Initial parameters
max_threads = 12

def download_data(dsd, work_dir, filter_expression):
    global max_threads
    max_ = max_threads if len(filter_expression)//max_threads > max_threads else len(filter_expression)//max_threads+1
    desired_thread_num = input(f"\nHow many threads do you want data to be downloaded in? The min number of threads is 1. The max is {max_}: ")
    filepaths = []

    # Defining functions
    # Downloading data
    def download_data(dataset_id, subset_request, filepaths):
        for i in subset_request:
            http_request = f'https://stats.oecd.org/sdmx-json/data/{dataset_id}/{i}/all'
            response = requests.get(http_request)
            response_status = response.status_code
            if response_status == 200:
                src_data = response.text
                time_now = datetime.datetime.now()
                prefix = time_now.strftime('_%d%m%Y%H%M%S%f')
                filename = f'OECD_{dataset_id}_source_data{prefix}.json'
                response_filepath = os.path.join(os.getcwd(), filename)
                f = open(filename, 'w', encoding="utf-8")
                f.write(src_data)
                f.close()
                # Insert info into a list
                filepaths.append(response_filepath) 

    # Change working directory
    os.chdir(work_dir)

    # Fix thread number
    desired_thread_num = int(desired_thread_num.strip())
    if len(filter_expression) == 1:
        desired_thread_num = 1
    elif desired_thread_num < 1:
        desired_thread_num = 1
    elif desired_thread_num > len(filter_expression)-1:
        desired_thread_num = len(filter_expression)-1
    thread_num = len(filter_expression)//desired_thread_num
    max_thread_num = len(filter_expression)//max_threads
    if thread_num < max_thread_num:
        thread_num = max_thread_num

    # Download files and insert data into a list
    print('\nThe data is being downloaded...')
    download_threads = []
    beg = 0
    if thread_num == len(filter_expression):
        download_data(dsd.dataset_id, filter_expression, filepaths)
    else:
        for i in range(0, len(filter_expression), thread_num):
            filtr_len = len(filter_expression)
            if i == 0:
                continue
            elif (filtr_len-i) < thread_num:
                thread = threading.Thread(target = download_data, args = [dsd.dataset_id, filter_expression[beg:i], filepaths])
                download_threads.append(thread)
                thread.start()
                # Downloading the end subset range
                thread = threading.Thread(target = download_data, args = [dsd.dataset_id, filter_expression[i:filtr_len], filepaths])
                download_threads.append(thread)
                thread.start()
            else:
                thread = threading.Thread(target = download_data, args = [dsd.dataset_id, filter_expression[beg:i], filepaths])
                download_threads.append(thread)
                thread.start()
            beg = i

        # Wait until threads have been run
        for i in download_threads:
            i.join()
            
    print('The data has been downloaded')
    return filepaths