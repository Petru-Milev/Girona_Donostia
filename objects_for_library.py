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
    def __init__(self, name = False, e_field = False, energy = False, dipole_moment = False, polarizability = False, hyperpolarizability = False, quadrupole_moment = False):
        self.name = name
        self.e_field = e_field
        self.energy = energy
        self.dipole_moment = dipole_moment
        self.polarizability = polarizability
        self.hyperpolarizability = hyperpolarizability
        self.quadrupole_moment = quadrupole_moment
