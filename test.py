import numpy as np
import os

def update_oldchk_for_files_in_a_folder(folder_path, file_extension = ".com", reference = False):
    """
    This function updates the %oldchk= line in the Gaussian input files in a folder.
    :param folder_path: the path to the folder containing the Gaussian input files
    :param file_extension: the extension of the Gaussian input files
    :param reference: the name of the reference file
    :return: None
    """

    def change_oldchk_file(file_path, new_oldchk_name):                # This function changes the %oldchk= line in a Gaussian input file
        old_chk_line = "%oldchk="                                      # The function takes the path to the file and the name of the new chk file
        with open(file_path, "r") as file_gaussian:                    
            lines = file_gaussian.readlines()
        for i, line in enumerate(lines):
            if old_chk_line in line.lower():
                lines[i] = "%oldchk=" + str(new_oldchk_name) + "\n"
                with open(file_path, "w") as file_1:
                    file_1.writelines(lines)
                break

    file_list = os.listdir(folder_path)                    # This part of the function sorts the files in the folder by the number in the file name     
    file_list = [file_name for file_name in file_list if file_name.endswith(file_extension)]
    file_list = [(np.float64(x.split("_")[-1][1:-4]), x) for x in file_list]  # The number is the last part of the file name, after the last underscore and before the file extension
    file_list = sorted(file_list, key=lambda x: x[0])                   # The files are sorted by the number
    zero_index = None                                                   # The index of the file with the number 0 is found
    for i in file_list:
        if np.round(i[0],0) == 0:
            zero_index = file_list.index(i)                            # The index of the file with the number 0 is found
            break
    file_list = [x[1] for x in file_list]                               # The file names are extracted from the list of tuples
    if reference is False:                                             # If no reference file is given, all the files are referenced to the file n-1
        reference = file_list[zero_index]
        for i in range(zero_index+1, len(file_list)):                   
            change_oldchk_file(os.path.join(folder_path, file_list[i]), reference[:-4] + ".chk")
            reference = file_list[i]
        reference = file_list[zero_index]
        for i in range(zero_index-1, -1, -1):
            change_oldchk_file(os.path.join(folder_path, file_list[i]), reference[:-4] + ".chk")
            reference= file_list[i]
    return
path = ("/Users/petrumilev/Documents/projects_python/File_for_proj_girona_donostia/Test_Input")
update_oldchk_for_files_in_a_folder(path, file_extension=".txt")