import numpy as np
import os

def change_oldchk_file(file_path, new_oldchk_name):
    old_chk_line = "%oldchk="
    with open(file_path, "r") as file_gaussian:
        lines = file_gaussian.readlines()
    
    found = False

    for i, line in enumerate(lines):
        if old_chk_line in line:
            lines[i] = "%oldchk=" + str(new_oldchk_name) + "\n"
            with open(file_path, "w") as file_1:
                file_1.writelines(lines)
            break

#change_oldchk_file("/Users/petrumilev/Documents/projects_python/project_girona_donostia/Test_file_0_X_1.0_Y_0_Z_0.inp", "changed_oldchk_file_name.fchk")

def update_oldchk_for_files_in_a_folder(folder_path, file_extension, type_of_change, reference = False):

    def change_oldchk_file(file_path, new_oldchk_name):
    old_chk_line = "%oldchk="
    with open(file_path, "r") as file_gaussian:
        lines = file_gaussian.readlines()
    
    found = False

    for i, line in enumerate(lines):
        if old_chk_line in line:
            lines[i] = "%oldchk=" + str(new_oldchk_name) + "\n"
            with open(file_path, "w") as file_1:
                file_1.writelines(lines)
            break

    file_list = os.listdir(folder_path)
    file_list = [file_name for file_name in file_list if file_name.endswith(file_extension)]
    file_list = sorted(file_list)
    if type_of_change == "n_minus_one":
        n_min_one = file_list[0]
        for i, file_name in enumerate(file_list[1:]):
            change_oldchk_file(os.path.join(folder_path, file_name), n_min_one)
            n_min_one = file_list[i]
    elif type_of_change == "reference":
        reference_file = [file_name for file_name in file_list if reference in file_name]
        for file_name in file_list:
            if file_name == reference_file:
                continue
            else: change_oldchk_file(os.path.join(folder_path, file_name), reference_file[0])

update_oldchk_for_files_in_a_folder("/Users/petrumilev/Documents/projects_python/project_girona_donostia", ".inp", "reference", reference = "index_1")


file_list = os.listdir("/Users/petrumilev/Documents/projects_python/project_girona_donostia")
file_list = [file_name for file_name in file_list if file_name.endswith(".inp")]
for i in file_list:
    print(i)

sorted_file = sorted(file_list)
for i in sorted_file:
    print(i)

