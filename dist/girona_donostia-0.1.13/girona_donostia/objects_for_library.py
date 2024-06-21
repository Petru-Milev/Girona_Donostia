import numpy as np

class Gaussian_File:
    def __init__(self, file_name = "name.inp", keywords = "", nproc=False, mem=False, title="Job Name", oldchk=False, oldchk_file=None, chk=False, chk_name=False,
                         charge_multiplicity=(0, 1), geom=False, basis_set=False, wfx=False, Field=False):
        self.file_name = file_name
        self.keywords = keywords
        self.nproc = nproc
        self.mem = mem 
        self.title = title 
        self.oldchk = oldchk
        self.oldchk_file = oldchk_file
        self.chk = chk
        self.chk_name = chk_name
        self.charge_multiplicity = charge_multiplicity
        self.geom = False 
        self.basis_set_gaussian = basis_set
        self.wfx = wfx
        self.Field = Field
    
class Fchk_File():
    """
    This class is used to store the data from a fchk file.
    """
    def __init__(self, name = False, e_field = False, energy = False, dipole_moment = False, polarizability = False, hyperpolarizability = False, quadrupole_moment = False):
        self.name = name
        self.e_field = e_field
        self.energy = energy
        self.dipole_moment = dipole_moment
        self.polarizability = polarizability
        self.hyperpolarizability = hyperpolarizability
        self.quadrupole_moment = quadrupole_moment
    
    def list_propreties(self, directions):
        """
        This function returns a list of propreties of the object if they are present.
        The input is a list of directions for which to return the propreties.
        """
        map_directions_1 = {"x" : 0, "y" : 1, "z" : 2, "xx" : 0, "yy" : 2, "zz" : 5, "xxx" : 0, "yyy" : 3, "zzz" : 9}
        map_dipole = {"x" : 0, "y" : 1, "z" : 2}
        map_polarizability = {"xx" : 0, "xy" : 1, "yy" : 2, "xz" : 3, "yz" : 4, "zz" : 5}
        map_hyperpolarizability = {"xxx" : 0, "xxy" : 1, "xyy" : 2, "yyy" : 3, "xxz" : 4, "xyz" : 5, "yyz" : 6, "xzz" : 7, "yzz" : 8, "zzz" : 9}
        main_directions = []      #if direction x, y or z is specified, it will be saved here, later to print also the xx, yy, zz, xxx, yyy, zzz
        secondary_directions = []   #All other directions which will be printed only once
        for char in directions:     #Separating the directions in the input file
            if char.lower() in map_dipole:
                main_directions.append(char)
            else: secondary_directions.append(char)

        new_list = [["Name", "E_Field_X", "E_Field_Y", "E_Field_Z", "Energy", "Dipole_Moment", "Polarizability", "Hyperpolarizability"]]
        new_list.append([])         #Creating the list in the form [[*names], [*values]
        new_list[1].append(self.name)
        new_list[1].extend(self.e_field)
        new_list[1].append(self.energy)
        if self.dipole_moment:          
            count = 0
            position = new_list[0].index("Dipole_Moment")
            del new_list[0][position]
            for i in main_directions:                   #Printing it for all the specified main directions
                new_list[0].insert(position + count, "Dipole_Moment_" + i.lower())
                new_list[1].append(self.dipole_moment[map_directions_1[i.lower()]])
                count += 1
        else: 
            count = 0
            position = new_list[0].index("Dipole_Moment")
            del new_list[0][position]
            for i in main_directions:                   #Printing it for all the specified main directions
                new_list[0].insert(position + count, "Dipole_Moment_" + i.lower())
                new_list[1].append(np.NaN)
                count += 1
            print("Dipole_Moment is not present in the file" + self.name)

        if self.polarizability:
            count = 0
            position = new_list[0].index("Polarizability")
            del new_list[0][position]
            for i in main_directions:                  #Printing it for all the specified main directions       
                new_list[0].insert(position + count, "Polarizability_" + 2*i.lower())
                new_list[1].append(self.polarizability[map_directions_1[2*i.lower()]])
                count += 1
            if secondary_directions:                #Printing it for all the specified secondary directions
                for i in secondary_directions:
                    if i.lower() in map_polarizability:
                        new_list[0].insert(position + count, "Polarizability_" + i.lower())
                        new_list[1].append(self.polarizability[map_polarizability[i.lower()]])
                        count += 1
        else: 
            count = 0
            position = new_list[0].index("Polarizability")
            del new_list[0][position]
            for i in main_directions:                  #Printing it for all the specified main directions       
                new_list[0].insert(position + count, "Polarizability_" + 2*i.lower())
                new_list[1].append(np.NaN)
                count += 1
            print("Polarizability is not present in the file" + self.name)
        
        if self.hyperpolarizability:
            count = 0
            position = new_list[0].index("Hyperpolarizability")
            del new_list[0][position]
            for i in main_directions:
                new_list[0].insert(position + count, "Hyperpolarizability_" + 3*i.lower())
                new_list[1].append(self.hyperpolarizability[map_directions_1[3*i.lower()]])
                count += 1
            if secondary_directions:
                for i in secondary_directions:
                    if i.lower() in map_hyperpolarizability:
                        new_list[0].insert(position + count, "Hyperpolarizability_" + i.lower())
                        new_list[1].append(self.hyperpolarizability[map_hyperpolarizability[i.lower()]])
                        count += 1

        else: 
            count = 0
            position = new_list[0].index("Hyperpolarizability")
            del new_list[0][position]
            for i in main_directions:
                new_list[0].insert(position + count, "Hyperpolarizability_" + 3*i.lower())
                new_list[1].append(np.NaN)
                count += 1
            print("Hyperpolarizability is not present in the file" + self.name)
        return new_list
