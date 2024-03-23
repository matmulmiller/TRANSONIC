import pandas as pd 
import numpy as np
import os.path as path


#TODO Might be a good idea for each simulation to be an object of a class
#TODO object can contain the parameters for each case and all the curves

class Patient:
    
    def __init__(self, ID):
        self.ID = ID
        self.c_curve = pd.read_csv("")
    

    def curve_return(self, curve_type):
        path_dict = {'C': 'data/C-curves',
                       'Et': 'data/Et_curves',
                       'Etheta': 'data/Etheta_curves'}

        curve_path = path.join(path_dict,[curve_type],  f"sim")
