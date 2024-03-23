import pandas as pd 
import numpy as np
import os.path as path


#TODO Create model_fit method
#TODO Create 

class Patient:
    
    def __init__(self, ID):
        self.ID = ID
        self.C = self.curve_return('C')
        self.Et = self.curve_return('Et')
        self.Etheta = self.curve_return('Etheta')
        self.params = self.patient_parameters()
    

    def curve_return(self, curve_type: str) -> pd.DataFrame:
        '''
        Fetches the .csv files for C, Et, & Etheta curves and assigns them to
        a class attribute of the same name
        '''
        
        path_dict = {'C': 'data/C_curves',
                    'Et': 'data/Et_curves',
                    'Etheta': 'data/Etheta_curves'}
        
        if curve_type not in path_dict:
            # Raise error if user has messed with valid curve types
            raise ValueError(f"Invalid Curve Type: Expected one of: \
                             {list(path_dict.keys())}")

        curve_path = path.join(path_dict[curve_type],  f"sim{self.ID}.csv")

        return pd.read_csv(curve_path, header=0, index_col= 0)
    
    def patient_parameters(self) -> pd.Series:
        '''
        Grabs the Pandas series of the relevant patient parameters from the 
        master design of experiments (DOE) file. 

        Returns:
        - A pandas series that includes the following information: 
            - COHORT : Cohort # patient belongs to
            - GEOMETRY : Geometry ID number 
            - FLOW_RATE : coronary flow rate in mL/s
            - PERC_DS : Percent diameter stenosis
            - RAMP_ANGLE : The angle of the ramp angle of the stenosis
            - VISCOUS_MODEL : Turublent of laminar CFD solver
            - ARTERIAL_VOLUME : Volume of the artery
            - TIMESTEP_SIZE : Size of time step used in CFD simulation
            - NO_TIMESTEPS : Total # of time steps simulated

        Notes:
            - The values of the pandas series may change depending on model
              real patient arteries. 
        '''

        df = pd.read_csv('data/CASE_PARAMETERS.csv', index_col='CASE_NUM')

        patient_params = df.loc[self.ID]

        return patient_params


if __name__ == '__main__':
    patient_obj = Patient(3)



