import pandas as pd 
import numpy as np
import os.path as path


class System:
    """
    This class is designed to hold all the experimental data for the system 
    being investigated. This includes concentration and RTD curves as well as 
    the independent variables of the system such as flow, volume, and geometry
    specifciations. 

    Attributes:
    - ID : the unique value that identifies the system from other systems
    - C : the exit concentration curve
    - Et : the E curve
    - Etheta : the E curve normalized by space time
    """
    
    def __init__(self, ID, wd):
        """
        Initializes the class instance and grabs the experimental curve data
        """

        self.ID = ID
        self.wd = wd
        self.C = self.curve_return('C')
        self.Et = self.curve_return('Et')
        self.Etheta = self.curve_return('Etheta')
    

    def curve_return(self, curve_type: str) -> pd.DataFrame:
        """
        Fetches the .csv files for C, Et, & Etheta curves and assigns them to
        a class attribute of the same name
        """
        
        path_dict = {'C': f"{path.join(self.wd,'results/')}C_curves",
                    'Et': f"{path.join(self.wd,'results/')}E_curves",
                    'Etheta': f"{path.join(self.wd,'results/')}Etheta_curves"}
        
        if curve_type not in path_dict:
            # Raise error if user has messed with valid curve types
            raise ValueError(f"Invalid Curve Type: Expected one of: \
                             {list(path_dict.keys())}")

        curve_path = path.join(path_dict[curve_type],  f"sim{self.ID}.csv")

        return pd.read_csv(curve_path, header=0, index_col= 0)
    
    
    def get_system_characteristics(self, df) -> pd.Series:
        """
        Accepts a design of experiments DataFrame as input. Given the system ID,
        deep copies the defining parameters of the system to a new pandas series
        and assigns it to the class attribute 'X'.

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
            - N0 : The initial mass of tracer injected 
            - tau : spacetime of the system defined by volume / flow rate
            - rho : the density of the fluid in kg m^-3

        Notes:
            - The system parameters will obviously change for different types of 
            system (e.g. coronary arteries versus chemical reactors).

            - N0 is technically equation to mass_fraction*mass_flow_rate*dt but
              for these experiments, initial mass_fraction was equal to 1.
        """

        X = df.loc[self.ID].copy(deep=True)
        X['rho'] = 1045
        X['N0'] = X.FLOW_RATE * 10**-6 * X.rho * X.TIMESTEP_SIZE
        X['tau'] = X.ARTERIAL_VOLUME/X.FLOW_RATE/10**-6

        self.X = X

    def predicted_curves(self, t_range, C_predicted):
        self.C_pred = pd.DataFrame({'time': t_range, 'mass_fraction': C_predicted})
        
        self.Et_pred = self.C_pred.copy(deep=True)
        self.Et_pred.rename(columns={'mass_fraction': 'Et'}, inplace=True)
        self.Et_pred.Et = (self.X.FLOW_RATE * 10**-6 * self.X.rho) * \
            (self.Et_pred.Et/self.X.N0)

        self.Etheta_pred = self.Et_pred.copy(deep=True)
        self.Etheta_pred.Et = self.Etheta_pred.Et * self.X.tau
        self.Etheta_pred.time = self.Etheta_pred.time/self.X.tau
    

if __name__ == '__main__':
    patient_obj = System(3)



