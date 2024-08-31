import numpy as np
import pandas as pd
import argparse
import yaml
from importlib import import_module
import os.path as path
import os
import platform
from src.transonic.modules.style import warn, emph1, emph2
from tqdm import tqdm
from src.transonic.modules.system_class import System
from src.transonic.scripts.E_curves import generate_curves
from src.transonic.scripts.model_eval import fit_model, generate_model_summary, append_model_summary, visualize_fit

default_params ={
    'LFR_DZ_CSTR': '\n- [0.01, 0.99]\n- [0.01, 0.99]',
    'TANKS_IN_SERIES': '\n- \'n\''
}

default_bounds ={
    'LFR_DZ_CSTR': '\n- [0.01, 0.99]\n- [0.01, 0.99]',
    'TANKS_IN_SERIES': '\n- [1, \'105\']'
}

def type_check(dtype, value) -> bool:
    '''
    Checks if the given dtype is a general match of the dtype for a given value

    Paramters:
    - dtpye : the data type you want to compare to
    - value : the value whose data type you want to check

    Returns:
    - bool_val : A boolean value about whether the data types are generally same

    Notes:
    - Trying to check if two variables, one from numpy/pandas and the other just
      normal python data type, (e.g. int32 vs int) in a general way is like 
      making love to a blender.
    '''

    try: 

        if type(value) == dtype:
            bool_val = True
        elif dtype==np.int32 and type(value)==int:
            bool_val = True
        elif dtype==pd.StringDtype() and type(value)==str:
            # B/c f*** me, pandas thought it would be cool if they had their own
            # string data type
            bool_val = True
        else:
            bool_val = False

        return bool_val

    except TyperError as e:
        # Raised if value can't be convert to numpy for example
        print(f"Type Error: {e}")
        return False
    except ValueError as e:
        # Raised if dtype is not a valid numpy data type 
        print(f"Value Error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return False 
        
def confirm_choice(y_option="Choice saved.", n_option="Choice not saved.", header="Confirm choice?"):
    while True:
        choice = input(f"\n{header} [y]/n\n>").lower()
        if choice == 'y':
            print(f"\n{y_option}")
            return True
        elif choice == 'n':
            print(f"\n{n_option}")
            return False
        else:
            print("Invalid choice. Type \'y\' or \'n\'")
        
def run_from_config(config_path):
    
    if os.path.exists(config_path) == False:
        print(f"{warn("Warning")}: No file found in the provided path: {config_path}")

    try: 
        config_data = load_config(config_path)
        results_dir = create_results_folder(config_data['wd'])

    except FileNotFoundError:
        print(f"{warn("error")}: Could not find config file.")
        pass

    # Generates the E curves and E_theta curves
    generate_curves(config_data['wd'], config_data['input'], config_data['doe'])

    # Grabs the desired model class specified in config file
    model_class = get_model_class(config_data)

    # Load design of experiments document
    doe = load_DOE(config_data['doe'])

    # Solve for the given system
    summary_df = solve(doe, config_data, results_dir, model_class)
    
    # Save results to specified results folder in config file
    summary_df.to_csv(path.join(results_dir, 'eval_outputs.csv'))

def ID_retrieval(df: pd.DataFrame, criteria: dict):
    '''
    Returns the indices of the given DataFrame where a set of criteria is true.

    Parameters:
    - df : This is the design of experiments document where parameters are kept
    - criteria : a dictionary of the form {'critiera': [value1, value2, ...]}

    Returns:
    - A pd.Series object of the indices/labels where the criteria are met. 
    '''

    # Create a pd.Series w/ same index as df and all TRUE values
    filter_series = pd.Series(True, index=df.index)  

    # Iterate through criteria dictionary
    for column, values in criteria.items():

        # Notify if the user provides a criteria that doesn't exist
        if column not in df.columns:
            raise ValueError(f"{column} is not an existing criteria.")
        
        # Check to see if data type in criteria is same as that in df
        if not type_check(df[column].dtype, values[0]):
            raise ValueError(f"Data types do not match for {column}. "
                            f"{column} data type is: {df[column].dtype}"
                            f" and the entered value is type {type(values[0])}")

        # Update filter by using the &= operatoer (e.g. True &= False -> False)
        filter_series &= df[column].isin(values)

    return df.index[filter_series]


def parse_args():
    parser = argparse.ArgumentParser(description='Pull YAML file entries and optionally add GUI.')
    # parser.add_argument('--config','-c', required=False, const=None help='Enter location '
    #                     ' of config file.')
    parser.add_argument('--gui', '-w', action='store_true', help='Deploys the GUI.')
    return parser.parse_args()


def load_config(path):
    with open(path, 'r') as file:
        config = yaml.safe_load(file)

    for row in config['parameter_bounds']:
        for i, value in enumerate(row):
            if value == 'INF':
                row[i] = np.inf 
            elif value == '-INF':
                row[i] = -np.inf

    return config

def get_model_class(config_yaml_data):
    model_name = config_yaml_data['model']
    module_name = f"src.transonic.models.{model_name}"
    module = import_module(module_name)
    return getattr(module, model_name)


def load_DOE(doe_path):
    doe = pd.read_csv(doe_path, index_col=0, header=0, 
                      dtype={'VISCOUS_MODEL': 'string'})
    return doe

def clear_screen():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")

def create_results_folder(wd):
    result_dir = path.join(wd, 'results')
    os.makedirs(result_dir, exist_ok=True)
    return result_dir

def solve(doe: pd.DataFrame, config: dict, results_dir: str, model_class) -> pd.DataFrame:

    summary_df = pd.DataFrame(
        columns=[
            *config['parameters'],
            'RAE',
            'MAE', 
            'avg_residual', 
            'std_of_residual'], 
        index=doe.index
    )

    for id in tqdm(doe.index):
        S = System(id, config['wd'])
        S.get_system_characteristics(doe)

        model_instance = fit_model(model_class, None, S, config)

        S.predicted_curves(S.C.time, model_instance.predict(S.C.time))

        metrics = generate_model_summary(S) 

        summary_df = append_model_summary(
            summary_df, 
            id, 
            metrics, 
            model_instance
        )
        visualize_fit(S, results_dir)
        
    return summary_df

if __name__ == '__main__':
    doe = pd.read_csv("data/CASE_PARAMETERS.csv", 
                      dtype={'VISCOUS_MODEL': 'string'})
    print(doe.dtypes)

    criteria = {'FLOW_RATE': [4.0], 
                'PERC_DS': [50],
                'RAMP_ANGLE': [60],
                'VISCOUS_MODEL': ['TURBULENT']}

    idxs = ID_retrieval(doe, criteria)

    print(idxs)
