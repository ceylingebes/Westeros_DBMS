import time
import os

MAX_FIELDS = 6
MAX_TYPE_NAME_LENGTH = 12
MAX_FIELD_NAME_LENGTH = 20
MAX_RECORDS_PER_PAGE = 10


def initialize_type(type_name, primary_key_index):
    filename = f"{type_name}.txt"
    
    #open a new file but does not write anything if it doesn't exist
    if not os.path.exists(filename):
        with open(filename, 'w') as f:

            f.write(str(int(primary_key_index) - 1))
            f.write("\n")
            initial_vacancy_list = str([0] * 9)
            f.write(initial_vacancy_list + "\n")
            for _ in range(8):
                f.write("\n")


def add_record(type_name, values):
    record_str = " ".join(values)
    new_record_added = False
    new_content = []

    with open(f"{type_name}.txt", 'r+') as f:
        primary_key_index = int(f.readline().strip())
        new_content.append(str(primary_key_index) + "\n")
        
        while True:
            # Remember the current position in the file
            current_position = f.tell()
            
            # Read the next 10 lines
            lines = [f.readline().strip() for _ in range(10)]
            if not lines[0]:
                break  # Reached the end of the file
            
            vacancy = eval(lines[0])  # Convert vacancy list string to list
            if 0 in vacancy and not new_record_added:  # Check if there are any vacant slots in the page
                for i, is_occupied in enumerate(vacancy):
                    if not is_occupied:
                        # Mark the vacancy list to indicate this slot is now occupied
                        vacancy[i] = 1
                        # Update the page in the file
                        lines[0] = str(vacancy)
                        lines[i + 1] = record_str
                        new_record_added = True
                        break
            
            new_content.extend([line + "\n" for line in lines])
        
        if not new_record_added:
            # If no vacancy was found in existing pages, add a new page
            vacancy_list = [1] + [0] * 8
            new_page = [str(vacancy_list)] + [record_str] + [""] * 8
            new_content.extend([line + "\n" for line in new_page])
        
        # Write the new content to the file in 10-line chunks
        f.seek(0)
        for i in range(0, len(new_content), 10):
            f.writelines(new_content[i:i+10])
        f.truncate()

        
""" 
def add_record(type_name, values):
    record_str = " ".join(values)
    new_record_added = False
    
    with open(f"{type_name}.txt", 'r+') as f:

        primary_key_index = int(f.readline().strip())
        
        while True:
            # Remember the current position in the file
            current_position = f.tell()
            
            # Read the next 10 lines
            lines = [f.readline().strip() for _ in range(10)]
            if not lines[0]:
                break  # Reached the end of the file
            
            vacancy = eval(lines[0])  # Convert vacancy list string to list
            if 0 in vacancy:  # Check if there are any vacant slots in the page
                for i, is_occupied in enumerate(vacancy):
                    if not is_occupied:
                        # Mark the vacancy list to indicate this slot is now occupied
                        vacancy[i] = 1
                        # Update the page in the file
                        lines[0] = str(vacancy)
                        lines[i + 1] = record_str
                        
                        # Go back to the start of this page in the file
                        f.seek(current_position)
                        f.write("\n".join(lines) + "\n")
                        new_record_added = True
                        break
            
        
        if not new_record_added:
            # If no vacancy was found in existing pages, add a new page
            vacancy_list = [1] + [0] * 8
            new_page = [str(vacancy_list)] + [record_str] + [""] * 8
            f.write("\n".join(new_page) + "\n")
        
        f.close() """
    

def delete_record(type_name, search_primary_key):
    with open(f"{type_name}.txt", 'r+') as f:
        # Read the primary key index from the first line
        primary_key_index = int(f.readline().strip())
        new_content = [str(primary_key_index) + "\n"]  # Start with the primary key index

        while True:
            # Remember the current position in the file
            current_position = f.tell()
            
            # Read the next 10 lines
            lines = [f.readline().strip() for _ in range(10)]
            if not lines[0]:
                break  # Reached the end of the file
            
            vacancy = eval(lines[0])  # Convert vacancy list string to list
            page_modified = False

            if 1 in vacancy:  # Check if there are any occupied slots in the page
                for i, is_occupied in enumerate(vacancy):
                    if is_occupied:
                        record_fields = lines[i + 1].split()
                        record_primary_key = record_fields[primary_key_index]
                        if record_primary_key == search_primary_key:
                            # Mark the vacancy list to indicate this slot is now vacant
                            vacancy[i] = 0
                            # Clear the record in the page
                            lines[i + 1] = ""
                            page_modified = True
            
            if page_modified:
                # Update the vacancy list in the page
                lines[0] = str(vacancy)
            new_content.extend([line + "\n" for line in lines])
        
        # Write the new content to the file in 10-line chunks
        f.seek(0)
        for i in range(0, len(new_content), 10):
            f.writelines(new_content[i:i+10])
        f.truncate()

    return page_modified  # Return True if any page was modified


""" 
def delete_record(type_name, search_primary_key):

    with open(f"{type_name}.txt", 'r+') as f:
        # first line is the primary key index
        primary_key_index = int(f.readline().strip())

        while True:
            # Remember the current position in the file
            current_position = f.tell()
            
            # Read the next 10 lines
            lines = [f.readline().strip() for _ in range(10)]
            if not lines[0]:
                break  # Reached the end of the file
            
            vacancy = eval(lines[0])  # Convert vacancy list string to list
            if 1 in vacancy:  # Check if there are any occupied slots in the page
                for i, is_occupied in enumerate(vacancy):
                    if is_occupied:
                        record_fields = lines[i + 1].split()
                        record_primary_key = record_fields[primary_key_index]
                        if record_primary_key == search_primary_key:
                            # Mark the vacancy list to indicate this slot is now vacant
                            vacancy[i] = 0
                            # Clear the record in the page
                            lines[i + 1] = ""
                            
                            # Update the vacancy list in the page
                            lines[0] = str(vacancy)
                            
                            # Go back to the start of this page in the file
                            f.seek(current_position)
                            f.write("\n".join(lines) + "\n")
                            # f.truncate()  # Truncate the file to remove leftover content
                            
                            f.close()
                            return True  # Record successfully deleted
        f.close()
    return False  # Record not found """

    
def search_record(type_name, primary_key):
    with open(f"{type_name}.txt", 'r') as f:
        primary_key_index = int(f.readline().strip())
        while True:
            lines = [f.readline().strip() for _ in range(10)]
            if not lines[0]:
                break  # Reached the end of the file

            vacancy = eval(lines[0])  # Convert vacancy list string to list
            if 1 in vacancy:  # Check if there are any records in the page
                for i, is_occupied in enumerate(vacancy):
                    if is_occupied:
                        record_fields = lines[i + 1].split()
                        record_primary_key = record_fields[primary_key_index]
                        if record_primary_key == primary_key:
                            f.close()
                            return record_fields  # Record found
        f.close()
    return None


def log_operation(operation, status):
    with open('log.csv', 'a') as h:
        h.write(f"{int(time.time())}, {operation}, {status}\n")


def in_create_type(operation):
    _, _, type_name, num_fields, primary_key_index, *fields = operation.split()
    fields = [(fields[i], fields[i+1]) for i in range(0, len(fields), 2)]
    if len(fields) > MAX_FIELDS or len(type_name) > MAX_TYPE_NAME_LENGTH or any(len(f[0]) > MAX_FIELD_NAME_LENGTH for f in fields):
        log_operation(operation, 'failure')
        return
    if os.path.exists(f"{type_name}.txt"):
        log_operation(operation, 'failure')
    else:
        initialize_type(type_name, primary_key_index)
        log_operation(operation, 'success')


def in_create_record(operation):
    _, _, type_name, *values = operation.split()
    
    with open(f"{type_name}.txt", 'r') as f:
        primary_key_index = int(f.readline().strip())
        primary_key = values[primary_key_index]
        f.close()

    if search_record(type_name, primary_key):
        log_operation(operation, 'failure')
    else:
        add_record(type_name, values)
        log_operation(operation, 'success')
        

def in_delete_record(operation):
    _, _, type_name, delete_primary_key = operation.split()
    if delete_record(type_name, delete_primary_key):
        log_operation(operation, 'success')
    else:
        log_operation(operation, 'failure')


def in_search_record(operation):
    _, _,  type_name, search_primary_key = operation.split()
    record = search_record(type_name, search_primary_key)
    print(record)
    if record:
        log_operation(operation, 'success')
        return record
    else:
        log_operation(operation, 'failure')
        return ""


def main(input_file):
    with open(input_file, 'r') as f:
        operations = f.readlines()
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
                with open('output.txt', 'a') as g:
                    g.write(" ".join(result))
                    g.write("\n")
                    g.close()

if __name__ == "__main__":
    import sys
    input_file = sys.argv[1]
    main(input_file)
