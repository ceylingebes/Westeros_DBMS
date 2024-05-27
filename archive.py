import time
import os

MAX_NUMBER_OF_FIELDS = 10
MAX_TYPE_NAME_LENGTH = 20
MAX_FIELD_NAME_LENGTH = 20
MAX_RECORDS_PER_PAGE = 10
MAX_PAGES_PER_FILE = 20


def initialize_type(type_name, primary_key_index):
    if not os.path.exists(type_name):
        os.makedirs(type_name)
    # Create the first page file
    with open(f"{type_name}/page_0.txt", 'w') as f:
        f.write(str(int(primary_key_index) - 1) + "\n")
        initial_vacancy_list = str([0] * 9)
        f.write(initial_vacancy_list + "\n")
        for _ in range(8):
            f.write("\n")

def add_record(type_name, values):
    record_str = " ".join(values)
    new_record_added = False

    # Find the latest page
    page_num = 0
    while os.path.exists(f"{type_name}/page_{page_num}.txt"):
        page_num += 1
    page_num -= 1

    for i in range(page_num + 1):
        page_path = f"{type_name}/page_{i}.txt"
        with open(page_path, 'r+') as f:
            primary_key_index = int(f.readline().strip())
            vacancy = eval(f.readline().strip())
            lines = [f.readline().strip() for _ in range(9)]
            
            if 0 in vacancy and not new_record_added:  
                for i, is_occupied in enumerate(vacancy):
                    if not is_occupied:
                        vacancy[i] = 1
                        lines[i] = record_str
                        new_record_added = True
                        break
                
                if new_record_added:
                    f.seek(0)
                    f.write(str(primary_key_index) + "\n")
                    f.write(str(vacancy) + "\n")
                    f.writelines([line + "\n" for line in lines])
                    f.truncate()
                    break

    if not new_record_added:
        vacancy_list = [1] + [0] * 8
        new_page = [str(vacancy_list)] + [record_str] + [""] * 8
        new_page_path = f"{type_name}/page_{page_num + 1}.txt"
        with open(new_page_path, 'w') as f:
            f.write(str(primary_key_index) + "\n")
            f.writelines([line + "\n" for line in new_page])
            f.truncate()

def delete_record(type_name, search_primary_key):
    page_num = 0
    page_modified = False

    while os.path.exists(f"{type_name}/page_{page_num}.txt"):
        page_path = f"{type_name}/page_{page_num}.txt"
        with open(page_path, 'r+') as f:
            primary_key_index = int(f.readline().strip())
            vacancy = eval(f.readline().strip())
            lines = [f.readline().strip() for _ in range(9)]
            
            if 1 in vacancy:
                for i, is_occupied in enumerate(vacancy):
                    if is_occupied:
                        record_fields = lines[i].split()
                        record_primary_key = record_fields[primary_key_index]
                        if record_primary_key == search_primary_key:
                            vacancy[i] = 0
                            lines[i] = ""
                            page_modified = True
                            break
                
                if page_modified:
                    f.seek(0)
                    f.write(str(primary_key_index) + "\n")
                    f.write(str(vacancy) + "\n")
                    f.writelines([line + "\n" for line in lines])
                    f.truncate()
                    break

        page_num += 1

    return page_modified

def search_record(type_name, primary_key):
    page_num = 0

    while os.path.exists(f"{type_name}/page_{page_num}.txt"):
        page_path = f"{type_name}/page_{page_num}.txt"
        with open(page_path, 'r') as f:
            primary_key_index = int(f.readline().strip())
            vacancy = eval(f.readline().strip())
            lines = [f.readline().strip() for _ in range(9)]
            
            if 1 in vacancy:
                for i, is_occupied in enumerate(vacancy):
                    if is_occupied:
                        record_fields = lines[i].split()
                        record_primary_key = record_fields[primary_key_index]
                        if record_primary_key == primary_key:
                            return record_fields
        
        page_num += 1

    return None

def log_operation(operation, status):
    with open('log.txt', 'a') as h:
        h.write(f"{int(time.time())}, {operation}, {status}\n")

def in_create_type(operation):
    _, _, type_name, num_fields, primary_key_index, *fields = operation.split()
    fields = [(fields[i], fields[i+1]) for i in range(0, len(fields), 2)]
    if len(fields) > MAX_NUMBER_OF_FIELDS or len(type_name) > MAX_TYPE_NAME_LENGTH or any(len(f[0]) > MAX_FIELD_NAME_LENGTH for f in fields):
        log_operation(operation, 'failure')
        return
    if os.path.exists(f"{type_name}"):
        log_operation(operation, 'failure')
    else:
        initialize_type(type_name, primary_key_index)
        log_operation(operation, 'success')

def in_create_record(operation):
    _, _, type_name, *values = operation.split()
    
    if not os.path.exists(f"{type_name}"):
        log_operation(operation, 'failure')
        return
    
    with open(f"{type_name}/page_0.txt", 'r') as f:
        primary_key_index = int(f.readline().strip())
        primary_key = values[primary_key_index]

    if search_record(type_name, primary_key):
        log_operation(operation, 'failure')
    else:
        add_record(type_name, values)
        log_operation(operation, 'success')

def in_delete_record(operation):
    _, _, type_name, delete_primary_key = operation.split()
    if not os.path.exists(f"{type_name}"):
        log_operation(operation, 'failure')
        return
    if delete_record(type_name, delete_primary_key):
        log_operation(operation, 'success')
    else:
        log_operation(operation, 'failure')

def in_search_record(operation):
    _, _,  type_name, search_primary_key = operation.split()
    record = search_record(type_name, search_primary_key)
    if record:
        log_operation(operation, 'success')
        return record
    else:
        log_operation(operation, 'failure')
        return ""

def main(input_file):
    with open(input_file, 'r') as f:
        operations = f.readlines()
    results = []
    for operation in operations:
        if operation.startswith('create type'):
            in_create_type(operation.strip())
        elif operation.startswith('create record'):
            in_create_record(operation.strip())
        elif operation.startswith('delete record'):
            in_delete_record(operation.strip())
        elif operation.startswith('search record'):
            result = in_search_record(operation.strip())
            if result:
                results.append(result)
    with open('output.txt', 'w') as g:
        g.write("\n".join([" ".join(result) for result in results]))

if __name__ == "__main__":
    import sys
    input_file = sys.argv[1]
    main(input_file)