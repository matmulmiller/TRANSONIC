import pandas as pd
import os.path as path
import sys

from PyQt5.QtWidgets import QApplication
from tqdm import tqdm
from src.transonic.scripts.E_curves import *
from src.transonic.modules.system_class import System
from src.transonic.modules.utilities import parse_args, solve, load_config, get_model_class, load_DOE, create_results_folder
from src.transonic.scripts.model_eval import *
from src.transonic.scripts.gui import MainWindow

def split():

    args = parse_args()
    print(args)
    if args.gui:
        print("GUI mode engaged")
        gui_main()
        return 0
    else:
        try:
            cli_main()
            pass
        except Exception as e:
            print(f"{e}")
            return 1
        else:
            return 1

def gui_main():
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
    return 0


def cli_main():

    args_config = input("Type directory: example: testing/configs/base.yaml\n\t~")
    config = load_config(args_config)

    results_folder = create_results_folder(config['wd'])

    # Generates the E curves and E_theta curves
    generate_curves(config['wd'], config['input'], config['doe'])


    # Grabs the desired model class specified in config file
    model_name = config['model']
    model_class = get_model_class(
        f"src.transonic.models.{model_name}", 
        model_name
    )


    # Load design of experiments document
    doe = load_DOE(config['doe'])


    summary_df = pd.DataFrame(
        columns=[
            *config['parameters'],
            'RAE',
            'MAE', 
            'avg_residual', 
            'std_of_residual'], 
        index=doe.index
    )

    solve(doe.index, config, results_folder, model_class, doe, summary_df)#kinda hacky :/ sorry. 
                    #i only did this so that the gui function could eventually use the utilities file and not self-reference the main
    
    # Save results to specified results folder in config file
    summary_df.to_csv(path.join(results_folder, 'eval_outputs.csv'))
    return 0
    
if __name__ == '__main__':
    return_code = split()
    print(f'Return Code: {return_code}')

