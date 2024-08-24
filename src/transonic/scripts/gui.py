import sys
import os
import pandas as pd

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QMessageBox
from PyQt5.uic import loadUi
from src.transonic.modules.utilities import solve, load_config, get_model_class, load_DOE, create_results_folder
from src.transonic.scripts.E_curves import generate_curves
from PyQt5.QtCore import pyqtSignal

default_params ={
    'LFR_DZ_CSTR': '\n- [0.01, 0.99]\n- [0.01, 0.99]',
    'TANKS_IN_SERIES': '\n- \'n\''
}

default_bounds ={
    'LFR_DZ_CSTR': '\n- [0.01, 0.99]\n- [0.01, 0.99]',
    'TANKS_IN_SERIES': '\n- [1, \'105\']'
}

class ConfigSettings(QWidget):
    # Define a signal to emit when the configuration is done
    config_updated = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        
        loadUi("./src/transonic/Windows/ConfigSettings.ui", self)
        self.setWindowTitle("Config Settings")

        #Buttons
        self.make_config.clicked.connect(self.create_config_file)
        
        #Actions
        self.cwd_label.setText(f"CWD: {os.getcwd()}")

        #Initialize variables
        self.tmp_dir = ''
    
    def create_config_file(self):
        model = self.model_select.currentIndex()
        if model == 0:
            model = 'LFR_DZ_CSTR'
        elif model == 1:
            model = 'TANKS_IN_SERIES'
         
        self.doe_path  = self.doe_path.displayText()
        self.wd = self.wd.displayText()
        self.input_path = self.input_path.displayText()

        if self.default_parameters.isChecked() == True:
            parameters = default_params[model]
            
        if self.default_bounds.isChecked() == True: 
            param_bounds = default_bounds[model]


        self.tmp_dir = os.path.join(self.wd, 'tmp')
        if not os.path.exists(self.tmp_dir):
            os.makedirs(self.tmp_dir)
        

        try:
            with open(os.path.join((self.tmp_dir),"config.yaml"),"w") as f:
                f.write(f"model: \'{model}\'\n\ndoe: \'{self.doe_path}\'\n\nwd: \'{self.wd}\'\n\ninput: \'{self.input_path}\'\n\nparameters:{parameters}\n\nparameter_bounds: {param_bounds}")
        except:
            pass
        print("Success! Config file generated")
        
        # Emit signal with updated configuration data
        self.config_updated.emit(self.get_path_attributes())
        self.close()        

    def get_path_attributes(self):
        return {
            'config_path':os.path.join(self.tmp_dir, 'config.yaml'),
            'doe_path': self.doe_path,
            'wd': self.wd,
            'input_path': self.input_path,
        }

    def closeEvent(self, event):
        # Handle any additional cleanup if needed
        super().closeEvent(event)



class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        
        loadUi("./src/transonic/Windows/App.ui", self)
        self.setWindowTitle("TRANSONIC")

        #Buttons
        self.config_button.clicked.connect(self.create_config)
        self.run_button.clicked.connect(self.run_config)
    
    def create_config(self):
        print('Creating config file...')
        self.config_settings = ConfigSettings()
        self.config_settings.config_updated.connect(self.handle_config_updated)
        self.config_settings.show()

    def handle_config_updated(self, path_attributes):
        # Process the config data after the window is closed
        self.path_attrs = path_attributes


    def run_config(self):

        config_path = self.path_attrs['config_path']
    
        if os.path.exists(config_path) == False:
            self.warning_label.setText(f"Warning: No file found in the provided path: {config_path}")
        
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
        summary_df.to_csv(os.path.join(results_dir, 'eval_outputs.csv'))
        print(f"Results created! They can be found in {results_dir}/eval_outputs.csv\n")

        




            

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())

