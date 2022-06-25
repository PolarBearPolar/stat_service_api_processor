# Initial parameters
dim_separator = '.'
val_separator = '+'
tp_limit = 1000000
request_len_limit = 1000
url_address_len = 43

def generate_requests(dsd):
    global dim_separator, val_separator, tp_limit, request_len_limit, url_address_len

    # Defining functions
    # Splitting code rule for splitting codes into subsets according to user dimension order
    def partitioning_rule(dims, time_dim, request_len_limit, tp_limit):
        code_num = 1
        url_len = 0
        # Define partitioning rule
        user_dim_order = input('\nWrite dimension order based on the instructions above: ')
        # Splitting code
        request = user_dim_order.split('.')
        for i in range(len(request)):
            request[i] = int(request[i].strip())
        # Check limits
        for i in range(len(request)):
            if request[i] >= dims[i][0] or request[i] < 0:
                code_num = tp_limit + 1
                url_len = request_len_limit + 1
                print(f'\nDecrease the number of codes in the {i+1} dimension. Max value is {dims[i][0]}. You passed {request[i]}.')
                return (request, code_num, url_len)
            # Time point and url length limits
            if request[i] == 0:
                num = dims[i][0]
                len_ = 1
            else:
                num = request[i]
                len_ = request[i]*dims[i][1]
            code_num *= num
            url_len += len_
        if time_dim:
            code_num = code_num * time_dim
        url_len += url_address_len
        return (request, code_num, url_len)

    # Function for generating requests
    def create_requests(arr, main_arr, count, dim_separator):
        # Inner function for the action
        def concat_dim_codes(a_1, a_2):
            intern_arr = []
            for i in a_1:
                for j in a_2:
                    string = str(i) + dim_separator + str(j)
                    intern_arr.append(string)
            return intern_arr   
        # Conditioning
        if count + 1 < len(main_arr):
            intern_arr = concat_dim_codes(arr, main_arr[count])
            return create_requests(intern_arr, main_arr, count + 1, dim_separator)
        elif count + 1 == len(main_arr):
            intern_arr = concat_dim_codes(arr, main_arr[count])
            return intern_arr

     # Printing info about dimension order
    print('\nHere is the dimension order:\n')
    dimension_order = []
    time_dim = None
    for i in dsd.dimensions:
        dim_data = "{}({})".format(i[0], len(i[1]))
        dimension_order.append(dim_data)
    if dsd.time_dimension:
        time_dim = "{}({})".format(dsd.time_dimension[0][0], len(dsd.time_dimension[0][1]))
    dimension_order = '.'.join(dimension_order)
    if time_dim:
        print('- ' + dimension_order + " | " + time_dim + '(do not include time dimension in requests)')
    else:
        print('- ' + dimension_order)
    print(f'\nChoose the number of codes for each dimension.' \
          f' It will determine how long each request will be (max {request_len_limit} signs)' \
          f' and if it exceeds the maximum number of time points returned from the server ({tp_limit} time points.' \
          f' This value is obtained by multiplying dimensions and the time dimension if it is present).' \
          f' Write only the number of codes for each corresponding dimension separated by a dot "."' \
          f' If all the codes of a dimension must be returned, pass "0".')

    # Getting dimensions and their codes (in lists) for building requests and partitioning rule
    request_list = []
    dims = []
    val_len = 0
    for i in dsd.dimensions:
        code_vals = []
        dims.append([len(i[1])])
        for j in i[1]:
            if val_len < len(j):
                val_len = len(j)
            code_vals.append(j)
        request_list.append(code_vals)
        dims[-1].append(val_len)
    if dsd.time_dimension:
        time_dim = len(dsd.time_dimension[0][1])
    else:
        time_dim = 1

    # Partitioning rule check
    request_check = partitioning_rule(dims, time_dim, request_len_limit, tp_limit)
    check_request = False
    while check_request == False:
        if request_check[1] > tp_limit or request_check[2] > request_len_limit:
            print(f'\nSomething went wrong. Try again!\n' \
                f'\nCurrent time point number - {request_check[1]}, limit - {tp_limit}\n' \
                f'Current url length - {request_check[2]}, limit - {request_len_limit}\n')
            check_request = False
            request_check = partitioning_rule(dims, time_dim, request_len_limit, tp_limit)
            continue
        print(f'\nThe partitioning rule has been approved!\n' \
                  f'Current time point number - {request_check[1]}, limit - {tp_limit}\n' \
                  f'Current url length - {request_check[2]}, limit - {request_len_limit}')
        question = input('Do you want to continue? Otherwise, you can increase / decrease time points or url length? Y/N: ').strip().upper()
        if question == 'Y':
            request = request_check[0]
            check_request = True
        else:
            check_request = False
            request_check = partitioning_rule(dims, time_dim, request_len_limit, tp_limit)

     # Devided code indexes in a separate list called ranges
    ranges = []
    for i in range(len(request)):
        list_num = len(request_list[i])
        if request[i] == 0:
            ranges.append([])
        else:
            group = range(0, list_num, request[i])
            arr = []
            start = 0
            if request[i] > 1:
                for j in group:
                    if j == 0:
                        continue
                    arr.append([start, j])
                    if (list_num-1)-j < request[i]:
                        arr.append([j, list_num])
                    start = j
                ranges.append(arr)
            elif request[i] == 1:
                ranges.append(list(group))

    # Devided codes in dictionary
    for i in range(len(ranges)):
        if not ranges[i]:
            request_list[i] = ['']
        elif type(ranges[i][0]) == list:
            split_arr = []
            for j in ranges[i]:
                #  Get first and last position of subset and slice code list into parts, then join tese parts with value separator
                beg = j[0]
                end = j[-1]
                if beg == end:
                    split_arr.append(request_list[i][beg])
                else:
                    split_arr.append(val_separator.join(request_list[i][beg:end]))
            request_list[i] = split_arr

    # Generating requests
    # Checking ranges length
    if len(request_list) > 1:
        filter_expression = create_requests(request_list[0], request_list, 1, dim_separator)
    else:
        filter_expression = request_list
    
    # Fixing filter expression lists with only one dimension
    if len(filter_expression) == 1 and isinstance(filter_expression[0], list):
        filter_expression = filter_expression[0]

    return filter_expression