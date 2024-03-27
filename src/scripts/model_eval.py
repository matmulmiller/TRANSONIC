import pandas as pd
import matplotlib.pyplot as plt
from src.modules.system_class import System
import os.path as path
import argparse
import yaml
from importlib import import_module
from src.modules.utilities import relative_absolute_error
import numpy as np


#TODO Come up with way to store parameters for each patient
    #TODO Needs to be able to be attached to DOE so must have same index
#TODO Implement LFR to CSTR/PFR parallel model and test


def parse_args():
    parser = argparse.ArgumentParser(description='Pull YAML file entries.')
    parser.add_argument('-c', '--config', required=True, help='Enter location '
                        ' of config file.')
    return parser.parse_args()


def load_config(path):
    with open(path, 'r') as file:
        config = yaml.safe_load(file)
    return config


def get_model_class(module_name, class_name):
    module = import_module(module_name)
    return getattr(module, class_name)


def load_DOE():
    script_dir = path.dirname(path.abspath(__file__))
    src_dir = path.dirname(script_dir)
    project_dir = path.dirname(src_dir)

    doe = pd.read_csv(path.join(project_dir, "data/CASE_PARAMETERS.csv"),
                      index_col=0, header=0, dtype={'VISCOUS_MODEL': 'string'})
    return doe



def main():
    # Parse args and load config file from YAML
    args = parse_args()
    config = load_config(args.config)

    # Get the desired model class from config file
    model_name = config['model']
    model_class = get_model_class(f"src.models.{model_name}", model_name)

    # Load design of experiments document
    doe = load_DOE()

    # Create pandas series with same index for fitted params and metrics
    quants = pd.DataFrame(columns=['Pe1', 'tau1', 'Pe1', 'tau1', 'RAE'], 
                          index=doe.index)


    for id in doe.index:
        # Instantiate system and get parameters that define the system from doe
        S = System(id)
        S.get_system_characteristics(doe)

        # Instantiate mathematical model based on config spec
        model_instance = model_class(S.X.TIMESTEP_SIZE, 
                                     S.X.tau, C0=S.X.N0/1045/S.X.ARTERIAL_VOLUME,
                                     bounds=([0, 0, 0, 0],
                                             [np.inf, np.inf, np.inf, np.inf]))
        
        # Fit model to CFD/experimental C-curve
        model_instance.fit(S.C['time'], S.C['mass_fraction'])

        # Generate E(t) and E(theta) curves from C-curves
        S.predicted_curves(S.C.time, model_instance.predict(S.C.time))

        # Calculate relative absolute error for model evaluation
        RAE = relative_absolute_error(S.Etheta.Et, S.Etheta_pred.Et)

        # Create a list that includes fitted model params and RAE
        quants_id = model_instance.params
        quants_id = np.append(RAE, quants_id)
        quants.loc[id] = quants_id.tolist()

        # Visualize each fitted line
        plt.figure()
        plt.plot(S.C.time, S.C.mass_fraction, label='CFD')
        plt.plot(S.C_pred.time, S.C_pred.mass_fraction, label='Predicted', linestyle='--')
        plt.legend()
        plt.xlabel('Normalized Time')
        plt.ylabel('Normalized E(t)')
        plt.show()

    # Save results to specified results folder in config file
    quants.to_csv(path.join(config['results_folder'], 'results.csv'))

    # Create box plot and save to results folder
    plt.figure
    plt.boxplot(quants['RAE'], notch=True, bootstrap=7500)
    plt.title(config['model'])
    plt.ylabel('Count')
    plt.savefig(path.join(config['results_folder'], 'boxplot.png'))
    plt.close()


if __name__ == '__main__':
    main()
