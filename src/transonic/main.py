import pandas as pd
import os.path as path
import sys
import PyQt5

from PyQt5 import QtCore, QtGui, uic, QtWidgets
from PyQt5.QtWidgets import QApplication
from tqdm import tqdm
from src.transonic.scripts.E_curves import *
from src.transonic.modules.system_class import System
from src.transonic.modules.utilities import parse_args, solve, load_config, get_model_class, load_DOE, create_results_folder, confirm_choice, default_params, default_bounds, clear_screen, run_from_config 
from src.transonic.scripts.model_eval import *
from src.transonic.scripts.gui import MainWindow 
from src.transonic.modules.style import emph1, emph2, warn, banners, in_color, symbols

models = {
    "Tanks in series": "TANKS_IN_SERIES",
    "Laminar flow reactor dead zone continuous stir tank reactor": "LFR_DZ_CSTR",
    "Taylor dispersion": "TAYLOR_DISPERSION",
    "Double dispersion": "DOUBLE_DISPERSION"
}

paths = {
    "Working Directory": "",
    "DOE path": "",
    "Data directory": ""
}



def gui_main():
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())


def get_dirs() -> tuple[str, str, str]:
    transonic_dir_path = os.path.abspath(os.path.dirname(__file__)) 
    src_dir_path = os.path.abspath(os.path.dirname(transonic_dir_path))
    root_dir_path = os.path.abspath(os.path.dirname(src_dir_path))
    return [transonic_dir_path, src_dir_path, root_dir_path] 


def set_default_paths(start_paths: list[str, str, str]) -> None:
    usr_data_dir_path = os.path.join(start_paths[2], "usr_data")
    wd_default = usr_data_dir_path
    doe_path_default = os.path.join(usr_data_dir_path, "DOEs", "DOE.csv")
    data_path_default = os.path.join(usr_data_dir_path, "raw_data", "C_curves")
    paths.update({"Working Directory": wd_default})
    paths.update({"DOE path": doe_path_default})
    paths.update({"Data directory": data_path_default})


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
    
    #creates the yaml file from user inputs
    try:
        config_dir = os.path.join(paths["Working Directory"], "config")
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        with open(os.path.join((config_dir),"config.yaml"),"w") as yf:
            yf.write(f"model: \'{model}\'\n\ndoe: \'{paths["DOE path"]}\'\n\nwd: \'{paths["Working Directory"]}\'\n\ninput: \'{paths["Data directory"]}\'\n\nparameters:{params}\n\nparameter_bounds: {bounds}")
        print("\nSuccess! Config file generated. Returning to home...")
    except:
        raise Exception
    
    
def edit_paths(): #currently only allows user to enter FULL path for each change. pretty inefficient.
    
    #Program displays paths and prompsts user for change selection
    while True:
        for idx, (name, path) in enumerate(paths.items()):
            print(f"\n{emph1(idx+1)}: {emph2(name)}\n{path}\n{'-'*50}")
            max_idx = idx
        change_op = input(f"\nSelect a path to change by typing its associated number or \'r\' to return.\n> ")
        
    #User responds to prompt with number corresponding to path name or r to return to main
        if change_op == 'r':
            print(f"Exiting edit mode, returning to home...")
            break
        try:
            change_op = int(change_op)
            if change_op < 1 or change_op > max_idx + 1:
                print(f"\n{warn("error")}: Must select a number between 0 and {max_idx+2} or \'r\'.")
                continue
        except ValueError:
            print(f"\n{warn("error")}: Must select a number or \'r\'.")
            continue
            
    
    #User inserts new path and value is changed.
        for idx, (name,path) in enumerate(paths.items()):
            if change_op == idx+1:
                new_path = input(f"\nType the new path for {name}\n> ")
                paths.update({name:new_path})
                if type(new_path) is not str: #doesn't currently work like i think it would
                    print(f"\n{warn("warning")}: user input not path-like.")
                continue
    
    print(f"{warn("heads up!")}Previously made config files are not affected by any path changes just made.")
    

    
def invalid_option():
    print(f"\nNot a valid option. Type \'h\' for help.")



def view():
    for name, path in paths.items():
        print(f"\n{emph1(name)}: {emph2(path)}")
    

def help():
    commands = {
        "new": "Create a new config file through guided prompts.",
        "edit paths": "Edit the working directory, DOE, and data path locations from their default values",
        "run": "Run a case with a config file",
        "clear": "Clear your screen",
        "view paths": "View paths for working directory, DOE directory, and data."
    }
    print(f"\nTRANSONIC currently supports the {emph1("commands")} below.")
    print(f"\n{emph1("Command")}\n{emph2("Description")}\n{'-'*50}")
    for k, v in sorted(commands.items()):
        print(f"{emph1(k)}\n{emph2(v)}")
        print(f"{'-'*50}")

    
def run_case():
    try:
        config_dir = os.path.join(paths["Working Directory"], "config")
        config_path = os.path.join(config_dir, "config.yaml")
        run_from_config(config_path)
        print(f"\nCase completed! Check for the results in\n{emph2(paths['Working Directory'])}{emph2("/results")}\nReturning to home...")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)


def easter_egg():
    print(f"\nPim, her name was Shrimpina. She'd be a shrimp.")


def cli_main():
    commands = {
        "new": make_case,
        "edit paths": edit_paths,
        "run": run_case,
        "help": help,
        "h": help,
        "clear": clear_screen,
        "view paths": view,
        "michaelstyle": easter_egg
    }
    clear_screen()
    banner = banners.get("shifted_box")
    color = banner[0]
    title = banner[1]
    print(f"{in_color(color,title)}\n")

    set_default_paths(get_dirs())
    view()

    print(f"\nTyping \'help\' will bring up the list of commands and \'q\' will quit the program.")
    while True:
        usr_command = input(f"\n> ").strip().lower()
        if usr_command == 'q':
            break
        commands.get(usr_command, invalid_option)()
    
    
    return 0


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
    
if __name__ == '__main__':
    return_code = interface()
    print(f'Return Code: {return_code}')

