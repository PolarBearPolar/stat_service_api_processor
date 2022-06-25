# Importing modules
import json, time, os, xlsxwriter
import pandas as pd
from zipfile import ZipFile, ZIP_DEFLATED

def transform_data(dsd, work_dir, filepaths, save_mode, host_work_dir):
    # Initial parameters
    xlsx_file = os.path.join(work_dir, f"{dsd.dataset_id.lower()}_source_data.xlsx")
    txt_file = os.path.join(work_dir, f"{dsd.dataset_id.lower()}_source_data.txt")
    zip_file = os.path.join(work_dir, f"{dsd.dataset_id.lower()}_source_data.zip")

    # Change working directory
    os.chdir(work_dir)
    
    # Define time dimension
    dims = [i[0] for i in dsd.dimensions]
    if dsd.time_dimension:
        time_dimension = dsd.time_dimension[0][0]
    else:
        question = f"\nChoose which dimension values you want to be used as columns in the transformed file.\n" \
            f"- Dimensions to choose from - {', '.join(dims)}\n"
        time_dimension = input(question).strip()
        while time_dimension not in dims:
            time_dimension = input("Try again: ").strip()

    # Defining functions
    def write_data(ins_dic, mode, write_obj):
        # Convert dic values to str
        row = []
        for i in ins_dic.values():
            if i is None:
                row.append('')
            else:
                row.append(str(i))
        # Inserting data into a txt file
        write_obj.write('\n')
        write_obj.write('\t'.join(row).encode('ascii', 'ignore').decode('ascii'))

    def transform_data(source_data, headers, mode, write_obj):
        # Get dataset part of a file
        source_data_dataset = source_data['dataSets'][0]['series']
        dim_structure = source_data['structure']['dimensions']['series']
        ins_dic = {}
        for el in source_data_dataset.keys():
            # Add headers with empty values to a row (ins_dic is a row)
            for i in headers:
                ins_dic[i] = None
            # Get dimensions
            src_data = el.split(':')
            for i in range(len(src_data)):
                for j in dim_structure:
                    if j['keyPosition'] == i:
                        code_position = int(src_data[i])
                        code_value = j['values'][code_position]['id']
                        code_value_name = j['values'][code_position]['name']
                        ins_dic[j['id']] = code_value
                        dim_name_header = '%s_NAME' % j['id']
                        ins_dic[dim_name_header] = code_value_name
            # Get time series attributes
            attr_ser_structure = source_data['structure']['attributes']['series']
            src_data = source_data_dataset[el]['attributes']
            for i in range(len(src_data)):
                if src_data[i] is None:
                    attr_value = None
                    ins_dic[attr_ser_structure[i]['id']] = attr_value
                else:
                    code_position = int(src_data[i])
                    attr_value  = attr_ser_structure[i]['values'][code_position]['id']
                    attr_value_name  = attr_ser_structure[i]['values'][code_position]['name']
                    ins_dic[attr_ser_structure[i]['id']] = attr_value
                    attr_name_header = '%s_NAME' % attr_ser_structure[i]['id']
                    ins_dic[attr_name_header] = attr_value_name
            # Get observations
            src_data = list(source_data_dataset[el]['observations'].items())
            obs_structure = source_data['structure']['dimensions']['observation']
            # Get observations for inserting into xlsx file and insert them
            for i in range(len(obs_structure[0]['values'])):
                obs_key = f"{obs_structure[0]['values'][i]['id']}"
                code_position = str(i)
                obs_value = source_data_dataset[el]['observations'].get(code_position, None)
                if obs_value is None:
                    continue
                else:
                    obs_value = obs_value[0]
                ins_dic[obs_key] = obs_value
            # Write data to a file
            write_data(ins_dic, mode, write_obj)
            # Set inserting dictionary to empty again
            ins_dic = {}
            
    def transform_data_no_time_dim(source_data, headers, mode, write_obj, time_dimension):
        # Get dataset part of a file
        source_data_dataset = source_data['dataSets'][0]['observations']
        dim_structure = source_data['structure']['dimensions']['observation']
        ins_dic = {}
        for el in source_data_dataset.keys():
            # Add headers with empty values to a row (ins_dic is a row)
            for i in headers:
                ins_dic[i] = None
            # Get dimensions
            src_data = el.split(':')
            current_row = []
            for i in range(len(src_data)):
                for j in dim_structure:
                    if j['keyPosition'] == i:
                        code_position = int(src_data[i])
                        code_value = j['values'][code_position]['id']
                        code_value_name = j['values'][code_position]['name']
                        # Time dimension key
                        if j['id'] == time_dimension:
                            obs_key = code_value
                        else:
                            ins_dic[j['id']] = code_value
                            dim_name_header = '%s_NAME' % j['id']
                            ins_dic[dim_name_header] = code_value_name
                            current_row.append(code_value)
            # Get time series attributes
            attr_ser_structure = source_data['structure']['attributes']['series']
            if attr_ser_structure:
                src_data = source_data_dataset[el]['attributes']
                for i in range(len(src_data)):
                    if src_data[i] is None:
                        attr_value = None
                        ins_dic[attr_ser_structure[i]['id']] = attr_value
                    else:
                        code_position = int(src_data[i])
                        attr_value  = attr_ser_structure[i]['values'][code_position]['id']
                        attr_value_name  = attr_ser_structure[i]['values'][code_position]['name']
                        ins_dic[attr_ser_structure[i]['id']] = attr_value
                        attr_name_header = '%s_NAME' % attr_ser_structure[i]['id']
                        ins_dic[attr_name_header] = attr_value_name
            # Get observations
            src_data = list(source_data_dataset[el])
            obs_value = source_data_dataset[el][0]
            if obs_value is None:
                continue
            else:
                obs_value = obs_value
            ins_dic[obs_key] = obs_value
            # Write data to a file
            write_data(ins_dic, mode, write_obj)
            # Set inserting dictionary to empty again
            ins_dic = {}

    print('\nThe data is being transformed...')
    # Get headers for source file from datastructre 
    headers, time_points = [],[]
    dims = [i[0] for i in dsd.dimensions]
    attrs = [i[0] for i in dsd.attributes]
    for i in dsd.dimensions:
        if i[0] != time_dimension:
            headers.append(i[0])
            concept_name = '%s_NAME' % i[0]
            headers.append(concept_name)
        else:
            time_points = i[1]
    for i in dsd.attributes:
        headers.append(i[0])
        concept_name = '%s_NAME' % i[0]
        headers.append(concept_name)
    if dsd.time_dimension:
        time_points = dsd.time_dimension[0][1]
    keys = headers.copy()
    headers += time_points
    
    # Delete txt file if it exists
    if os.path.exists(txt_file):
        os.remove(txt_file)
    # Create a new txt file
    f = open(txt_file, 'a')
    # Write headers
    f.write('\t'.join(headers))
    
    # Reading and processing JSON file
    for i in range(len(filepaths)):
        json_file = open(filepaths[i], 'r', encoding='utf-8')
        source_data = json.load(json_file)
        if dsd.time_dimension:
            transform_data(source_data, headers, save_mode, f)
        else:
            df = pd.DataFrame(columns = headers)
            transform_data_no_time_dim(source_data, headers, "txt", f, time_dimension)
        json_file.close()
    # Save txt file
    if dsd.time_dimension:
        f.close()
    else:
        f.close()
        df = pd.read_csv(txt_file, sep='\t', dtype=object, encoding='utf-8')
        df = df.groupby(keys, dropna=False)[time_points].first().reset_index()
        df.to_csv(txt_file, sep='\t', index=False, encoding='utf-8')
    # Save in xlsx mode (if applicable)
    if save_mode == "xlsx":
        # Delete xlsx file if it exists
        if os.path.exists(xlsx_file):
            os.remove(xlsx_file)
        # Read txt file and write it to an xlsx file using pandas and xlsxwriter
        df = pd.read_csv(txt_file, sep='\t', dtype=object, encoding='utf-8')
        writer = pd.ExcelWriter(xlsx_file, engine='xlsxwriter')
        df.to_excel(writer, sheet_name=dsd.dataset_id.lower(), index=False)
        writer.close()
        # Delete temporary txt file
        os.remove(txt_file)
     
    # Delete archive if it exists
    if os.path.exists(zip_file):
        os.remove(zip_file)
    # Archive soure data files
    zip_obj = ZipFile(zip_file, 'w', compression = ZIP_DEFLATED)
    for i in filepaths:
        filename = i.split("\\")[-1]
        zip_obj.write(filename)
    zip_obj.close()
    # Delete source data
    for i in filepaths:
        os.remove(i)
    print(f'The data has been transformed! Congrats! The transformed data is in {host_work_dir}. Have a wonderful day!')