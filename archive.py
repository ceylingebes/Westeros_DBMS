import time
import os

# Constants
MAX_NUMBER_OF_FIELDS = 10
MAX_TYPE_NAME_LENGTH = 20
MAX_FIELD_NAME_LENGTH = 20
MAX_RECORDS_PER_PAGE = 10
MAX_PAGES_PER_FILE = 20


# function to initialize a type in a directory
def initialize_type(type_name, primary_key_index):
    if not os.path.exists(type_name): # check if the type already exists
        os.makedirs(type_name) # create a directory for the type
    # Create the first page file
    with open(f"{type_name}/page_0.txt", 'w') as f: # open the file in write mode
        f.write(str(int(primary_key_index) - 1) + "\n") # write the primary key index
        initial_vacancy_list = str([0] * 9) # create the page header i.e. the vacancy list
        f.write(initial_vacancy_list + "\n")
        for _ in range(8):
            f.write("\n")


# function to add a record to a type 
def add_record(type_name, values):
    record_str = " ".join(values) # convert the values to a string
    new_record_added = False # flag to check if the new record has been added

    # Find the latest page number
    page_num = 0
    while os.path.exists(f"{type_name}/page_{page_num}.txt"): 
        page_num += 1
    page_num -= 1

    for i in range(page_num + 1):
        page_path = f"{type_name}/page_{i}.txt" # get the path of the page
        with open(page_path, 'r+') as f:
            primary_key_index = int(f.readline().strip()) # read the primary key index
            vacancy = eval(f.readline().strip()) # read the vacancy list
            lines = [f.readline().strip() for _ in range(9)]
            
            # check if there is a vacancy in the page
            if 0 in vacancy and not new_record_added:  
                for i, is_occupied in enumerate(vacancy):
                    # check if the record is not occupied in the vacancy list
                    if not is_occupied:
                        vacancy[i] = 1 # set the vacancy to occupied
                        lines[i] = record_str # add the record to the page
                        new_record_added = True # set the flag to True
                        break
                
                # If a new record is added, update the page
                if new_record_added:
                    f.seek(0) # move the file pointer to the beginning of the file
                    f.write(str(primary_key_index) + "\n") # write the primary key index
                    f.write(str(vacancy) + "\n") # write the vacancy list
                    f.writelines([line + "\n" for line in lines]) # write the records
                    f.truncate() # truncate the file
                    break

    # If no page has vacancy, create a new page
    if not new_record_added:
        vacancy_list = [1] + [0] * 8 # create a new vacancy list
        new_page = [str(vacancy_list)] + [record_str] + [""] * 8 
        new_page_path = f"{type_name}/page_{page_num + 1}.txt" # get the path of the new page
        # write the new page to the file
        with open(new_page_path, 'w') as f:
            f.write(str(primary_key_index) + "\n") # write the primary key index
            f.writelines([line + "\n" for line in new_page]) # write the page
            f.truncate() # truncate the file


# function to delete a record from a type
def delete_record(type_name, search_primary_key):
    page_num = 0
    page_modified = False # flag to check if the page has been modified

    while os.path.exists(f"{type_name}/page_{page_num}.txt"): # check if the page exists
        page_path = f"{type_name}/page_{page_num}.txt"
        with open(page_path, 'r+') as f:
            primary_key_index = int(f.readline().strip()) # read the primary key index
            vacancy = eval(f.readline().strip()) # read the vacancy list
            lines = [f.readline().strip() for _ in range(9)] # read the records
            
            # check if there is a record in the page
            if 1 in vacancy:
                for i, is_occupied in enumerate(vacancy): # iterate over the vacancy list
                    if is_occupied:
                        record_fields = lines[i].split() # get the record fields
                        record_primary_key = record_fields[primary_key_index] # get the primary key
                        # if the primary key matches the search key, delete the record
                        if record_primary_key == search_primary_key:
                            vacancy[i] = 0 # set the vacancy to unoccupied
                            lines[i] = "" # remove the record
                            page_modified = True # set the flag to True
                            break
                
                # If the page is modified, update the page
                if page_modified:
                    # same operations as in add_record
                    f.seek(0)
                    f.write(str(primary_key_index) + "\n")
                    f.write(str(vacancy) + "\n")
                    f.writelines([line + "\n" for line in lines])
                    f.truncate()
                    break

        page_num += 1 # move to the next page

    return page_modified # return the status of the operation


# function to search for a record in a type
def search_record(type_name, primary_key):
    page_num = 0 # initialize the page number

    while os.path.exists(f"{type_name}/page_{page_num}.txt"): # check if the page exists
        page_path = f"{type_name}/page_{page_num}.txt" # get the path of the page
        with open(page_path, 'r') as f:
            primary_key_index = int(f.readline().strip())
            vacancy = eval(f.readline().strip())
            lines = [f.readline().strip() for _ in range(9)]
            
            # check if there is a record in the page
            if 1 in vacancy:
                for i, is_occupied in enumerate(vacancy): # iterate over the vacancy list
                    if is_occupied:
                        record_fields = lines[i].split() # get the record fields
                        record_primary_key = record_fields[primary_key_index] # get the primary key
                        # if the primary key matches the search key, return the record
                        if record_primary_key == primary_key:
                            return record_fields
        
        page_num += 1 # move to the next page

    return None


# helper function to log the operation in log.txt
def log_operation(operation, status):
    with open('log.txt', 'a') as h:
        h.write(f"{int(time.time())}, {operation}, {status}\n")


# function to process the input file
def in_create_type(operation):
    _, _, type_name, num_fields, primary_key_index, *fields = operation.split() # parse the operation passed as argument
    fields = [(fields[i], fields[i+1]) for i in range(0, len(fields), 2)] # create a list of tuples of field names and types
    
    # check if the input is valid and is in the correct format/length anf return failure if not
    if len(fields) > MAX_NUMBER_OF_FIELDS or len(type_name) > MAX_TYPE_NAME_LENGTH or any(len(f[0]) > MAX_FIELD_NAME_LENGTH for f in fields):
        log_operation(operation, 'failure')
        return
    
    # check if the type already exists and return failure if so
    if os.path.exists(f"{type_name}"):
        log_operation(operation, 'failure')
    
    # in every other case, initialize the type and log the operation as success
    else:
        initialize_type(type_name, primary_key_index)
        log_operation(operation, 'success')


# function to process the input file
def in_create_record(operation):
    _, _, type_name, *values = operation.split() # parse the operation passed as argument
    
    # log failure if the type does not exist
    if not os.path.exists(f"{type_name}"):
        log_operation(operation, 'failure')
        return
    
    with open(f"{type_name}/page_0.txt", 'r') as f: # open the first page file
        primary_key_index = int(f.readline().strip()) # read the primary key index
        primary_key = values[primary_key_index] # get the primary key from the values

    # log failure if the record already exists i.e. the primary key is already in use in search_record
    if search_record(type_name, primary_key):
        log_operation(operation, 'failure')

    # in every other case, add the record and log the operation as success
    else:
        add_record(type_name, values)
        log_operation(operation, 'success')


# function to process the input file
def in_delete_record(operation):
    _, _, type_name, delete_primary_key = operation.split() # parse the operation passed as argument

    # log failure if the type does not exist and return
    if not os.path.exists(f"{type_name}"):
        log_operation(operation, 'failure')
        return
    
    # if the record is deleted, log the operation as success, otherwise log it as failure
    if delete_record(type_name, delete_primary_key):
        log_operation(operation, 'success')
    else:
        log_operation(operation, 'failure')


# function to process the input file
def in_search_record(operation):
    _, _,  type_name, search_primary_key = operation.split() # parse the operation
    record = search_record(type_name, search_primary_key) # search for the record

    # log the operation as success if the record is found, otherwise log it as failure
    if record:
        log_operation(operation, 'success')
        return record # return the record
    else:
        log_operation(operation, 'failure')
        return "" # return an empty string


# main func
def main(input_file):
    # read the operations from the input file
    with open(input_file, 'r') as f:
        operations = f.readlines()
    results = []
    for operation in operations:
        # check the operation and call the appropriate function
        if operation.startswith('create type'):
            in_create_type(operation.strip())
        elif operation.startswith('create record'):
            in_create_record(operation.strip())
        elif operation.startswith('delete record'):
            in_delete_record(operation.strip())
        elif operation.startswith('search record'):
            result = in_search_record(operation.strip())
            # append the result to the results list, only used here since only search record is written in the output.txt
            if result:
                results.append(result)
    # write the results to the output.txt file
    with open('output.txt', 'w') as g:
        g.write("\n".join([" ".join(result) for result in results])) 


if __name__ == "__main__":
    import sys
    input_file = sys.argv[1]
    main(input_file)