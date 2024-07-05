import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.uic import loadUi
import os

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
         model = self.model_select.currentText().replace(" ", "_")
         doe_path  = self.doe_path.displayText()
         work_dir = self.work_dir.displayText()
         input_path = self.input_path.displayText()
         if self.default_parameters.isChecked() == True:
             if model == 'LFR_DZ_CSTR':
                 parameters = '\n- \'alpha\'\n- \'beta\''
         if self.default_bounds.isChecked() == True: 
            if model == 'LFR_DZ_CSTR':
                param_bounds = '\n- [0.01, 0.99]\n- [0.01, 0.99]'
            else:
                print(model)

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

