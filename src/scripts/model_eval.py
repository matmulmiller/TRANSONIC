import pandas as pd
import matplotlib.pyplot as plt
from src.modules.system_class import System
import os.path as path
from src.modules.utilities import *
import numpy as np
from tqdm import tqdm
from src.modules.model_analysis import MAE_calc, residual_analysis
from src.scripts.E_curves import *

# MANUAL CHANGES YOU HAVE TO MAKE
## - C0 between diffusion and ideal reactor models


def main():

    # Parse args and load config file from YAML
    args = parse_args()
    config = load_config(args.config)

    # Create results folder
    results_folder = create_results_folder(config['wd'])

    # Generate the E curves and E_theta curves
    generate_curves(config['wd'], config['input'], config['doe'])


    # Get the desired model class from config file
    model_name = config['model']
    model_class = get_model_class(f"src.models.{model_name}", model_name)


    # Load design of experiments document
    doe = load_DOE(config['doe'])


    # Create pandas series with same index for fitted params and metrics
    quants = pd.DataFrame(columns=[*config['parameters'], 
                                   'RAE_Etheta', 
                                   'RAE_Et',
                                   'RAE_C',
                                   'MAE_C',
                                   'avg_residual',
                                   'std_residual'], 

                          index=doe.index)

    case_nums = [1, 2, 3, 4, 5] 
    # Iterate through all each system provided in the DOE document
    for id in tqdm(doe.index):

        # Instantiate system and get parameters that define the system from doe
        S = System(id, config['wd'])
        S.get_system_characteristics(doe)


        # Instantiate mathematical model based on config spec
        model_instance = model_class(S.X.TIMESTEP_SIZE, 
                                     S.X.tau, 
                                     #C0=S.X.N0/1045/S.X.ARTERIAL_VOLUME,
                                     bounds=config['parameter_bounds'],
                                     initial_guess=[0.5, 0.5, 0.5])
        

        # Fit model to CFD/experimental C-curve
        model_instance.fit(S.C.time, S.C.mass_fraction)

        # Testing to see if curve_fit method still works
        # curve_fit_bounds = [[0, 0, 0], [1, 1, 1]]
        # model_instance.scipy_curve_fit(S.C.time, S.C.mass_fraction, bounds=curve_fit_bounds)


        # Generate E(t) and E(theta) curves from C-curves
        S.predicted_curves(S.C.time, model_instance.predict(S.C.time))


        # Calculate relative absolute error for model evaluation
        RAE_Etheta = relative_absolute_error(S.Etheta.Et, S.Etheta_pred.Et)
        RAE_Et = relative_absolute_error(S.Et.Et, S.Et_pred.Et)
        RAE_C = relative_absolute_error(S.C.mass_fraction, S.C_pred.mass_fraction)
        MAE_C = MAE_calc(S.C.mass_fraction, S.C_pred.mass_fraction)
        avg_residual, std_residual = residual_analysis(S.C.mass_fraction,
                                                       S.C_pred.mass_fraction)


        # Create a list that includes fitted model params and RAE
        quants_id = model_instance.params
        quants_id = np.append(quants_id, [RAE_Etheta, RAE_Et, RAE_C, 
                                          MAE_C, avg_residual, std_residual], 
                                          axis=0)
        quants.loc[id] = quants_id.tolist()

        # Visualize each fitted line
        plt.figure()
        plt.plot(S.Etheta.time, S.Etheta.Et, label='CFD')
        plt.plot(S.Etheta_pred.time, S.Etheta_pred.Et, label='Predicted', linestyle='--')
        plt.title(f'Q={S.X.FLOW_RATE} mL/s, %DS={S.X.PERC_DS}, SRA={S.X.RAMP_ANGLE}\u00B0')
        plt.legend()
        plt.xlabel('Normalized Time')
        plt.ylabel('Normalized E(t)')
        plt.savefig(path.join(results_folder, f'Q{S.X.FLOW_RATE}_DS{S.X.PERC_DS}_SRA{S.X.RAMP_ANGLE}.png'))
        plt.close()




    # Save results to specified results folder in config file
    quants.to_csv(path.join(results_folder, 'eval_outputs.csv'))


    # Create box plot and save to results folder
    plt.figure
    plt.boxplot([quants['RAE_C'], quants['RAE_Et'], quants['RAE_Etheta']], 
                 notch=True, 
                 bootstrap=7500,
                 labels=['C-Curve', 'E-Curve', 'Normalized E-Curve'])
    plt.title(config['model'])
    plt.ylabel('Count')
    plt.savefig(path.join(results_folder, 'boxplot.png'))
    plt.close()

    # Create a plot of residuals 
    plt.figure()
    plt.errorbar(quants.index.tolist(), y=quants['avg_residual'], 
                 yerr=quants['std_residual'])
    plt.show()


if __name__ == '__main__':
    main()
