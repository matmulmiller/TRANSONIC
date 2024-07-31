import sys
import os
import pandas as pd

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.uic import loadUi
from src.transonic.modules.utilities import solve, load_config, get_model_class, load_DOE, create_results_folder
from src.transonic.scripts.E_curves import generate_curves

default_params ={
    'LFR_DZ_CSTR': '\n- [0.01, 0.99]\n- [0.01, 0.99]',
    'TANKS_IN_SERIES': '\n- \'n\''
}

default_bounds ={
    'LFR_DZ_CSTR': '\n- [0.01, 0.99]\n- [0.01, 0.99]',
    'TANKS_IN_SERIES': '\n- [1, \'105\']'
}

class ConfigSettings(QWidget):
    def __init__(self):
        super().__init__()
        
        loadUi("./src/transonic/Windows/ConfigSettings.ui", self)
        self.setWindowTitle("Config Settings")

        #Buttons
        self.make_config.clicked.connect(self.create_config_file)
        
        #Actions
        self.cwd_label.setText(f"CWD: {os.getcwd()}")
    
    def create_config_file(self):
        model = self.model_select.currentIndex()
        if model == 0:
            model = 'LFR_DZ_CSTR'
        elif model == 1:
            model = 'TANKS_IN_SERIES'
         
        doe_path  = self.doe_path.displayText()
        work_dir = self.work_dir.displayText()
        input_path = self.input_path.displayText()

        if self.default_parameters.isChecked() == True:
            parameters = default_params[model]
            
        if self.default_bounds.isChecked() == True: 
            param_bounds = default_bounds[model]

        if not os.path.exists("./tmp"):
            tmp_dir = "./tmp"
            os.makedirs(tmp_dir)
        try:
            with open("./tmp/config.yaml","w") as f:
                f.write(f"model: \'{model}\'\n\ndoe: \'{doe_path}\'\n\nwd: \'{work_dir}\'\n\ninput: \'{input_path}\'\n\nparameters:{parameters}\n\nparameter_bounds: {param_bounds}")
        except:
            print("Failure! Something went wrong trying to generate the file")
        print("Success! Config file generated")

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        
        loadUi("./src/transonic/Windows/App.ui", self)
        self.setWindowTitle("TRANSONIC")

        #Buttons
        self.config_button.clicked.connect(self.create_config)
        self.run_button.clicked.connect(self.run_config)
    
    def run_config(self):

        config_path = 'tmp/config.yaml'
        config = load_config(config_path)
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
        summary_df.to_csv(os.path.join(results_folder, 'eval_outputs.csv'))

    def create_config(self):
        print("Creating config file...")
        if not os.path.exists("./tmp"):
            tmp_dir = "./tmp"
            os.makedirs(tmp_dir)

        self.config_settings = ConfigSettings()
        self.config_settings.show()
            

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())

