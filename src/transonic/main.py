import pandas as pd
import os.path as path
import sys
import PyQt5

from PyQt5 import QtCore, QtGui, uic, QtWidgets
from PyQt5.QtWidgets import QApplication
from tqdm import tqdm
from src.transonic.scripts.E_curves import *
from src.transonic.modules.system_class import System
from src.transonic.modules.utilities import parse_args, solve, load_config, get_model_class, load_DOE, create_results_folder
from src.transonic.scripts.model_eval import *
from src.transonic.scripts.gui import MainWindow

def interface() -> int:

    args = parse_args()
    if args.gui:
        if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
            PyQt5.QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

        if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
            PyQt5.QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
        print("GUI mode engaged.")
        gui_main()
    else:
        print("CLI mode engaged.")
        cli_main()
    return 0

def gui_main() -> int:
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
    return 0


def cli_main() -> int:
    
    config_path = input("Please provide the directory of the config file.\n\t~")
    
    if os.path.exists(config_path) == False:
        print(f"Warning: No file found in the provided path: {config_path}")
    
    try: 
        config_data = load_config(config_path)
        results_dir = create_results_folder(config_data['wd'])
    except FileNotFoundError:
        print(f"Error in finding config file.\n")
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

    return 0
    
if __name__ == '__main__':
    return_code = interface()
    print(f'Return Code: {return_code}')

