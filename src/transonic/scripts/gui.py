import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.uic import loadUi
import os

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

