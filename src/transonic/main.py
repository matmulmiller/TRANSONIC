import pandas as pd
import os.path as path
import sys
import PyQt5

from PyQt5 import QtCore, QtGui, uic, QtWidgets
from PyQt5.QtWidgets import QApplication
from tqdm import tqdm
from src.transonic.scripts.E_curves import *
from src.transonic.modules.system_class import System
from src.transonic.modules.utilities import parse_args, solve, load_config, get_model_class, load_DOE, create_results_folder, confirm_choice, default_params, default_bounds, clear_screen
from src.transonic.scripts.model_eval import *
from src.transonic.scripts.gui import MainWindow
from src.transonic.modules.style import emph1, emph2, warn, banners, in_color, symbols

models = {
    "Tanks in series": "TANKS_IN_SERIES",
    "Laminar flow reactor dead zone continuous stir tank reactor": "LFR_DZ_CSTR",
    "Taylor dispersion": "TAYLOR_DISPERSION",
    "Double dispersion": "DOUBLE_DISPERSION"
}

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

def get_dirs() -> tuple[str, str]:
    file_dir = os.path.abspath(os.path.dirname(__file__))
    src_path = os.path.abspath(os.path.dirname(file_dir))
    root_dir = os.path.abspath(os.path.dirname(src_path))
    return [file_dir, src_path, root_dir] #returns directory of main.py (transonic)and directory transonic is stored in (src)

def gui_main() -> int:
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
    return 0

def get_path(dir_name: str):
    cwds = get_dirs()

    while True:
        try:
            if dir_name is not None:
                path = input(f"{cwds[0]}/{dir_name}")
            else:
                path = input(f"{cwds[0]}/")
            os.makedirs(os.path.abspath(os.path.dirname(path)), exist_ok=True)
            return os.path.abspath(path)
        except Exception as e:
            print(f"\nError: {e}. Try again.")

def make_case():

    #User selects the model
    print(f"\n Select a model from below by typing its associated number.")
    for idx, (k, v) in enumerate(models.items()):
        print(f"\n{emph1(idx+1)}: {emph2(k)}")
        max_idx = idx+1
    
    while True: 
        try:
            model_idx = int(input(f"> "))
            if model_idx < 1 or model_idx > max_idx:
                raise Exception
            break
        except ValueError:
            print(f"\nError. Value must be an integer (1, 2, etc.)")
            continue
        except Exception:
            print(f"\nValue must be an integer between 0 and {max_idx + 1}.")

    for idx, (k, v) in enumerate(models.items()):
        if idx+1 == model_idx:
            model = v
    
    #User determines if default parameters should be used for their model
    if confirm_choice(header="Would you like to use default parameters for the model?"):
        params = default_params[model]
    else:
        print(f"\nThis feature is still under construction!")
    
    #User determines if default bounds should be used for their model
    if confirm_choice(header="Would you like to use default bounds for the model?"):
        bounds = default_bounds[model]
    else:
        print(f"\nThis feature is still under construction!")

    #User selects the DOE path, wd, and data input path
    while True:
        print(f"\nPlease provide path for DOE.")
        doe_path = get_path(dir_name="DOEs/")
        # if not os.path.exists(doe_path):f
        #     print(f"{doe_path} not found.")
        if not confirm_choice(header=f"Current working directory: {get_dirs()[0]}. Okay?", y_option="Using working directory.", n_option="Type new working directory:\n"):
            wd = get_path()
        else:
            wd = get_dirs()[0]
        print(f"\nPlease provide a path for the data.")
        data_input_path = get_path(dir_name="data_raw/")
        if confirm_choice(header=f"\nDOE path: {doe_path}\nWorking directory: {wd}\nData path: {data_input_path}\nConfirm?"):
            break
        else:
            continue
    
    #creates the yaml file from user inputs
    try:
        tmp_dir = os.path.join(get_dirs()[1], "tmp")
        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir)
        with open(os.path.join((tmp_dir),"config.yaml"),"w") as yf:
            yf.write(f"model: \'{model}\'\n\ndoe: \'{doe_path}\'\n\nwd: \'{wd}\'\n\ninput: \'{data_input_path}\'\n\nparameters:{params}\n\nparameter_bounds: {bounds}")
        print("\nSuccess! Config file generated")
    except:
        raise Exception
    
def invalid_option():
    print(f"\nNot a valid option. Type \'h\' for help.")

def help():
    commands = {
        "new": "Create a new config file through guided prompts.",
        "run": "Run a case with a config file",
        "adv": "Create/edit a config file by changing values direclty without prompts.",
        "clear": "Clear your screen"
    }
    print(f"\nThe TRANSONIC CLI currently supports the functions below. Simply type the {emph1("highlighted words")} to achieve the {emph2("descriptions")}.")
    for k, v in sorted(commands.items()):
        print(f"\n{emph1(k)}: {emph2(v)}")
    
def run_case():
    pass

def easter_egg():
    print(f"\nPim, her name was Shrimpina. She's a shrimp.")

def cli_main():
    commands = {
        "new": make_case,
        "run": run_case,
        "help": help,
        "h": help,
        "clear": clear_screen,
        "michaelstyle": easter_egg
    }
    clear_screen()
    banner = banners.get("shifted_box")
    color = banner[0]
    title = banner[1]
    print(f"{in_color(color,title)}\n")

    
    print(f"\nTyping \'help\' will bring up the list of commands and \'q\' will quit the program.")
    while True:
        usr_command = input(f"\nType a command\n> ").strip().lower()
        if usr_command == 'q':
            break
        commands.get(usr_command, invalid_option)()
    
    
    return 0
    

# def cli_main() -> int:
    
#     config_path = input("Please provide the directory of the config file.\n\t~")
    
#     if os.path.exists(config_path) == False:
#         print(f"Warning: No file found in the provided path: {config_path}")
    
#     try: 
#         config_data = load_config(config_path)
#         results_dir = create_results_folder(config_data['wd'])
#     except FileNotFoundError:
#         print(f"Error in finding config file.\n")
#         pass

#     # Generates the E curves and E_theta curves
#     generate_curves(config_data['wd'], config_data['input'], config_data['doe'])

#     # Grabs the desired model class specified in config file
#     model_class = get_model_class(config_data)

#     # Load design of experiments document
#     doe = load_DOE(config_data['doe'])

#     # Solve for the given system
#     summary_df = solve(doe, config_data, results_dir, model_class)
    
#     # Save results to specified results folder in config file
#     summary_df.to_csv(path.join(results_folder, 'eval_outputs.csv'))

#     return 0
    
if __name__ == '__main__':
    return_code = interface()
    print(f'Return Code: {return_code}')

