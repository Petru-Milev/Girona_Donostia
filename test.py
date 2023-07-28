import numpy as np
import os
import re
from functions_for_library import *

def change_kw(path_to_file, keywords):
    with open(path_to_file, "r") as file:
        lines = file.readlines()
    with open(path_to_file, "w") as file:
        introducing_new_kw = False
        gaussian_file_started = True
        count_kw_introduced = 0
        for line in lines:
    
            if "#" in line.strip() and gaussian_file_started:
                introducing_new_kw = True

            if introducing_new_kw:
                if count_kw_introduced == 0:
                    for i, line in enumerate(keywords):
                        file.write(line + "\n" if i != len(keywords) - 1 else line)
                    gaussian_file_started = False
                    count_kw_introduced += 1
                if line.strip() == "":
                    introducing_new_kw = False
                    gaussian_file_started = True
            if gaussian_file_started:
                file.write(line)
    return 

def read_input_file(path_to_file, extension = ".com"):
    

    def read_block_in_file(path_to_file, kw_start):
        with open(path_to_file, "r") as file:
            lines = []
            record = False
            count = 0
            for line in file:
                if kw_start in line.strip() and count == 0:
                    record = True
                    count += 1
                    continue
                if record:
                    if kw_start in line.strip():
                        record = False
                        break
                    else: lines.append(line.strip())
        return lines

    primary_functions = {"gen_e_field_direction": 1, "update_old_chk":3, "basis_set" : 2, "change_kw": 3, "delete": 4}
    path_to_folder = "/".join(path_to_file.split("/")[:-1])
    
    with open(path_to_file, "r") as file:
        kw_lines = []
        for i, line in enumerate(file):
            if line.strip() == "":
                line_kw_end = i
                break
            else: kw_lines.append(line.strip())
    keywords = []
    for line in kw_lines:
        keywords.extend(re.split(r'\s(?![^(]*\))',line.strip()))
    keywords = keywords[1:]

    with open(path_to_file, "r") as file:
        original_file_lines = []
        record_file = False
        for line in file:
            if "***start_gaussian_file***" in line.strip().lower():
                record_file = True
                continue
            if record_file:
                original_file_lines.append(line)
    kw_without_input_for_function = []
    input_for_function = []
    for i in keywords:
        kw_without_input_for_function.append(i.split("(")[0])
        input_for_function.append(re.findall(r'\((.*?)\)', i) if re.findall(r'\((.*?)\)', i) else None)

    print("list of keywords: ", kw_without_input_for_function)

    if "gen_e_field_direction" in kw_without_input_for_function:
        index = kw_without_input_for_function.index("gen_e_field_direction")
        inp = input_for_function[index]
        if inp == None:
            print("No input for function gen_e_field_direction")
            print("Please specify the input for the function gen_e_field_direction")
            print("Syntax: gen_e_field_direction(c1, c2, c3, start, finish, step, type_coordinates, type_space, (not_necessary)extension of the file)")
        new_kw = False
        if "new_kw" in keywords:
            new_kw = read_block_in_file(path_to_file, "kw_e_field_calc")
        inp = inp[0].split(" ")
        generate_files_e_field_in_one_direction(path_to_file, *inp, lines = original_file_lines, new_kw=new_kw)
    
    if "update_old_chk" in kw_without_input_for_function:
        index = kw_without_input_for_function.index("update_old_chk")
        inp = input_for_function[index]
        if inp == None:
            reference = False
            print("All files will be referencing file n-1")
        else: 
            reference = inp[0]
            if "zero" in reference.lower():
                for file in os.listdir(path_to_folder):
                    if file.endswith(extension):
                        with open(os.path.join(path_to_folder, file), "r") as file_1:
                            lines = file_1.readlines()
                            for line in lines:
                                if "0.0 0.0 0.0" in line:
                                    reference = file
                                    break
            print("Selected file for reference is: " + reference)

        update_oldchk_for_files_in_a_folder(path_to_folder, file_extension=".com", reference_from_input=reference)




def generate_files_e_field_in_one_direction(path_to_file, c1, c2, c3, start, finish, step, type_coordinates, type_space, extension = ".com", lines = "" ,new_kw = False):
    c1, c2, c3 = np.float128(c1), np.float128(c2), np.float128(c3)
    start, finish = np.float128(start), np.float128(finish)
    if type_space == "linear":
        step = int(step)
    elif type_space == "log":
        step = int(step)
    else: step = np.float128(step)
    map_directions = {"0" : "X", "1" : "Y", "2" :"Z"}              #Dictionary to map the index of the direction into the letter
    #Generate the values of the electric field over the specified direction
    e_fields = vary_e_field_in_certain_direction(c1, c2, c3, var_range = [start, finish, step], type_coordinates = type_coordinates, type_space = type_space)
    for field in e_fields:
        field = list(field)
        if field[0] == 0 and field[1] == 0 and field[2] == 0:
            continue
        else: directions = [map_directions[str(i)] for i, x in enumerate(field) if x != 0]
    for field in e_fields:                                         #Looping to creating the files
        #Creating the name of the file. File name will have the following format:
        #Input_kw example_test_X-1.41e+00_Y-1.41e+00
        if field[0] == 0 and field[1] == 0 and field[2] == 0:
            file_name  = path_to_file[:-4] + "_" + "_".join([str(x) + "+0" for x in directions]) + extension
        else: file_name = path_to_file[:-4] + "_" + "_".join(["".join((map_directions[str(i)], "+" + "{:.2e}".format(x) if x > 0 else "{:.2e}".format(x))) for i, x, in enumerate(field) if x!= 0]) + extension
        with open (file_name, "w") as file:                        #Creating the file                           
            for line in lines:                                     #Writting line of the file
                file.write(line)
            file.write(" ".join([str(x) for x in field]) + "\n")
        change_line_in_file(file_name, "%chk", "%chk=" + file_name.split("/")[-1][:-4] + ".chk")
        if new_kw:
            if field[0] == 0 and field[1] == 0 and field[2] == 0:
                None
            else: change_kw(file_name, new_kw)



path = "/Users/petrumilev/Documents/projects_python/File_for_proj_girona_donostia/Test_Input/Example_how_we_want.txt"



print(read_input_file(path))