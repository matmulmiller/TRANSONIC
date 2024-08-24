import pandas as pd 
import numpy as np
import os
import os.path as path
from src.transonic.modules.utilities import create_results_folder
from src.transonic.modules.utilities import load_DOE


def E_curve_generator(c_curve: pd.DataFrame, dt: float, flow_rate: float):
    '''Converts the concentration curve into the probability density function 
    (PDF) E-curve/h-curve.
    
    Parameters:
    - dt : time step size used during tracer injection
    - flow_rate : coronary flow rate in mL/s

    Returns:
    - pd.DataFrame : returns a data frame of the E_curve and time stamps

    Notes:
    - Implementation is based off of the definition of the E(t) curve: 
                        E(t) = flow_rate*C(t) / N_0
        where, N0 is the initial amount of tracer injected
    '''

    E_curve = c_curve.copy(deep=True)  # creates a new df in memory
    E_curve = E_curve.rename(columns={'mass_fraction': 'Et'})
    
    density = 1045  # density of blood
    mass_flow_rate = flow_rate * 10**-6 * density  
    total_tracer_injected = mass_flow_rate * dt

    E_curve.Et = mass_flow_rate * c_curve.mass_fraction / total_tracer_injected
    return E_curve


def E_theta_generator(E_curve, artery_volume, flow_rate):
    '''Normalizes E(t) curve by space time of the artery for ease of comparison.

    Parameters:
    - artery_volume : the volume of the artery found in ANSYS Mesher
    - flow_rate : coronary flow rate in mL/s

    Returns: 
    - pd.DataFrame : returns normalized E(t) curve with time stamps

    Notes:
    - Note that there's no deep copy used for this function. This means that no
    new dataframe is created in memory and all operations are done on the 
    original dataframe. This was done to conserve memory requirements for a 
    large number of C-curves.
    
    '''

    space_time = artery_volume / (flow_rate * 10**-6)

    E_curve.Et = E_curve.Et * space_time
    E_curve.time = E_curve.time / space_time
    E_curve = E_curve.rename(columns={'mass_fraction': 'Etheta', 
                                      'time': 'theta'})
    return E_curve

def generate_curves(wd: str, cCurves: str, doe_path: str) -> None:
    print(f"{cCurves}")
    # Define save location for C curves and create folder
    C_CURVES_DEST_FOLDER = path.join(wd, 'results/C_curves')
    os.makedirs(C_CURVES_DEST_FOLDER, exist_ok=True)
    os.makedirs(path.join(wd, 'results/E_curves'), exist_ok=True)
    os.makedirs(path.join(wd, 'results/Etheta_curves'), exist_ok=True)

    # Load DOE document for getting case parameters
    doe = load_DOE(doe_path)
    # Iterate over every concentration curve in the data directory.
    for dirpath, dirnames, filenames in os.walk(cCurves):
        for filename in filenames:
            if filename.endswith('.out'):
            # Path to each concentration curve in cCurves directory
                src_path = path.join(dirpath, filename)  

                # Concentration curve from CFD simulations
                c_curve = pd.read_csv(src_path, 
                                    index_col=0, 
                                    sep='\s+', 
                                    names=['mass_fraction', 'time'],
                                    header=None)
            

                # Retrive current case number and get necessary parameters from 
                # design of experiment spreadsheet
                case_num=int(
                        filename.replace('sim', '').replace('_tracer_conc.out', '')
                )
                
                case_params = doe.loc[case_num]


                # Create save name for curves files
                save_name = "sim"+str(case_num)+".csv"

                # Save C curve .csv
                c_curve.to_csv(path.join(C_CURVES_DEST_FOLDER, save_name))


                # Create the E curve and save
                E_curve = E_curve_generator(c_curve, 
                                            case_params.TIMESTEP_SIZE, 
                                            case_params.FLOW_RATE)
                E_curve.to_csv(path.join(wd,'results/E_curves', save_name))

                E_theta = E_theta_generator(E_curve, 
                                            case_params.ARTERIAL_VOLUME,
                                            case_params.FLOW_RATE)
                E_curve.to_csv(path.join(wd, 'results/Etheta_curves', save_name))





