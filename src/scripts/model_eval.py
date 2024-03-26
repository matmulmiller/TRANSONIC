import pandas as pd
import matplotlib.pyplot as plt
from src.modules.system_class import System
import os.path as path
import argparse
import yaml
from importlib import import_module
import numpy as np


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


def main():
    args = parse_args()
    config = load_config(args.config)
    model_name = config['model']
    model_class = get_model_class(f"src.models.{model_name}", model_name)


    script_dir = path.dirname(path.abspath(__file__))
    src_dir = path.dirname(script_dir)
    project_dir = path.dirname(src_dir)

    doe = pd.read_csv(path.join(project_dir, "data/CASE_PARAMETERS.csv"),
                      index_col=0, header=0, dtype={'VISCOUS_MODEL': 'string'})

    
    for id in doe.index:
        S = System(id)
        S.get_system_characteristics(doe)

        model_instance = model_class(S.X.TIMESTEP_SIZE, 
                                     S.X.tau, 
                                     bounds=([0, 0], [1, 1]))
        model_instance.fit(S.C['time'], S.C['mass_fraction'])

        S.predicted_curves(S.C.time, model_instance.predict(S.C.time))
        
        plt.figure()
        plt.plot(S.Etheta.time, S.Etheta.Et, label='CFD')
        plt.plot(S.Etheta_pred.time, S.Etheta_pred.Et, label='Predicted')
        plt.xlabel("Normalized Time")
        plt.ylabel("Normalized E-Curve")
        plt.legend()
        plt.show()

if __name__ == '__main__':
    main()
